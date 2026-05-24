from unittest.mock import MagicMock, patch

from neko2020.adapters.tkinter_renderer import TkinterRenderer
from neko2020.domain.value_objects import Point, Rect, Size

_ICON_COUNT = 32


def _make_canvas(w=800, h=600):
    canvas = MagicMock()
    canvas.winfo_width.return_value = w
    canvas.winfo_height.return_value = h
    return canvas


def _make_config(animal="neko"):
    config = MagicMock()
    config.get_string.return_value = animal
    return config


def _make_renderer(
    animal="neko",
    vx=0,
    vy=0,
    canvas_w=800,
    canvas_h=600,
    initial=Point(100, 100),
):
    canvas = _make_canvas(canvas_w, canvas_h)
    config = _make_config(animal)
    mock_images = [MagicMock() for _ in range(_ICON_COUNT)]

    with (
        patch(
            "neko2020.adapters.tkinter_renderer.image_loader.load_images",
            return_value=(mock_images, 32, 32),
        ),
        patch(
            "neko2020.adapters.tkinter_renderer.files.get_user_resource_dir",
            return_value=None,
        ),
    ):
        renderer = TkinterRenderer(canvas, config, vx, vy, initial)

    return renderer, canvas, mock_images


# ---------------------------------------------------------------------------
# get_position / get_size / get_bounds
# ---------------------------------------------------------------------------


def test_get_position_returns_initial_position():
    renderer, _c, _imgs = _make_renderer(initial=Point(42, 77))
    assert renderer.get_position() == Point(42, 77)


def test_get_size_reflects_image_dimensions():
    renderer, _c, _imgs = _make_renderer()
    assert renderer.get_size() == Size(32, 32)


def test_get_bounds_covers_canvas_area_with_offset():
    renderer, _c, _imgs = _make_renderer(
        vx=10, vy=20, canvas_w=800, canvas_h=600
    )
    assert renderer.get_bounds() == Rect(10, 20, 810, 620)


def test_get_bounds_zero_origin():
    renderer, _c, _imgs = _make_renderer(
        vx=0, vy=0, canvas_w=1920, canvas_h=1080
    )
    assert renderer.get_bounds() == Rect(0, 0, 1920, 1080)


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


def test_render_clears_canvas_before_drawing():
    renderer, canvas, _imgs = _make_renderer()
    renderer.render(0, 100, 100)
    canvas.delete.assert_called_with("all")


def test_render_creates_image_on_canvas():
    renderer, canvas, _imgs = _make_renderer()
    renderer.render(0, 100, 100)
    canvas.create_image.assert_called_once()


def test_render_subtracts_virtual_origin_from_coords():
    renderer, canvas, _imgs = _make_renderer(vx=50, vy=30)
    renderer.render(0, 200, 130)
    args = canvas.create_image.call_args.args
    assert args[0] == 150  # 200 - 50
    assert args[1] == 100  # 130 - 30


def test_render_passes_correct_frame_image():
    renderer, canvas, imgs = _make_renderer()
    renderer.render(5, 100, 100)
    kwargs = canvas.create_image.call_args.kwargs
    assert kwargs["image"] is imgs[5]


def test_render_updates_stored_position():
    renderer, _c, _imgs = _make_renderer(initial=Point(0, 0))
    renderer.render(0, 300, 400)
    assert renderer.get_position() == Point(300, 400)


def test_render_skips_redraw_when_frame_and_position_unchanged():
    renderer, canvas, _imgs = _make_renderer(initial=Point(0, 0))
    renderer.render(0, 100, 100)
    canvas.reset_mock()
    renderer.render(0, 100, 100)
    canvas.delete.assert_not_called()
    canvas.create_image.assert_not_called()


def test_render_redraws_when_frame_index_changes():
    renderer, canvas, _imgs = _make_renderer()
    renderer.render(0, 100, 100)
    canvas.reset_mock()
    renderer.render(1, 100, 100)
    canvas.create_image.assert_called_once()


def test_render_redraws_when_position_changes():
    renderer, canvas, _imgs = _make_renderer()
    renderer.render(0, 100, 100)
    canvas.reset_mock()
    renderer.render(0, 200, 100)
    canvas.create_image.assert_called_once()


# ---------------------------------------------------------------------------
# random animal selection
# ---------------------------------------------------------------------------


def test_random_animal_calls_select_random_directory_merged():
    canvas = _make_canvas()
    config = _make_config("random")
    mock_images = [MagicMock() for _ in range(_ICON_COUNT)]

    with (
        patch(
            "neko2020.adapters.tkinter_renderer.image_loader.load_images",
            return_value=(mock_images, 32, 32),
        ),
        patch(
            "neko2020.adapters.tkinter_renderer.files.get_user_resource_dir",
            return_value="/some/path",
        ),
        patch(
            "neko2020.adapters.tkinter_renderer.files.select_random_directory_merged",
            return_value="neko",
        ) as mock_rand,
    ):
        TkinterRenderer(canvas, config, 0, 0, Point(0, 0))

    mock_rand.assert_called_once()


def test_non_random_animal_does_not_call_select_random_directory_merged():
    canvas = _make_canvas()
    config = _make_config("neko")
    mock_images = [MagicMock() for _ in range(_ICON_COUNT)]

    with (
        patch(
            "neko2020.adapters.tkinter_renderer.image_loader.load_images",
            return_value=(mock_images, 32, 32),
        ),
        patch(
            "neko2020.adapters.tkinter_renderer.files.get_user_resource_dir",
            return_value=None,
        ),
        patch(
            "neko2020.adapters.tkinter_renderer.files.select_random_directory_merged",
        ) as mock_rand,
    ):
        TkinterRenderer(canvas, config, 0, 0, Point(0, 0))

    mock_rand.assert_not_called()
