import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from project_intelligence import get_projects, scan_projects


HEALTH_REPORT_PATH = Path("D:/AUTOMATION/project_health_report.json")
HEALTH_CACHE_PATH = Path("D:/AUTOMATION/project_health_cache.json")
REPAIR_LOG_PATH = Path("D:/AUTOMATION/project_repair_log.json")
BACKUP_DIR = Path("D:/AUTOMATION/project_backups")
ENGINE_VERSION = "1.0"


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


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


def _run_command(cmd, cwd=None, timeout=10):
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    except FileNotFoundError:
        return {"ok": False, "code": 127, "stdout": "", "stderr": "Command not found"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": 124, "stdout": "", "stderr": "Command timed out"}
    except Exception as e:
        return {"ok": False, "code": 1, "stdout": "", "stderr": str(e)}


def _confirm(message):
    answer = input(f"{message} (Y/N): ").strip().lower()
    return answer in {"y", "yes"}


def _backup_project(project_name, project_root):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = BACKUP_DIR / f"{project_name}_{stamp}"
    archive_path = shutil.make_archive(str(base_name), "zip", root_dir=project_root)
    return archive_path


def _restore_from_backup(project_root, backup_zip):
    if not os.path.exists(backup_zip):
        return False, "Backup archive not found."

    root = Path(project_root)
    if not root.exists():
        return False, "Project root not found."

    temp_failed = root.with_name(f"{root.name}_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    try:
        root.rename(temp_failed)
    except Exception as e:
        return False, f"Could not move current project for rollback: {e}"

    try:
        shutil.unpack_archive(backup_zip, root.parent)
    except Exception as e:
        try:
            if root.exists():
                shutil.rmtree(root)
            temp_failed.rename(root)
        except Exception:
            pass
        return False, f"Rollback extraction failed: {e}"

    return True, f"Rollback restored from {backup_zip}"


def _append_repair_log(entry):
    data = _load_json(REPAIR_LOG_PATH, {"repairs": []})
    repairs = data.get("repairs", []) if isinstance(data, dict) else []
    if not isinstance(repairs, list):
        repairs = []
    repairs.append(entry)
    _save_json(REPAIR_LOG_PATH, {"updated_at": _now_iso(), "repairs": repairs})


def _clear_cached_health(root_folder):
    cache = _load_json(HEALTH_CACHE_PATH, {"entries": {}})
    entries = cache.get("entries", {}) if isinstance(cache, dict) else {}
    if isinstance(entries, dict) and root_folder in entries:
        del entries[root_folder]
        cache["entries"] = entries
        cache["updated_at"] = _now_iso()
        _save_json(HEALTH_CACHE_PATH, cache)


def _compute_signature(project_root):
    root = Path(project_root)
    if not root.exists():
        return "missing"

    markers = [
        "pubspec.yaml",
        "pubspec.lock",
        ".dart_tool/package_config.json",
        "android/build.gradle",
        "android/settings.gradle",
        "android/settings.gradle.kts",
        "android/gradle/wrapper/gradle-wrapper.properties",
        "build.gradle",
        "settings.gradle",
        "settings.gradle.kts",
        "package.json",
        "requirements.txt",
        "setup.py",
        "pyproject.toml",
        "CMakeLists.txt",
        ".git/HEAD",
        ".git/index",
    ]

    parts = []
    try:
        root_stat = root.stat()
        parts.append(f"root:{int(root_stat.st_mtime)}:{int(root_stat.st_size)}")
    except Exception:
        parts.append("root:na")

    for marker in markers:
        p = root / marker
        if not p.exists():
            continue
        try:
            st = p.stat()
            parts.append(f"{marker}:{int(st.st_mtime)}:{int(st.st_size)}")
        except Exception:
            parts.append(f"{marker}:na")

    parts.append(f"engine:{ENGINE_VERSION}")
    return "|".join(parts)


def _status_from_issues(issues):
    broken = any(issue.get("severity") == "broken" for issue in issues)
    warning = any(issue.get("severity") == "warning" for issue in issues)
    if broken:
        return "broken"
    if warning:
        return "warning"
    return "healthy"


def _add_issue(issues, suggestions, severity, message, suggestion=None):
    issues.append({"severity": severity, "message": message})
    if suggestion:
        suggestions.append(suggestion)


def _parse_flutter_version(output):
    lines = output.splitlines()
    if not lines:
        return None
    m = re.search(r"Flutter\s+([0-9]+\.[0-9]+\.[0-9]+)", lines[0])
    if m:
        return m.group(1)
    return lines[0].strip() or None


def _read_text(path_obj):
    try:
        return path_obj.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _extract_pubspec_dependencies(pubspec_text):
    deps = set()
    in_deps_block = False
    for line in pubspec_text.splitlines():
        stripped = line.rstrip()
        if not stripped or stripped.lstrip().startswith("#"):
            continue
        if re.match(r"^(dependencies|dev_dependencies)\s*:\s*$", stripped):
            in_deps_block = True
            continue
        if re.match(r"^[A-Za-z0-9_]+\s*:\s*$", stripped):
            in_deps_block = False
        if in_deps_block:
            m = re.match(r"^\s{2,}([A-Za-z0-9_]+)\s*:", line)
            if m:
                name = m.group(1)
                if name != "flutter":
                    deps.add(name)
    return deps


def _extract_package_config_names(package_config_text):
    names = set(re.findall(r'"name"\s*:\s*"([A-Za-z0-9_]+)"', package_config_text))
    return names


def _diagnose_flutter(project_root, report):
    root = Path(project_root)
    issues = report["issues"]
    suggestions = report["suggestions"]

    flutter_cmd = _run_command(["flutter", "--version"], timeout=8)
    if not flutter_cmd["ok"]:
        _add_issue(
            issues,
            suggestions,
            "broken",
            "Flutter SDK is not installed or not available in PATH.",
            "Install Flutter and ensure `flutter` is available from terminal PATH.",
        )
        return

    report["flutter_version"] = _parse_flutter_version(flutter_cmd["stdout"])

    pubspec = root / "pubspec.yaml"
    lib_dir = root / "lib"
    if not pubspec.exists() or not lib_dir.exists():
        _add_issue(
            issues,
            suggestions,
            "broken",
            "Flutter project structure is invalid (missing pubspec.yaml or lib/).",
            "Ensure project root contains both `pubspec.yaml` and `lib/`.",
        )
        return

    pubspec_text = _read_text(pubspec)
    if "name:" not in pubspec_text:
        _add_issue(
            issues,
            suggestions,
            "warning",
            "pubspec.yaml may be malformed (missing `name:`).",
            "Validate `pubspec.yaml` format and required fields.",
        )

    required_deps = _extract_pubspec_dependencies(pubspec_text)
    pkg_cfg_path = root / ".dart_tool" / "package_config.json"
    if not pkg_cfg_path.exists():
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Dependency resolution file missing (.dart_tool/package_config.json).",
            "Run `flutter pub get` in the project root.",
        )
    else:
        installed_deps = _extract_package_config_names(_read_text(pkg_cfg_path))
        missing = sorted(dep for dep in required_deps if dep not in installed_deps)
        if missing:
            _add_issue(
                issues,
                suggestions,
                "warning",
                f"Potential missing dependencies: {', '.join(missing[:10])}",
                "Run `flutter pub get` and re-check dependency resolution.",
            )

    main_dart = root / "lib" / "main.dart"
    if not main_dart.exists():
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Build entrypoint not found at lib/main.dart.",
            "Ensure a valid app entrypoint exists at `lib/main.dart`.",
        )

    build_probe = _run_command(
        ["flutter", "build", "apk", "--debug", "--no-pub"],
        cwd=str(root),
        timeout=240,
    )
    if not build_probe["ok"]:
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Flutter build check failed.",
            "Run `flutter doctor`, then `flutter pub get`, then `flutter build apk --debug`.",
        )


def _detect_gradle_version(project_root):
    root = Path(project_root)
    wrapper_bat = root / "gradlew.bat"
    wrapper_sh = root / "gradlew"

    if wrapper_bat.exists():
        return _run_command([str(wrapper_bat), "--version"], cwd=str(root), timeout=10)
    if wrapper_sh.exists():
        return _run_command([str(wrapper_sh), "--version"], cwd=str(root), timeout=10)
    return _run_command(["gradle", "--version"], cwd=str(root), timeout=10)


def _extract_gradle_version(output):
    m = re.search(r"Gradle\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)", output)
    return m.group(1) if m else None


def _diagnose_android(project_root, report):
    root = Path(project_root)
    issues = report["issues"]
    suggestions = report["suggestions"]

    gradle_check = _detect_gradle_version(project_root)
    if gradle_check["ok"]:
        report["gradle_version"] = _extract_gradle_version(
            f"{gradle_check['stdout']}\n{gradle_check['stderr']}"
        )
    else:
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Gradle is not available (wrapper/global) or failed to execute.",
            "Add Gradle wrapper (`gradlew`) to project or install Gradle globally.",
        )

    java_check = _run_command(["java", "-version"], timeout=8)
    if not java_check["ok"]:
        _add_issue(
            issues,
            suggestions,
            "broken",
            "Java is not installed or not configured in PATH.",
            "Install JDK (recommended 17 for modern Android builds) and set JAVA_HOME.",
        )

    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not android_home:
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Android SDK path environment variable is not set.",
            "Set ANDROID_HOME or ANDROID_SDK_ROOT to your Android SDK path.",
        )

    structure_candidates = [
        root / "app" / "src" / "main" / "AndroidManifest.xml",
        root / "android" / "app" / "src" / "main" / "AndroidManifest.xml",
    ]
    if not any(p.exists() for p in structure_candidates):
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Android project structure seems incomplete (AndroidManifest.xml missing).",
            "Verify `app/src/main/AndroidManifest.xml` exists.",
        )

    gradle_files = [
        root / "build.gradle",
        root / "settings.gradle",
        root / "settings.gradle.kts",
        root / "android" / "build.gradle",
        root / "android" / "settings.gradle",
        root / "android" / "settings.gradle.kts",
    ]
    if not any(p.exists() for p in gradle_files):
        _add_issue(
            issues,
            suggestions,
            "broken",
            "Gradle project files are missing.",
            "Ensure Gradle files like `build.gradle` and `settings.gradle` exist.",
        )


def _diagnose_web(project_root, report):
    root = Path(project_root)
    issues = report["issues"]
    suggestions = report["suggestions"]

    pkg = root / "package.json"
    if not pkg.exists():
        _add_issue(
            issues,
            suggestions,
            "broken",
            "Web project marker found but package.json is missing.",
            "Ensure `package.json` exists in project root.",
        )
        return

    node_check = _run_command(["node", "--version"], timeout=6)
    npm_check = _run_command(["npm", "--version"], timeout=6)
    if not node_check["ok"] or not npm_check["ok"]:
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Node.js or npm is unavailable.",
            "Install Node.js LTS and ensure both `node` and `npm` are in PATH.",
        )

    node_modules = root / "node_modules"
    if not node_modules.exists():
        _add_issue(
            issues,
            suggestions,
            "warning",
            "node_modules is missing.",
            "Run `npm install` to restore dependencies.",
        )


def _diagnose_python(project_root, report):
    root = Path(project_root)
    issues = report["issues"]
    suggestions = report["suggestions"]

    py_check = _run_command(["python", "--version"], timeout=6)
    if not py_check["ok"]:
        _add_issue(
            issues,
            suggestions,
            "broken",
            "Python is not available in PATH.",
            "Install Python 3 and ensure `python` command works in terminal.",
        )

    if not any((root / p).exists() for p in ["requirements.txt", "setup.py", "pyproject.toml"]):
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Python dependency/project metadata file is missing.",
            "Add `requirements.txt`, `setup.py`, or `pyproject.toml`.",
        )

    if not any((root / p).exists() for p in [".venv", "venv"]):
        _add_issue(
            issues,
            suggestions,
            "warning",
            "Virtual environment folder not found.",
            "Create a virtual environment (`python -m venv .venv`).",
        )


def _get_project_by_name(project_name):
    projects = get_projects()
    if not projects:
        projects = scan_projects()

    target = project_name.strip().lower()
    for project in projects:
        if str(project.get("project_name", "")).strip().lower() == target:
            return project

    for project in projects:
        root_name = os.path.basename(str(project.get("root_folder", ""))).strip().lower()
        if root_name == target:
            return project

    return None


def diagnose_project(project_name):
    project = _get_project_by_name(project_name)
    if not project:
        return {
            "status": "broken",
            "issues": [{"severity": "broken", "message": f"Project not found: {project_name}"}],
            "suggestions": ["Run project scan first and verify project name."],
        }

    root = project.get("root_folder")
    project_types = [t.lower() for t in project.get("type", [])]
    signature = _compute_signature(root)

    cache = _load_json(HEALTH_CACHE_PATH, {"entries": {}})
    entries = cache.get("entries", {}) if isinstance(cache, dict) else {}
    cached = entries.get(root) if isinstance(entries, dict) else None
    if cached and cached.get("signature") == signature and cached.get("report"):
        return cached["report"]

    report = {
        "status": "healthy",
        "issues": [],
        "suggestions": [],
        "project_name": project.get("project_name"),
        "project_types": project_types,
        "root_folder": root,
        "checked_at": _now_iso(),
    }

    if "flutter" in project_types:
        _diagnose_flutter(root, report)
    if "android" in project_types:
        _diagnose_android(root, report)
    if "web" in project_types:
        _diagnose_web(root, report)
    if "python" in project_types:
        _diagnose_python(root, report)

    report["status"] = _status_from_issues(report["issues"])
    report["suggestions"] = list(dict.fromkeys(report["suggestions"]))

    if not isinstance(entries, dict):
        entries = {}
    entries[root] = {"signature": signature, "report": report}
    cache = {"updated_at": _now_iso(), "entries": entries}
    _save_json(HEALTH_CACHE_PATH, cache)

    full_report = _load_json(HEALTH_REPORT_PATH, {"updated_at": None, "reports": {}})
    all_reports = full_report.get("reports", {}) if isinstance(full_report, dict) else {}
    if not isinstance(all_reports, dict):
        all_reports = {}
    all_reports[project.get("project_name")] = report
    _save_json(HEALTH_REPORT_PATH, {"updated_at": _now_iso(), "reports": all_reports})

    return report


def get_health_report():
    data = _load_json(HEALTH_REPORT_PATH, {"updated_at": None, "reports": {}})
    if not isinstance(data, dict):
        data = {"updated_at": None, "reports": {}}
    reports = data.get("reports")
    if not isinstance(reports, dict):
        data["reports"] = {}
    return data
