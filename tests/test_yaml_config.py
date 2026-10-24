import pytest

from neko2020.adapters.yaml_config import YamlConfigProvider, _deep_merge


# ---------------------------------------------------------------------------
# _deep_merge
# ---------------------------------------------------------------------------


def test_deep_merge_adds_new_key():
    assert _deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_deep_merge_overrides_scalar():
    assert _deep_merge({"a": 1}, {"a": 2}) == {"a": 2}


def test_deep_merge_merges_nested_dicts():
    result = _deep_merge({"a": {"b": 1, "c": 2}}, {"a": {"b": 99}})
    assert result == {"a": {"b": 99, "c": 2}}


def test_deep_merge_adds_nested_key_from_user():
    result = _deep_merge({"a": {"b": 1}}, {"a": {"c": 2}})
    assert result == {"a": {"b": 1, "c": 2}}


def test_deep_merge_three_way():
    result = _deep_merge({"a": 1}, {"b": 2}, {"a": 3})
    assert result == {"a": 3, "b": 2}


def test_deep_merge_does_not_mutate_inputs():
    base = {"a": {"b": 1}}
    overlay = {"a": {"b": 99}}
    _deep_merge(base, overlay)
    assert base["a"]["b"] == 1


# ---------------------------------------------------------------------------
# YamlConfigProvider.reload
# ---------------------------------------------------------------------------


def test_reload_uses_defaults_when_no_user_config(tmp_path):
    default = tmp_path / "default.yml"
    default.write_text("fps: 4\nspeed:\n  max: 60\n")
    p = YamlConfigProvider(str(default), str(tmp_path / "missing.yml"))
    p.reload()
    assert p.get_int("fps") == 4
    assert p.get_int("speed.max") == 60


def test_reload_user_scalar_overrides_default(tmp_path):
    default = tmp_path / "default.yml"
    default.write_text("fps: 4\n")
    user = tmp_path / "user.yml"
    user.write_text("fps: 10\n")
    p = YamlConfigProvider(str(default), str(user))
    p.reload()
    assert p.get_int("fps") == 10


def test_reload_user_nested_override_preserves_other_keys(tmp_path):
    default = tmp_path / "default.yml"
    default.write_text("speed:\n  max: 60\n  min: 2\n")
    user = tmp_path / "user.yml"
    user.write_text("speed:\n  max: 120\n")
    p = YamlConfigProvider(str(default), str(user))
    p.reload()
    assert p.get_int("speed.max") == 120
    assert p.get_int("speed.min") == 2


def test_reload_can_be_called_multiple_times(tmp_path):
    default = tmp_path / "default.yml"
    default.write_text("fps: 4\n")
    user = tmp_path / "user.yml"
    user.write_text("fps: 8\n")
    p = YamlConfigProvider(str(default), str(user))
    p.reload()
    p.reload()
    assert p.get_int("fps") == 8


# ---------------------------------------------------------------------------
# Type accessors
# ---------------------------------------------------------------------------


def test_get_int(tmp_path):
    f = tmp_path / "d.yml"
    f.write_text("fps: 4\n")
    p = YamlConfigProvider(str(f), str(tmp_path / "x.yml"))
    p.reload()
    assert p.get_int("fps") == 4


def test_get_float(tmp_path):
    f = tmp_path / "d.yml"
    f.write_text("scale: 1.5\n")
    p = YamlConfigProvider(str(f), str(tmp_path / "x.yml"))
    p.reload()
    assert p.get_float("scale") == pytest.approx(1.5)


def test_get_string(tmp_path):
    f = tmp_path / "d.yml"
    f.write_text("animal: neko\n")
    p = YamlConfigProvider(str(f), str(tmp_path / "x.yml"))
    p.reload()
    assert p.get_string("animal") == "neko"


def test_get_nested_value_via_dot_notation(tmp_path):
    f = tmp_path / "d.yml"
    f.write_text("speed:\n  max: 60\n")
    p = YamlConfigProvider(str(f), str(tmp_path / "x.yml"))
    p.reload()
    assert p.get_int("speed.max") == 60


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_missing_top_level_key_raises(tmp_path):
    f = tmp_path / "d.yml"
    f.write_text("fps: 4\n")
    p = YamlConfigProvider(str(f), str(tmp_path / "x.yml"))
    p.reload()
    with pytest.raises((TypeError, AttributeError)):
        p.get_int("nonexistent")


def test_missing_nested_key_raises(tmp_path):
    f = tmp_path / "d.yml"
    f.write_text("speed:\n  min: 2\n")
    p = YamlConfigProvider(str(f), str(tmp_path / "x.yml"))
    p.reload()
    with pytest.raises(TypeError):
        p.get_int("speed.max")
