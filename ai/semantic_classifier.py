from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ===== MODEL =====
_MODEL_NAME = "all-mpnet-base-v2"
model = None
_category_embeddings = None

# ===== CATEGORIES =====
categories = {
    "COLLEGE": "university, academic subjects, operating systems, computer networks, dbms, daa, assignments, lab manuals, semester, exam, theory",
    "PROGRAMMING": "coding, software development, programming languages, python, c, cpp, java, scripts, system design",
    "PROJECTS": "personal projects, flutter apps, web apps, mobile apps, development projects",
    "CAREER": "resume, job, internship, placement, interview, offer letter, certificate",
    "REFERENCE": "ebooks, documentation, manuals, research papers",
}

category_names = list(categories.keys())


def get_model():
    """Lazily load the transformer model only when classification is needed."""
    global model
    if model is None:
        model = SentenceTransformer(_MODEL_NAME)
    return model


def get_category_embeddings():
    """Cache category embeddings after the first model load."""
    global _category_embeddings
    if _category_embeddings is None:
        _category_embeddings = get_model().encode(list(categories.values()))
    return _category_embeddings


# ===== CLASSIFICATION =====
def classify_document(text_chunks, file_name=""):

    text = " ".join(text_chunks[:5]).lower()
    file_name = file_name.lower()

    # ===== STRONG KEYWORD SIGNALS =====
    if any(word in text or word in file_name for word in ["assignment", "lab", "semester", "exam"]):
        return "COLLEGE"

    if any(word in text or word in file_name for word in ["resume", "cv", "offer", "certificate"]):
        return "CAREER"

    if any(word in text or word in file_name for word in ["flutter", "react", "project", "app"]):
        return "PROJECTS"

    # ===== PERSONAL STUDY PATTERN =====
    if any(word in text or word in file_name for word in ["day", "task", "plan", "notes"]):
        return "COLLEGE"

    # ===== ACADEMIC PROGRAMMING DETECTION =====
    has_academic_file_signal = any(word in file_name for word in ["task", "lab", "experiment"])
    has_programming_text_signal = any(
        word in text for word in ["c++", "java", "python", "fstream", "program"]
    )
    if has_academic_file_signal and has_programming_text_signal:
        return "COLLEGE"

    # ===== SUBJECT DETECTION =====
    if any(
        word in text
        for word in ["operating system", "cpu scheduling", "process", "deadlock"]
    ):
        return "COLLEGE"

    if any(word in text for word in ["dbms", "sql", "database"]):
        return "COLLEGE"

    if any(word in text for word in ["computer networks", "tcp", "ip"]):
        return "COLLEGE"
    


    # ===== SEMANTIC FALLBACK =====
    semantic_input = f"{text} {file_name}".strip()
    doc_embedding = get_model().encode([semantic_input])

    similarities = cosine_similarity(doc_embedding, get_category_embeddings())[0]

    best_index = np.argmax(similarities)

    return category_names[best_index]
