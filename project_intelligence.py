import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


PROJECT_DB_PATH = Path("D:/AUTOMATION/projects.json")
CACHE_DB_PATH = Path("D:/AUTOMATION/projects_cache.json")

STATIC_SCAN_ROOTS = [
    Path("D:/Projects"),
    Path("D:/02_PROGRAMMING"),
]

IGNORE_DIRS = {
    ".git",
    ".dart_tool",
    ".idea",
    ".vscode",
    "node_modules",
    "build",
    "dist",
    "__pycache__",
    ".venv",
    "venv",
    "target",
    "out",
    "bin",
    "obj",
}

PROJECT_MARKERS = {
    "flutter": {"pubspec.yaml", "lib"},
    "android": {"build.gradle", "settings.gradle"},
    "web": {"package.json"},
    "python": {"requirements.txt", "setup.py"},
    "cpp": {"CMakeLists.txt"},
}


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _normalize_path(path_obj):
    return str(path_obj.resolve()).replace("\\", "/")


def _load_json(path_obj, default_value):
    if not path_obj.exists():
        return default_value
    try:
        with path_obj.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_value


def _save_json(path_obj, data):
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with path_obj.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _user_roots():
    home = Path.home()
    roots = [home / "Desktop", home / "Documents"]
    return [path for path in roots if path.exists()]


def _scan_roots():
    roots = []
    for root in STATIC_SCAN_ROOTS + _user_roots():
        if root.exists():
            roots.append(root)
    dedup = []
    seen = set()
    for root in roots:
        key = _normalize_path(root)
        if key in seen:
            continue
        seen.add(key)
        dedup.append(root)
    return dedup


def _safe_stat(path_obj):
    try:
        return path_obj.stat()
    except Exception:
        return None


def _project_type_from_entries(entry_names):
    project_types = []

    if "pubspec.yaml" in entry_names and "lib" in entry_names:
        project_types.append("flutter")
    if "build.gradle" in entry_names or "settings.gradle" in entry_names:
        project_types.append("android")
    if "package.json" in entry_names:
        project_types.append("web")
    if "requirements.txt" in entry_names or "setup.py" in entry_names:
        project_types.append("python")
    if "CMakeLists.txt" in entry_names:
        project_types.append("cpp")
    if ".git" in entry_names:
        project_types.append("git")

    return sorted(set(project_types))


def _signature_for_directory(root_path, entry_names):
    dir_stat = _safe_stat(root_path)
    if not dir_stat:
        return ""

    marker_parts = []
    interesting_entries = set(entry_names).intersection(
        {
            "pubspec.yaml",
            "lib",
            "build.gradle",
            "settings.gradle",
            "package.json",
            "requirements.txt",
            "setup.py",
            "CMakeLists.txt",
            ".git",
        }
    )

    for entry in sorted(interesting_entries):
        entry_path = root_path / entry
        st = _safe_stat(entry_path)
        if not st:
            marker_parts.append(f"{entry}:missing")
            continue
        marker_parts.append(f"{entry}:{int(st.st_mtime)}:{int(st.st_size)}")

    return f"{int(dir_stat.st_mtime)}|{';'.join(marker_parts)}"


def _git_signature(project_root):
    git_dir = project_root / ".git"
    if not git_dir.exists():
        return ""
    head_stat = _safe_stat(git_dir / "HEAD")
    index_stat = _safe_stat(git_dir / "index")
    return (
        f"head:{int(head_stat.st_mtime) if head_stat else 0}:"
        f"{int(head_stat.st_size) if head_stat else 0}|"
        f"index:{int(index_stat.st_mtime) if index_stat else 0}:"
        f"{int(index_stat.st_size) if index_stat else 0}"
    )


def _get_git_status(project_root, cached_project=None):
    if not (project_root / ".git").exists():
        return {"is_git_repo": False, "branch": None, "dirty": None}

    git_sig = _git_signature(project_root)
    if cached_project and cached_project.get("git_signature") == git_sig:
        return {
            "is_git_repo": True,
            "branch": cached_project.get("branch"),
            "dirty": cached_project.get("dirty"),
            "git_signature": git_sig,
        }

    try:
        cmd = ["git", "-C", str(project_root), "status", "--porcelain", "--branch"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2, check=False)
        lines = (proc.stdout or "").splitlines()
        branch = None
        dirty = False
        if lines:
            head = lines[0].strip()
            if head.startswith("##"):
                branch = head[2:].strip()
        for line in lines[1:]:
            if line.strip():
                dirty = True
                break
        return {
            "is_git_repo": True,
            "branch": branch,
            "dirty": dirty,
            "git_signature": git_sig,
        }
    except Exception:
        return {
            "is_git_repo": True,
            "branch": None,
            "dirty": None,
            "git_signature": git_sig,
        }


def _project_record(project_root, project_types, cached_project=None):
    root_stat = _safe_stat(project_root)
    modified_at = datetime.fromtimestamp(root_stat.st_mtime).isoformat(timespec="seconds")
    git_data = _get_git_status(project_root, cached_project=cached_project)

    marker_map = {}
    entries = set(os.listdir(project_root))
    for ptype, markers in PROJECT_MARKERS.items():
        matched = sorted(marker for marker in markers if marker in entries)
        if matched:
            marker_map[ptype] = matched

    return {
        "project_name": project_root.name,
        "type": project_types,
        "root_folder": _normalize_path(project_root),
        "last_modified_time": modified_at,
        "git_repo_status": {
            "is_git_repo": git_data.get("is_git_repo", False),
            "branch": git_data.get("branch"),
            "dirty": git_data.get("dirty"),
        },
        "detected_markers": marker_map,
        # Reserved for future semantic-memory enrichment.
        "semantic_topics": [],
        "git_signature": git_data.get("git_signature", ""),
    }


def _load_cache():
    data = _load_json(CACHE_DB_PATH, {"entries": {}, "last_scan_at": None})
    if not isinstance(data, dict):
        return {"entries": {}, "last_scan_at": None}
    entries = data.get("entries", {})
    if not isinstance(entries, dict):
        entries = {}
    return {"entries": entries, "last_scan_at": data.get("last_scan_at")}


def _save_cache(cache):
    _save_json(CACHE_DB_PATH, cache)


def _scan_with_cache(cache):
    projects = []
    new_cache_entries = {}
    known_entries = cache.get("entries", {})

    for root in _scan_roots():
        for current_root, dir_names, file_names in os.walk(root):
            current_path = Path(current_root)
            dir_names[:] = [d for d in dir_names if d not in IGNORE_DIRS]

            entry_names = set(file_names).union(set(dir_names))
            project_types = _project_type_from_entries(entry_names)
            if not project_types:
                continue

            root_key = _normalize_path(current_path)
            signature = _signature_for_directory(current_path, entry_names)
            cached = known_entries.get(root_key)

            if cached and cached.get("signature") == signature and cached.get("project"):
                project = cached["project"]
            else:
                old_project = cached.get("project") if cached else None
                project = _project_record(
                    current_path,
                    project_types=project_types,
                    cached_project=old_project,
                )

            new_cache_entries[root_key] = {"signature": signature, "project": project}
            projects.append(project)

            # Once a root project is detected, skip nested traversal for speed.
            dir_names[:] = []

    return projects, new_cache_entries


def _strip_internal_fields(project):
    clean = dict(project)
    clean.pop("git_signature", None)
    return clean


def scan_projects():
    cache = _load_cache()
    projects, new_cache_entries = _scan_with_cache(cache)

    unique = {}
    for project in projects:
        unique[project["root_folder"]] = project
    final_projects = sorted(
        [_strip_internal_fields(p) for p in unique.values()],
        key=lambda item: item["last_modified_time"],
        reverse=True,
    )

    db_data = {
        "updated_at": _now_iso(),
        "scan_roots": [_normalize_path(p) for p in _scan_roots()],
        "total_projects": len(final_projects),
        "projects": final_projects,
    }
    _save_json(PROJECT_DB_PATH, db_data)

    cache_data = {
        "last_scan_at": _now_iso(),
        "entries": new_cache_entries,
    }
    _save_cache(cache_data)

    return final_projects


def get_projects():
    data = _load_json(PROJECT_DB_PATH, {})
    if not isinstance(data, dict):
        return []
    projects = data.get("projects", [])
    return projects if isinstance(projects, list) else []


def search_projects(query):
    if not query:
        return get_projects()

    q = query.strip().lower()
    results = []
    for project in get_projects():
        name = str(project.get("project_name", "")).lower()
        types = " ".join(project.get("type", [])).lower()
        root = str(project.get("root_folder", "")).lower()
        branch = str(project.get("git_repo_status", {}).get("branch", "") or "").lower()
        markers = " ".join(
            marker
            for markers in project.get("detected_markers", {}).values()
            for marker in markers
        ).lower()

        haystack = f"{name} {types} {root} {branch} {markers}"
        if q in haystack:
            results.append(project)

    return results
