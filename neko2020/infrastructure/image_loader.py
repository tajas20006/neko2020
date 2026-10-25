import os

from PIL import Image, ImageTk

from neko2020.infrastructure import files


def resize_image(img, scale):
    if isinstance(scale, int | float):
        scale = {"x": scale, "y": scale}
    return img.resize(
        (int(img.width * scale["x"]), int(img.height * scale["y"]))
    )


def _resolve_animal_dir(animal, user_resource_base):
    if user_resource_base:
        user_dir = os.path.join(user_resource_base, animal)
        if os.path.isdir(user_dir):
            return user_dir
    return os.path.join(files.get_project_root(), "resource", animal)


# The sprite file names every animal directory must provide.
# fmt: off
ICON_NAMES = (
    "Awake", "up1", "up2", "upright1", "upright2",
    "right1", "right2", "downright1", "downright2",
    "down1", "down2", "downleft1", "downleft2",
    "left1", "left2", "upleft1", "upleft2",
    "upclaw1", "upclaw2", "rightclaw1", "rightclaw2",
    "leftclaw1", "leftclaw2", "downclaw1", "downclaw2",
    "wash2", "scratch1", "scratch2", "yawn2", "yawn3",
    "sleep1", "sleep2",
)
# fmt: on


def load_images(
    animal="neko",
    scale=1.0,
    user_resource_base=None,
):
    icons = {}

    base_icon_dir = _resolve_animal_dir(animal, user_resource_base)
    for name in ICON_NAMES:
        icon_path = os.path.join(base_icon_dir, ".".join([name, "ico"]))
        with Image.open(icon_path) as src:
            img = resize_image(src, scale)
        icons[name] = ImageTk.PhotoImage(img)

    return icons, img.width, img.height


def load_image(animal="neko", icon_name="Awake.ico"):
    icon_path = os.path.join(
        files.get_project_root(), "resource", animal, icon_name
    )
    return Image.open(icon_path)
