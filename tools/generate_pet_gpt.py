#!/usr/bin/env python3
"""
Generate custom pet sprites using gpt-image-2 (OpenAI).

Not included in the exe. Install the imgen-gpt dependency group first:
    uv sync --group imgen-gpt

Requires an OpenAI API key in the OPENAI_API_KEY environment variable.

Usage:
    # From text prompt only
    uv run --group imgen-gpt python tools/generate_pet_gpt.py \\
        --name mycat --prompt "cute orange tabby cat"

    # From a hand-drawn character image (recommended for best results)
    uv run --group imgen-gpt python tools/generate_pet_gpt.py \\
        --name mycat --prompt "cute orange tabby cat" \\
        --base-image mycharacter.png

    # Skip prompt expansion
    uv run --group imgen-gpt python tools/generate_pet_gpt.py \\
        --name mycat --prompt "..." --no-expand

Generation strategy
-------------------
Without --base-image:
  1. The user's prompt is expanded by gpt-5.4-mini.
  2. The "Awake" frame is generated via images.generate.
  3. All other 31 frames are generated via images.edit using the Awake
     frame as the style reference.

With --base-image (hand-drawn character):
  1. The user's prompt is expanded by gpt-5.4-mini.
  2. All 32 frames are generated via images.edit using the supplied
     image as the style reference — no generate step needed.

In both cases rembg removes the background and icons are saved as
transparent 32x32 RGBA ICOs.

Icons are saved to ~/.config/neko2020/resources/<name>/. Activate with
`animal: <name>` in ~/.config/neko2020/config.yml.
"""
import argparse
import base64
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image
from rembg import remove as remove_bg

# fmt: off
ICON_NAMES = [
    "Awake",
    "up1", "up2",
    "upright1", "upright2",
    "right1", "right2",
    "downright1", "downright2",
    "down1", "down2",
    "downleft1", "downleft2",
    "left1", "left2",
    "upleft1", "upleft2",
    "upclaw1", "upclaw2",
    "rightclaw1", "rightclaw2",
    "leftclaw1", "leftclaw2",
    "downclaw1", "downclaw2",
    "wash2",
    "scratch1", "scratch2",
    "yawn2", "yawn3",
    "sleep1", "sleep2",
]
# fmt: on

POSE_PROMPTS: dict[str, str] = {
    "Awake":      "sitting upright, facing forward, alert, surprised",
    "up1":        "rear view, back facing viewer, walking away, step 1, right leg forward",  # noqa:E501
    "up2":        "rear view, back facing viewer, walking away, step 2, left leg forward",  # noqa:E501
    "upright1":   "3/4 rear view facing upper-right, walking away, step 1, right leg forward",  # noqa:E501
    "upright2":   "3/4 rear view facing upper-right, walking away, step 2, left leg forward",  # noqa:E501
    "right1":     "walking right, step 1, right leg forward",
    "right2":     "walking right, step 2, left leg forward",
    "downright1": "walking lower-right, step 1, right leg forward",
    "downright2": "walking lower-right, step 2, left leg forward",
    "down1":      "walking downward, step 1, right leg forward",
    "down2":      "walking downward, step 2, left leg forward",
    "downleft1":  "walking lower-left, step 1, right leg forward",
    "downleft2":  "walking lower-left, step 2, left leg forward",
    "left1":      "walking left, step 1, right leg forward",
    "left2":      "walking left, step 2, left leg forward",
    "upleft1":    "3/4 rear view facing upper-left, walking away, step 1, right leg forward",  # noqa:E501
    "upleft2":    "3/4 rear view facing upper-left, walking away, step 2, left leg forward",  # noqa:E501
    "upclaw1":    "rear view, clinging to wall above, scratching upward, frame 1",  # noqa:E501
    "upclaw2":    "rear view, clinging to wall above, scratching upward, frame 2",  # noqa:E501
    "rightclaw1": "clinging to right wall, scratching, frame 1",
    "rightclaw2": "clinging to right wall, scratching, frame 2",
    "leftclaw1":  "clinging to left wall, scratching, frame 1",
    "leftclaw2":  "clinging to left wall, scratching, frame 2",
    "downclaw1":  "scratching the floor, frame 1",
    "downclaw2":  "scratching the floor, frame 2",
    "wash2":      "grooming, washing face with paw",
    "scratch1":   "scratching self, frame 1",
    "scratch2":   "scratching self, frame 2",
    "yawn2":      "yawning, mouth open",
    "yawn3":      "yawning, mouth wide open",
    "sleep1":     "sleeping, curled up, frame 1, exhale",
    "sleep2":     "sleeping, curled up, frame 2, inhale",
}

ICON_SIZE = 32
GEN_SIZE = 1024

_EXPAND_SYSTEM = """\
You are a prompt engineer for AI image generation of pixel art desktop-pet
sprites. Given a short character description, write a single detailed
image-generation prompt that produces a consistent, high-quality pixel art
character. Cover: exact colours and markings, body shape, facial features,
chibi/cute proportions, and any distinctive accessories. Do NOT include pose
or animation instructions — those are added separately. Output only the
prompt text, with no explanation, no quotes, and no preamble."""

_STYLE = (
    "pixel art style, chibi proportions, white background, "
    "clean sprite, cute, simple, game asset, "
    "full body centered, fixed character scale, "
    "character fills 80% of canvas. "
)


def _user_resource_dir() -> str:
    xdg = os.getenv(
        "XDG_CONFIG_HOME",
        os.path.join(os.path.expanduser("~"), ".config"),
    )
    return os.path.join(xdg, "neko2020", "resources")


def _save_ico(img: Image.Image, path: str) -> None:
    rgba = img.convert("RGBA")
    resized = rgba.resize((ICON_SIZE, ICON_SIZE), Image.NEAREST)
    resized.save(path, format="ICO", sizes=[(ICON_SIZE, ICON_SIZE)])


def _to_png_bytes(img: Image.Image) -> io.BytesIO:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def _full_transparent_mask() -> io.BytesIO:
    """Fully transparent mask — gpt-image-2 regenerates everything."""
    mask = Image.new("RGBA", (GEN_SIZE, GEN_SIZE), (0, 0, 0, 0))
    return _to_png_bytes(mask)


def _decode_image(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64)))


def _expand_prompt(client, user_prompt: str, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _EXPAND_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def _generate(client, prompt: str) -> Image.Image:
    resp = client.images.generate(
        model="gpt-image-2",
        prompt=prompt,
        size=f"{GEN_SIZE}x{GEN_SIZE}",
    )
    return _decode_image(resp.data[0].b64_json)


def _edit(client, reference: Image.Image, prompt: str) -> Image.Image:
    ref_rgba = reference.convert("RGBA").resize(
        (GEN_SIZE, GEN_SIZE), Image.NEAREST
    )
    resp = client.images.edit(
        model="gpt-image-2",
        image=("reference.png", _to_png_bytes(ref_rgba), "image/png"),
        mask=("mask.png", _full_transparent_mask(), "image/png"),
        prompt=prompt,
        size=f"{GEN_SIZE}x{GEN_SIZE}",
    )
    return _decode_image(resp.data[0].b64_json)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate custom pet sprites using gpt-image-2.\n"
            "Requires: uv sync --group imgen-gpt\n"
            "          OPENAI_API_KEY environment variable"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Animal name; icons saved to "
             "~/.config/neko2020/resources/<name>/",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Short description of the pet character",
    )
    parser.add_argument(
        "--base-image",
        metavar="PATH",
        help=(
            "Hand-drawn character image (PNG/JPG/WEBP). When supplied, "
            "every frame is generated via images.edit from this image "
            "instead of first generating an Awake reference."
        ),
    )
    parser.add_argument(
        "--expand-model",
        default="gpt-5.4-mini",
        help="OpenAI model for prompt expansion (default: gpt-5.4-mini)",
    )
    parser.add_argument(
        "--no-expand",
        action="store_true",
        help="Skip prompt expansion and use --prompt as-is",
    )
    parser.add_argument(
        "--style",
        default=_STYLE,
        help="Style tokens appended to every frame prompt",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel API calls for images.edit (default: 4)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY environment variable is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    # ------------------------------------------------------------------ #
    # Prompt expansion                                                     #
    # ------------------------------------------------------------------ #
    if args.no_expand:
        character_prompt = args.prompt
    else:
        print(f"Expanding prompt with {args.expand_model}...")
        try:
            character_prompt = _expand_prompt(
                client, args.prompt, args.expand_model
            )
            print(f"Expanded prompt:\n  {character_prompt}\n")
        except Exception as e:
            print(f"Expansion failed ({e}), using prompt as-is.\n")
            character_prompt = args.prompt

    out_dir = os.path.join(_user_resource_dir(), args.name)
    os.makedirs(out_dir, exist_ok=True)
    print(f"Output directory : {out_dir}")
    print()

    total = len(ICON_NAMES)

    def _do_edit(name, reference):
        frame_prompt = (
            f"{character_prompt}, {POSE_PROMPTS[name]}, {args.style}"
        )
        raw = _edit(client, reference, frame_prompt)
        frame = remove_bg(raw)
        _save_ico(frame, os.path.join(out_dir, f"{name}.ico"))
        return name

    def _run_parallel(tasks):
        """tasks: list of (name, reference). Prints as each completes."""
        done = 0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(_do_edit, name, ref): name
                for name, ref in tasks
            }
            for fut in as_completed(futures):
                done += 1
                name = futures[fut]
                try:
                    fut.result()
                    print(f"  [{done}/{len(tasks)}] {name} done")
                except Exception as exc:
                    print(f"  [{done}/{len(tasks)}] {name} FAILED: {exc}")

    if args.base_image:
        # ---------------------------------------------------------------- #
        # Base-image mode: all 32 frames in parallel                       #
        # ---------------------------------------------------------------- #
        reference = Image.open(args.base_image).convert("RGBA")
        print(f"Generating {total} frames in parallel "
              f"(workers={args.workers})...")
        _run_parallel([(name, reference) for name in ICON_NAMES])
    else:
        # ---------------------------------------------------------------- #
        # Text-only mode: generate Awake first, then 31 frames in parallel #
        # ---------------------------------------------------------------- #
        print(f"[1/{total}] Awake  (images.generate)")
        awake_prompt = (
            f"{character_prompt}, {POSE_PROMPTS['Awake']}, {args.style}"
        )
        awake_img = _generate(client, awake_prompt)
        _save_ico(
            remove_bg(awake_img), os.path.join(out_dir, "Awake.ico")
        )

        remaining = [n for n in ICON_NAMES if n != "Awake"]
        print(f"Generating {len(remaining)} frames in parallel "
              f"(workers={args.workers})...")
        _run_parallel([(name, awake_img) for name in remaining])

    print()
    print(
        f"Done! {total} icons saved to "
        f"~/.config/neko2020/resources/{args.name}/"
    )
    print("To use your new pet, add this to ~/.config/neko2020/config.yml:")
    print(f"    animal: {args.name}")


if __name__ == "__main__":
    main()
