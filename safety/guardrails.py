"""
PHASE 6: Safety Guardrails
Protect critical files and system integrity.
Never move hidden files, system files, or project structures.
"""

import os
from typing import Tuple, List


class SafetyGuardrails:
    """Safety checks to protect important files and project structure."""

    # System and hidden patterns
    HIDDEN_PATTERNS = {
        ".git",
        ".github",
        ".env",
        ".vscode",
        ".idea",
        ".DS_Store",
        ".gitignore",
        ".gitkeep",
        ".config",
        ".cache",
        ".pytest_cache",
        "__pycache__",
        ".mypy_cache",
    }

    # Critical project structure files
    CRITICAL_PROJECT_FILES = {
        "package.json",
        "package-lock.json",
        "setup.py",
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
        "Gemfile",
        "pom.xml",
        "build.gradle",
        "settings.gradle",
        "docker-compose.yml",
        "docker-compose.yaml",
        "Dockerfile",
        "Makefile",
        "CMakeLists.txt",
        "tox.ini",
        "pytest.ini",
        ".editorconfig",
    }

    # Build and cache directories
    BUILD_DIRECTORIES = {
        "build",
        "dist",
        "target",
        ".gradle",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        ".dart_tool",
        "android",
        "ios",
        "windows",
        "linux",
        "macos",
        "web",
        ".next",
        "out",
        "bin",
        "obj",
    }

    # System file extensions
    SYSTEM_EXTENSIONS = {
        "exe",
        "dll",
        "sys",
        "msi",
        "app",
        "dmg",
        "deb",
        "rpm",
        "apk",
    }

    @staticmethod
    def is_hidden_file(file_name: str) -> bool:
        """
        Check if file is hidden (starts with .)

        Args:
            file_name: Name of the file

        Returns:
            True if file is hidden
        """
        return file_name.startswith(".")

    @staticmethod
    def is_in_hidden_directory(file_path: str) -> bool:
        """
        Check if file is in a hidden directory.

        Args:
            file_path: Full path to file

        Returns:
            True if file is in hidden directory
        """
        path_parts = file_path.replace("\\", "/").split("/")

        for part in path_parts:
            if part.startswith("."):
                return True

        return False

    @staticmethod
    def is_critical_project_file(file_name: str) -> bool:
        """
        Check if file is critical for project configuration.

        Args:
            file_name: Name of the file

        Returns:
            True if file is critical
        """
        return file_name.lower() in SafetyGuardrails.CRITICAL_PROJECT_FILES

    @staticmethod
    def is_in_build_directory(file_path: str) -> bool:
        """
        Check if file is in a build/cache directory.

        Args:
            file_path: Full path to file

        Returns:
            True if file is in build directory
        """
        path_parts = file_path.replace("\\", "/").lower().split("/")

        for part in path_parts:
            if part in SafetyGuardrails.BUILD_DIRECTORIES:
                return True

        return False

    @staticmethod
    def is_system_executable(file_name: str) -> bool:
        """
        Check if file is a system executable.

        Args:
            file_name: Name of the file

        Returns:
            True if file is system executable
        """
        _, ext = os.path.splitext(file_name)
        ext = ext.lower().lstrip(".")
        return ext in SafetyGuardrails.SYSTEM_EXTENSIONS

    @staticmethod
    def is_lock_file(file_name: str) -> bool:
        """
        Check if file is a lock file (package manager, etc).

        Args:
            file_name: Name of the file

        Returns:
            True if file is a lock file
        """
        lock_names = {
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "Pipfile.lock",
            "poetry.lock",
            "Gemfile.lock",
            "composer.lock",
            "go.lock",
            ".gradle.lock",
        }
        return file_name.lower() in lock_names

    @staticmethod
    def check_safety(file_path: str) -> Tuple[bool, List[str]]:
        """
        Perform comprehensive safety checks on a file.

        Args:
            file_path: Full path to file

        Returns:
            (is_safe, list_of_violations)
            is_safe: True if file passes all safety checks
            violations: List of safety violations found
        """
        file_name = os.path.basename(file_path)
        violations = []

        # Check 1: Hidden files
        if SafetyGuardrails.is_hidden_file(file_name):
            violations.append("File is hidden (starts with '.')")

        # Check 2: Hidden directory
        if SafetyGuardrails.is_in_hidden_directory(file_path):
            violations.append("File is in hidden directory (e.g., .git, .vscode)")

        # Check 3: Critical project files
        if SafetyGuardrails.is_critical_project_file(file_name):
            violations.append("File is critical for project configuration")

        # Check 4: Build/cache directories
        if SafetyGuardrails.is_in_build_directory(file_path):
            violations.append("File is in build/cache directory")

        # Check 5: System executables
        if SafetyGuardrails.is_system_executable(file_name):
            violations.append("File is a system executable")

        # Check 6: Lock files
        if SafetyGuardrails.is_lock_file(file_name):
            violations.append("File is a package manager lock file")

        is_safe = len(violations) == 0

        return is_safe, violations

    @staticmethod
    def get_safety_report(file_path: str) -> str:
        """
        Generate a detailed safety report for a file.

        Args:
            file_path: Full path to file

        Returns:
            Formatted report string
        """
        file_name = os.path.basename(file_path)
        is_safe, violations = SafetyGuardrails.check_safety(file_path)

        report_lines = []
        report_lines.append(f"\n🛡️  Safety Check: {file_name}")
        report_lines.append("=" * 60)

        if is_safe:
            report_lines.append("✓ SAFE - File passed all safety checks")
        else:
            report_lines.append("✗ UNSAFE - File failed safety checks:")
            for violation in violations:
                report_lines.append(f"  • {violation}")

        report_lines.append("=" * 60 + "\n")

        return "\n".join(report_lines)

    @staticmethod
    def print_safety_check(file_path: str, verbose: bool = False) -> bool:
        """
        Perform and print safety check for a file.

        Args:
            file_path: Full path to file
            verbose: Print detailed report

        Returns:
            True if file is safe, False otherwise
        """
        is_safe, violations = SafetyGuardrails.check_safety(file_path)

        if verbose:
            print(SafetyGuardrails.get_safety_report(file_path))
        else:
            file_name = os.path.basename(file_path)
            if not is_safe:
                print(f"🛡️  {file_name}: BLOCKED - {violations[0]}")

        return is_safe


# Global guardrails instance
safety_guardrails = SafetyGuardrails()
