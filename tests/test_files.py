import os
import pytest

from neko2020.infrastructure.files import (
    get_project_root,
    get_user_resource_dir,
    select_random_directory,
    select_random_directory_merged,
)


# ---------------------------------------------------------------------------
# get_project_root
# ---------------------------------------------------------------------------


def test_get_project_root_is_a_directory():
    assert os.path.isdir(get_project_root())


def test_get_project_root_contains_pyproject_toml():
    root = get_project_root()
    assert os.path.exists(os.path.join(root, "pyproject.toml"))


# ---------------------------------------------------------------------------
# get_user_resource_dir
# ---------------------------------------------------------------------------


def test_get_user_resource_dir_default_uses_home_config(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    result = get_user_resource_dir()
    expected = os.path.join(
        os.path.expanduser("~"), ".config", "neko2020", "resources"
    )
    assert result == expected


def test_get_user_resource_dir_respects_xdg_config_home(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    result = get_user_resource_dir()
    assert result == str(tmp_path / "neko2020" / "resources")


# ---------------------------------------------------------------------------
# select_random_directory
# ---------------------------------------------------------------------------


def test_select_random_directory_returns_a_directory_name(tmp_path):
    (tmp_path / "dir_a").mkdir()
    (tmp_path / "dir_b").mkdir()
    result = select_random_directory(str(tmp_path))
    assert result in {"dir_a", "dir_b"}


def test_select_random_directory_ignores_files(tmp_path):
    (tmp_path / "only_dir").mkdir()
    (tmp_path / "file.txt").write_text("x")
    result = select_random_directory(str(tmp_path))
    assert result == "only_dir"


def test_select_random_directory_returns_name_not_full_path(tmp_path):
    (tmp_path / "mydir").mkdir()
    result = select_random_directory(str(tmp_path))
    assert result == "mydir"
    assert not os.path.sep in result


# ---------------------------------------------------------------------------
# select_random_directory_merged
# ---------------------------------------------------------------------------


def test_merged_includes_dirs_from_both_sources(tmp_path):
    project = tmp_path / "project"
    user = tmp_path / "user"
    project.mkdir()
    user.mkdir()
    (project / "neko").mkdir()
    (user / "catdog").mkdir()

    seen = set()
    for _ in range(30):
        seen.add(select_random_directory_merged(str(project), str(user)))

    assert "neko" in seen
    assert "catdog" in seen


def test_merged_with_only_project_dir(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "neko").mkdir()
    result = select_random_directory_merged(
        str(project), str(tmp_path / "nonexistent")
    )
    assert result == "neko"


def test_merged_with_only_user_dir(tmp_path):
    user = tmp_path / "user"
    user.mkdir()
    (user / "mycat").mkdir()
    result = select_random_directory_merged(
        str(tmp_path / "nonexistent"), str(user)
    )
    assert result == "mycat"


def test_merged_user_dir_overrides_same_name_from_project(tmp_path):
    project = tmp_path / "project"
    user = tmp_path / "user"
    project.mkdir()
    user.mkdir()
    (project / "neko").mkdir()
    (user / "neko").mkdir()
    # Same name from both → deduplicated, still returns "neko"
    result = select_random_directory_merged(str(project), str(user))
    assert result == "neko"


def test_merged_both_missing_raises_index_error(tmp_path):
    with pytest.raises(IndexError):
        select_random_directory_merged(
            str(tmp_path / "nope1"), str(tmp_path / "nope2")
        )
