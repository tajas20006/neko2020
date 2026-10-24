import os
from unittest.mock import MagicMock, patch

from neko2020.infrastructure import files
from neko2020.infrastructure.image_loader import (
    _resolve_animal_dir,
    load_images,
    resize_image,
)


# ---------------------------------------------------------------------------
# resize_image
# ---------------------------------------------------------------------------


def test_resize_image_scalar_int_applies_to_both_axes():
    img = MagicMock()
    img.width = 10
    img.height = 20
    resize_image(img, 3)
    img.resize.assert_called_once_with((30, 60))


def test_resize_image_scalar_float_applies_to_both_axes():
    img = MagicMock()
    img.width = 32
    img.height = 32
    resize_image(img, 2.0)
    img.resize.assert_called_once_with((64, 64))


def test_resize_image_dict_scale_applies_axes_independently():
    img = MagicMock()
    img.width = 32
    img.height = 32
    resize_image(img, {"x": 2.0, "y": 0.5})
    img.resize.assert_called_once_with((64, 16))


def test_resize_image_returns_result_of_resize():
    img = MagicMock()
    img.width = 10
    img.height = 20
    result = resize_image(img, 1.0)
    assert result is img.resize.return_value


# ---------------------------------------------------------------------------
# _resolve_animal_dir
# ---------------------------------------------------------------------------


def test_resolve_animal_dir_returns_project_resource_when_no_user_base():
    result = _resolve_animal_dir("neko", None)
    expected = os.path.join(files.get_project_root(), "resource", "neko")
    assert result == expected


def test_resolve_animal_dir_uses_user_dir_when_it_exists(tmp_path):
    (tmp_path / "neko").mkdir()
    result = _resolve_animal_dir("neko", str(tmp_path))
    assert result == str(tmp_path / "neko")


def test_resolve_animal_dir_falls_back_to_project_when_user_subdir_missing(
    tmp_path,
):
    # tmp_path exists but has no "neko" subdirectory
    result = _resolve_animal_dir("neko", str(tmp_path))
    expected = os.path.join(files.get_project_root(), "resource", "neko")
    assert result == expected


# ---------------------------------------------------------------------------
# load_images
# ---------------------------------------------------------------------------


def _mock_img(w=32, h=32):
    img = MagicMock()
    img.width = w
    img.height = h
    img.resize.return_value = img
    return img


def test_load_images_returns_32_icons():
    mock_img = _mock_img()
    with (
        patch(
            "neko2020.infrastructure.image_loader.Image.open",
            return_value=mock_img,
        ),
        patch("neko2020.infrastructure.image_loader.ImageTk.PhotoImage"),
    ):
        icons, _w, _h = load_images("neko")
    assert len(icons) == 32


def test_load_images_returns_image_dimensions():
    mock_img = _mock_img(w=48, h=48)
    with (
        patch(
            "neko2020.infrastructure.image_loader.Image.open",
            return_value=mock_img,
        ),
        patch("neko2020.infrastructure.image_loader.ImageTk.PhotoImage"),
    ):
        _icons, w, h = load_images("neko")
    assert w == 48
    assert h == 48


def test_load_images_wraps_each_frame_in_photo_image():
    mock_img = _mock_img()
    with (
        patch(
            "neko2020.infrastructure.image_loader.Image.open",
            return_value=mock_img,
        ),
        patch(
            "neko2020.infrastructure.image_loader.ImageTk.PhotoImage"
        ) as mock_photo,
    ):
        icons, _w, _h = load_images("neko")
    assert mock_photo.call_count == 32
    assert len(icons) == 32


def test_load_images_applies_scalar_scale():
    mock_img = _mock_img(w=32, h=32)
    with (
        patch(
            "neko2020.infrastructure.image_loader.Image.open",
            return_value=mock_img,
        ),
        patch("neko2020.infrastructure.image_loader.ImageTk.PhotoImage"),
    ):
        load_images("neko", scale=2.0)
    mock_img.resize.assert_called_with((64, 64))


def test_load_images_resolves_icons_under_user_resource_base(tmp_path):
    (tmp_path / "neko").mkdir()
    mock_img = _mock_img()
    opened_paths = []

    def _fake_open(path):
        opened_paths.append(path)
        return mock_img

    with (
        patch(
            "neko2020.infrastructure.image_loader.Image.open",
            side_effect=_fake_open,
        ),
        patch("neko2020.infrastructure.image_loader.ImageTk.PhotoImage"),
    ):
        load_images("neko", user_resource_base=str(tmp_path))

    user_neko_dir = str(tmp_path / "neko")
    assert all(p.startswith(user_neko_dir) for p in opened_paths)
