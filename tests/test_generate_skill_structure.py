import os
import stat

from site2skill.generate_skill_structure import generate_skill_structure


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def test_generate_skill_structure_creates_references_and_metadata(tmp_path):
    source_dir = tmp_path / "src"
    output_base = tmp_path / "out"
    nested_md = source_dir / "docs.example.com" / "api" / "index.md"
    nested_md.parent.mkdir(parents=True, exist_ok=True)
    nested_md.write_text("# API\n", encoding="utf-8")

    generate_skill_structure(
        "demo",
        str(source_dir),
        str(output_base),
        skill_description="Demo description",
        target_agent="codex",
    )

    skill_dir = output_base / "demo"
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "description: Demo description" in skill_md
    assert "target_agent: codex" in skill_md
    assert "Query Building" in skill_md
    assert "references/" in skill_md

    copied = skill_dir / "references" / "docs.example.com" / "api" / "index.md"
    assert copied.exists()

    search_script = skill_dir / "scripts" / "search_docs.py"
    mode = search_script.stat().st_mode
    assert mode & stat.S_IXUSR


def test_replace_skill_md_flag_controls_overwrite(tmp_path):
    source_dir = tmp_path / "src"
    output_base = tmp_path / "out"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "root.md").write_text("# Root\n", encoding="utf-8")

    generate_skill_structure("demo", str(source_dir), str(output_base), skill_description="First")
    skill_md_path = output_base / "demo" / "SKILL.md"
    skill_md_path.write_text("custom\n", encoding="utf-8")

    generate_skill_structure("demo", str(source_dir), str(output_base), skill_description="Second")
    assert skill_md_path.read_text(encoding="utf-8") == "custom\n"

    generate_skill_structure(
        "demo",
        str(source_dir),
        str(output_base),
        skill_description="Third",
        replace_skill_md=True,
    )
    replaced = skill_md_path.read_text(encoding="utf-8")
    assert "description: Third" in replaced


def test_full_sync_removes_stale_references_and_legacy_docs(tmp_path):
    source_dir = tmp_path / "src"
    output_base = tmp_path / "out"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "fresh.md").write_text("# Fresh\n", encoding="utf-8")

    skill_dir = output_base / "demo"
    _write(str(skill_dir / "references" / "stale.md"), "stale\n")
    _write(str(skill_dir / "docs" / "legacy.md"), "legacy\n")

    generate_skill_structure(
        "demo",
        str(source_dir),
        str(output_base),
        full_sync=True,
    )

    assert not (skill_dir / "references" / "stale.md").exists()
    assert not (skill_dir / "docs" / "legacy.md").exists()
    assert (skill_dir / "references" / "fresh.md").exists()
