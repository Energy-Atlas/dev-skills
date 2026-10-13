"""Tests for skills/editorial-icons/scripts/prepare_dependencies.py, with a fake home folder and no real installs."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "skills" / "editorial-icons" / "scripts"))
import prepare_dependencies as prep  # noqa: E402


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("EDITORIAL_ICONS_HOME", str(home))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "cache"))
    return home


@pytest.fixture
def commands(monkeypatch):
    """Record commands instead of running them."""
    ran = []

    def fake_run(command, dry_run, log):
        ran.append(command)
        log.append("$ " + " ".join(command))
        return True

    monkeypatch.setattr(prep, "run", fake_run)
    monkeypatch.setattr(prep.shutil, "which", lambda name: None)  # no `claude` CLI
    return ran


def install_custom_icons(root: Path) -> Path:
    skill = root / "custom-icons"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: custom-icons\ndescription: x\n---\n", encoding="utf-8")
    (skill / "scripts" / "validate_icon.py").write_text("", encoding="utf-8")
    return skill


def install_draw_plugin(home: Path) -> Path:
    renderer = home / ".claude" / "plugins" / "cache" / "claudedraw" / "draw" / "2.1.0" / "skills" / "draw" / "draw.py"
    renderer.parent.mkdir(parents=True)
    renderer.write_text("", encoding="utf-8")
    return renderer


def test_finds_installed_dependencies_without_running_anything(fake_home, commands, tmp_path):
    skill = install_custom_icons(fake_home / ".agents" / "skills")
    renderer = install_draw_plugin(fake_home)
    log = []
    custom = prep.prepare_custom_icons(tmp_path, update=False, dry_run=False, log=log)
    draw = prep.prepare_draw(update=False, dry_run=False, log=log)
    assert custom["ready"] and custom["status"] == "found"
    assert Path(custom["validator"]) == (skill / "scripts" / "validate_icon.py").resolve()
    assert draw["ready"] and Path(draw["renderer"]) == renderer.resolve()
    assert commands == []


def test_project_install_wins_over_global(fake_home, commands, tmp_path):
    install_custom_icons(fake_home / ".claude" / "skills")
    project_skill = install_custom_icons(tmp_path / ".claude" / "skills")
    custom = prep.prepare_custom_icons(tmp_path, update=False, dry_run=False, log=[])
    assert Path(custom["skill_dir"]) == project_skill.resolve()


def test_skill_is_matched_by_front_matter_name_not_folder(fake_home, commands, tmp_path):
    other = fake_home / ".claude" / "skills" / "custom-icons"
    other.mkdir(parents=True)
    (other / "SKILL.md").write_text("---\nname: something-else\n---\n", encoding="utf-8")
    assert prep.find_skill("custom-icons", tmp_path) is None


def test_missing_dependencies_are_installed_latest(fake_home, commands, tmp_path):
    log = []
    custom = prep.prepare_custom_icons(tmp_path, update=False, dry_run=False, log=log)
    draw = prep.prepare_draw(update=False, dry_run=False, log=log)
    assert commands[0][:4] == ["npx", "-y", "skills", "add"]
    assert "jkc66/custom-icons-skill" in commands[0] and "--copy" in commands[0]
    assert commands[1][:2] == ["git", "clone"] and prep.DRAW["repo"] in commands[1]
    # The fakes install nothing, so both stay not ready and say so.
    assert custom["status"] == "installed" and not custom["ready"]
    assert draw["status"] == "installed" and not draw["ready"]


def test_draw_uses_the_claude_cli_when_present(fake_home, monkeypatch, commands, tmp_path):
    monkeypatch.setattr(prep.shutil, "which", lambda name: "claude" if name == "claude" else None)
    prep.prepare_draw(update=False, dry_run=False, log=[])
    assert commands[0] == ["claude", "plugin", "marketplace", "add", "Griffin2/claudedraw"]
    assert commands[1] == ["claude", "plugin", "install", "draw@claudedraw"]


def test_update_refreshes_installed_skill(fake_home, commands, tmp_path):
    install_custom_icons(fake_home / ".claude" / "skills")
    custom = prep.prepare_custom_icons(tmp_path, update=True, dry_run=False, log=[])
    assert commands[0][:5] == ["npx", "-y", "skills", "update", "custom-icons"]
    assert custom["status"] == "updated" and custom["ready"]


def test_main_reports_json_and_fails_when_custom_icons_is_missing(fake_home, commands, tmp_path, capsys):
    status = prep.main(["--project", str(tmp_path), "--json"])
    report = json.loads(capsys.readouterr().out)
    assert status == 1
    assert report["custom-icons"]["ready"] is False
    assert report["draw"]["optional"] is True


def test_dry_run_changes_nothing_and_succeeds(fake_home, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(prep.shutil, "which", lambda name: None)
    status = prep.main(["--project", str(tmp_path), "--dry-run"])
    out = capsys.readouterr().out
    assert status == 0
    assert "would install" in out
    assert not (tmp_path / "cache").exists()
