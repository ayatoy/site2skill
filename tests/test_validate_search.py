import importlib.util
import shutil
from pathlib import Path

from site2skill.validate_skill import validate_skill


def _write_markdown(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        (
            "---\n"
            f'title: "{title}"\n'
            'source_url: "https://example.com"\n'
            'fetched_at: "2026-01-01T00:00:00+00:00"\n'
            "---\n\n"
            f"{body}\n"
        ),
        encoding="utf-8",
    )


def _load_search_module():
    script_path = Path(__file__).resolve().parents[1] / "site2skill" / "templates" / "search_docs.py"
    spec = importlib.util.spec_from_file_location("search_docs_template", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_validate_accepts_references_and_legacy_docs(tmp_path):
    skill_refs = tmp_path / "skill-refs"
    skill_refs.mkdir(parents=True, exist_ok=True)
    (skill_refs / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")
    _write_markdown(skill_refs / "references" / "index.md", "Refs", "hello references")
    assert validate_skill(str(skill_refs))

    skill_docs = tmp_path / "skill-docs"
    skill_docs.mkdir(parents=True, exist_ok=True)
    (skill_docs / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")
    _write_markdown(skill_docs / "docs" / "index.md", "Docs", "hello docs")
    assert validate_skill(str(skill_docs))


def test_search_prefers_references_then_falls_back_to_docs(tmp_path):
    module = _load_search_module()
    skill_dir = tmp_path / "skill"
    (skill_dir / "SKILL.md").parent.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")

    _write_markdown(skill_dir / "docs" / "legacy.md", "Legacy", "legacy-only-term")
    _write_markdown(skill_dir / "references" / "current.md", "Current", "current-only-term")

    # references/ exists, so docs/ should be ignored.
    no_legacy = module.search_docs(skill_dir, "legacy-only-term")
    assert no_legacy == []

    current = module.search_docs(skill_dir, "current-only-term")
    assert len(current) == 1

    # Remove references/ to validate fallback behavior.
    shutil.rmtree(skill_dir / "references")

    legacy = module.search_docs(skill_dir, "legacy-only-term")
    assert len(legacy) == 1
