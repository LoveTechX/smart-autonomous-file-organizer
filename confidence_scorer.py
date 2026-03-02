"""
PHASE 4: Confidence Scorer
Assign confidence scores to classification decisions.
Low confidence triggers user confirmation instead of silent automation.
"""

from typing import Optional, Tuple, List
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level categories."""

    VERY_HIGH = 0.95  # >95%  - Fully automated
    HIGH = 0.85  # 85-95% - Automated with logging
    MEDIUM = 0.70  # 70-85% - Requires confirmation
    LOW = 0.50  # 50-70% - Requires user approval
    VERY_LOW = 0.00  # <50%  - Fully manual


class ConfidenceScorer:
    """Score confidence in file classification decisions."""

    # Thresholds
    CONFIDENCE_THRESHOLD_AUTO = 0.80  # >= 80%: Silent automation
    CONFIDENCE_THRESHOLD_CONFIRM = 0.60  # >= 60%: Requires confirmation
    # NOTE: previously a reject threshold existed for very low confidence
    # (<40%) where files would be skipped automatically.  Under the new
    # human-in-the-loop policy we no longer drop any file based solely on
    # confidence; every uncertain decision is surfaced to the user.  The
    # constant is retained here for backwards compatibility with any code or
    # documentation that referenced it, but it is no longer used.
    CONFIDENCE_THRESHOLD_REJECT = 0.40  # < 40%: (deprecated) previously skipped

    @staticmethod
    def score_keyword_match(num_keywords: int, keyword_priority: str = "high") -> float:
        """
        Score confidence for keyword-based rule match.

        Args:
            num_keywords: Number of matching keywords
            keyword_priority: "high" | "medium" | "low"

        Returns:
            Confidence score (0-1)
        """
        priority_weights = {
            "high": 0.95,
            "medium": 0.70,
            "low": 0.45,
        }

        weight = priority_weights.get(keyword_priority, 0.70)

        if num_keywords >= 3:
            return min(0.99, weight + 0.15)
        elif num_keywords == 2:
            return weight
        elif num_keywords == 1:
            return weight * 0.85
        else:
            return 0.0

    @staticmethod
    def score_semantic_match(semantic_confidence: Optional[float]) -> float:
        """
        Score confidence for semantic classifier match.

        Args:
            semantic_confidence: Confidence from semantic model (0-1)

        Returns:
            Adjusted confidence score (0-1)
        """
        if semantic_confidence is None or semantic_confidence < 0:
            return 0.0

        # Semantic scores are already 0-1, use directly with slight dampening
        # to account for model uncertainty
        return semantic_confidence * 0.95

    @staticmethod
    def score_subject_detection(
        subject_confidence: Optional[float], keyword_matches: int = 0
    ) -> float:
        """
        Score confidence for subject detection (nested classification).

        Args:
            subject_confidence: Confidence from subject classifier (0-1)
            keyword_matches: Number of keyword matches for subject

        Returns:
            Confidence score (0-1)
        """
        if subject_confidence is None or subject_confidence < 0:
            base_score = 0.50
        else:
            base_score = subject_confidence * 0.93

        # Boost confidence if keywords support the subject
        if keyword_matches >= 2:
            base_score = min(0.99, base_score + 0.15)
        elif keyword_matches == 1:
            base_score = min(0.99, base_score + 0.08)

        return base_score

    @staticmethod
    def score_extension_rule(extension: str, is_content_mapped: bool = False) -> float:
        """
        Score confidence for extension-based rule match.

        Args:
            extension: File extension
            is_content_mapped: Whether content was analyzed

        Returns:
            Confidence score (0-1)
        """
        # Extension-only rules are less reliable if no content analysis
        if is_content_mapped:
            return 0.75  # Combined rule + semantic = moderate-high
        else:
            return 0.55  # Extension only = moderate

    @staticmethod
    def combine_signals(
        keyword_score: Optional[float] = None,
        semantic_score: Optional[float] = None,
        extension_score: Optional[float] = None,
        subject_score: Optional[float] = None,
    ) -> Tuple[float, str]:
        """
        Combine multiple signals into final confidence score.
        Uses weighted ensemble approach.

        Args:
            keyword_score: Keyword matching confidence
            semantic_score: Semantic model confidence
            extension_score: Extension rule confidence
            subject_score: Subject classification confidence

        Returns:
            (combined_score, reasoning)
        """
        scores = []
        weights = []
        signals = []

        if keyword_score is not None and keyword_score > 0:
            scores.append(keyword_score)
            weights.append(0.35)  # Keywords are strong signals
            signals.append(f"keyword({keyword_score:.2f})")

        if semantic_score is not None and semantic_score > 0:
            scores.append(semantic_score)
            weights.append(0.40)  # Semantics are the strongest
            signals.append(f"semantic({semantic_score:.2f})")

        if extension_score is not None and extension_score > 0:
            scores.append(extension_score)
            weights.append(0.15)  # Extension is supporting signal
            signals.append(f"extension({extension_score:.2f})")

        if subject_score is not None and subject_score > 0:
            scores.append(subject_score)
            weights.append(0.10)  # Subject augments primary category
            signals.append(f"subject({subject_score:.2f})")

        if not scores:
            return 0.0, "No confidence signals available"

        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        # Weighted average
        combined = sum(s * w for s, w in zip(scores, normalized_weights))

        reasoning = f"Combined [{', '.join(signals)}]"

        return combined, reasoning

    @staticmethod
    def get_action_for_confidence(confidence: float) -> Tuple[str, str]:
        """
        Determine action based on confidence score.

        Args:
            confidence: Score 0-1

        Returns:
            (action, description)
            action: "auto" | "preview" | "preview_warn"

        The routing policy was revised to eliminate any automatic skipping of
        files due to low confidence.  Instead, uncertain cases are handled via
        the preview subsystem where a human operator can make the final call.

        Routing rules:
        * >= AUTO threshold: highest confidence → automatic move ("auto")
        * >= CONFIRM threshold: medium confidence → preview ("preview")
        * < CONFIRM threshold: low confidence → preview with stronger warning
          ("preview_warn").

        The return value is a tuple ``(action, description)`` where ``action``
        is one of ``"auto"``, ``"preview"`` or ``"preview_warn"``.  This
        intentionally replaces the old ``"skip"``/``"reject"`` actions to
        maintain backward compatibility while changing the behavior.
        """

        # NOTE: the deprecated CONFIDENCE_THRESHOLD_REJECT constant exists only
        # for backward compatibility and is not consulted here.
        if confidence >= ConfidenceScorer.CONFIDENCE_THRESHOLD_AUTO:
            return "auto", "High confidence - move automatically"
        elif confidence >= ConfidenceScorer.CONFIDENCE_THRESHOLD_CONFIRM:
            return "preview", "Medium confidence - show preview for user review"
        else:
            return (
                "preview_warn",
                "Low confidence - show preview with strong warning (user review required)",
            )

    @staticmethod
    def print_confidence_report(
        file_name: str,
        confidence: float,
        signals: Optional[List[str]] = None,
        recommendation: Optional[str] = None,
    ) -> None:
        """Pretty-print a confidence report."""
        confidence_pct = confidence * 100

        # Get level
        if confidence >= 0.95:
            level = "VERY HIGH"
            icon = "🟢"
        elif confidence >= 0.85:
            level = "HIGH"
            icon = "🟢"
        elif confidence >= 0.70:
            level = "MEDIUM"
            icon = "🟡"
        elif confidence >= 0.50:
            level = "LOW"
            icon = "🟠"
        else:
            level = "VERY LOW"
            icon = "🔴"

        # Confidence bar
        bar = "█" * int(confidence_pct / 10) + "░" * (10 - int(confidence_pct / 10))

        print(f"\n{icon} Confidence Report: {file_name}")
        print(f"   Score:  [{bar}] {confidence_pct:.0f}% ({level})")

        if signals:
            print(f"   Signals: {', '.join(signals)}")

        if recommendation:
            print(f"   Action:  {recommendation}")

        print()


# Global scorer instance
confidence_scorer = ConfidenceScorer()
