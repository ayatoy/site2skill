import sys
from typing import Any

from site2skill import main as main_module


def test_main_uses_target_default_output_and_skips_package_for_non_desktop(tmp_path, monkeypatch):
    calls: dict[str, Any] = {}

    monkeypatch.setattr(main_module, "fetch_site", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "convert_html_to_md", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "normalize_markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "validate_skill", lambda *_args, **_kwargs: True)

    def fake_generate(
        skill_name,
        source_dir,
        output_base,
        skill_description,
        full_sync,
        replace_skill_md,
        target_agent=None,
    ):
        calls["generate"] = {
            "skill_name": skill_name,
            "output_base": output_base,
            "skill_description": skill_description,
            "full_sync": full_sync,
            "replace_skill_md": replace_skill_md,
            "target_agent": target_agent,
        }

    def fake_package(*_args, **_kwargs):
        calls["packaged"] = True
        return "demo.skill"

    monkeypatch.setattr(main_module, "generate_skill_structure", fake_generate)
    monkeypatch.setattr(main_module, "package_skill", fake_package)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "site2skill",
            "https://example.com",
            "demo",
            "--target",
            "codex",
            "--temp-dir",
            str(tmp_path),
            "--skip-fetch",
        ],
    )
    main_module.main()

    assert calls["generate"]["output_base"] == ".codex/skills"
    assert calls["generate"]["target_agent"] == "codex"
    assert "packaged" not in calls


def test_main_packages_only_for_claude_desktop_unless_skip_package(tmp_path, monkeypatch):
    package_calls: list[tuple[str, str]] = []

    monkeypatch.setattr(main_module, "fetch_site", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "convert_html_to_md", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "normalize_markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "validate_skill", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(main_module, "generate_skill_structure", lambda *_args, **_kwargs: None)

    def fake_package(skill_dir, skill_output):
        package_calls.append((skill_dir, skill_output))
        return "demo.skill"

    monkeypatch.setattr(main_module, "package_skill", fake_package)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "site2skill",
            "https://example.com",
            "demo",
            "--target",
            "claude-desktop",
            "--temp-dir",
            str(tmp_path / "run1"),
            "--skip-fetch",
        ],
    )
    main_module.main()
    assert len(package_calls) == 1

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "site2skill",
            "https://example.com",
            "demo",
            "--target",
            "claude-desktop",
            "--temp-dir",
            str(tmp_path / "run2"),
            "--skip-fetch",
            "--skip-package",
        ],
    )
    main_module.main()
    assert len(package_calls) == 1


def test_main_keeps_optional_skill_description(tmp_path, monkeypatch):
    calls: dict[str, Any] = {}

    monkeypatch.setattr(main_module, "fetch_site", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "convert_html_to_md", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "normalize_markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "validate_skill", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(main_module, "package_skill", lambda *_args, **_kwargs: "demo.skill")

    def fake_generate(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs

    monkeypatch.setattr(main_module, "generate_skill_structure", fake_generate)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "site2skill",
            "https://example.com",
            "demo",
            "custom description",
            "--target",
            "claude-desktop",
            "--temp-dir",
            str(tmp_path),
            "--skip-fetch",
        ],
    )
    main_module.main()

    # Positional args: skill_name, source_dir, output_base, skill_description, full_sync, replace_skill_md
    assert calls["args"][3] == "custom description"
    assert calls["kwargs"]["target_agent"] == "claude-desktop"
