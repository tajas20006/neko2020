import os

from PIL import Image, ImageTk

from neko2020.infrastructure import files


def resize_image(img, scale):
    if type(scale) in {int, float}:
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


def load_images(
    animal="neko",
    scale={"x": 1.0, "y": 1.0},
    user_resource_base=None,
):
    # fmt: off
    icon_names = [
        "Awake", "up1", "up2", "upright1", "upright2",
        "right1", "right2", "downright1", "downright2",
        "down1", "down2", "downleft1", "downleft2",
        "left1", "left2", "upleft1", "upleft2",
        "upclaw1", "upclaw2", "rightclaw1", "rightclaw2",
        "leftclaw1", "leftclaw2", "downclaw1", "downclaw2",
        "wash2", "scratch1", "scratch2", "yawn2", "yawn3",
        "sleep1", "sleep2",
    ]
    # fmt: on

    icons = []

    base_icon_dir = _resolve_animal_dir(animal, user_resource_base)
    for name in icon_names:
        icon_path = os.path.join(base_icon_dir, ".".join([name, "ico"]))
        img = Image.open(icon_path)
        img = resize_image(img, scale)
        icons.append(ImageTk.PhotoImage(img))

    return icons, img.width, img.height


def load_image(animal="neko", icon_name="Awake.ico"):
    icon_path = os.path.join(
        files.get_project_root(), "resource", animal, icon_name
    )
    return Image.open(icon_path)
