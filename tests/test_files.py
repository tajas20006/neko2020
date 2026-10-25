import os
import pytest

from neko2020.infrastructure.files import (
    get_project_root,
    get_user_resource_dir,
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


def test_get_user_config_dir_respects_xdg_config_home(tmp_path, monkeypatch):
    from neko2020.infrastructure.files import get_user_config_dir

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert get_user_config_dir() == str(tmp_path / "neko2020")


def test_list_animals_merges_and_sorts_both_dirs(tmp_path):
    from neko2020.infrastructure.files import list_animals

    project = tmp_path / "project"
    (project / "neko").mkdir(parents=True)
    (project / "dog").mkdir()
    (project / "file.txt").write_text("x")
    user = tmp_path / "user"
    (user / "cat").mkdir(parents=True)
    (user / "dog").mkdir()
    assert list_animals(str(project), str(user)) == ["cat", "dog", "neko"]


def test_list_animals_ignores_missing_directories(tmp_path):
    from neko2020.infrastructure.files import list_animals

    missing = str(tmp_path / "nope")
    assert list_animals(missing, missing) == []


def test_list_animals_defaults_to_bundled_and_user_resource_dirs(
    tmp_path, monkeypatch
):
    from neko2020.infrastructure import files

    (tmp_path / "project" / "resource" / "neko").mkdir(parents=True)
    (tmp_path / "user" / "cat").mkdir(parents=True)
    monkeypatch.setattr(
        files, "get_project_root", lambda: str(tmp_path / "project")
    )
    monkeypatch.setattr(
        files, "get_user_resource_dir", lambda: str(tmp_path / "user")
    )
    assert files.list_animals() == ["cat", "neko"]
