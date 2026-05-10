#!/usr/bin/env python3
"""
Generate custom pet sprites using Stable Diffusion.

Not included in the exe. Install the imgen dependency group first:
    uv sync --group imgen

Usage:
    uv run --group imgen python tools/generate_pet.py \\
        --name mycat --prompt "cute orange tabby cat"

    # Skip Ollama prompt expansion
    uv run --group imgen python tools/generate_pet.py \\
        --name mycat --prompt "cute orange tabby cat" --no-expand

The user's prompt is first expanded into a detailed image-generation
prompt by a local Ollama model (default: qwen3.5), then each of the
32 frames uses the matching neko sprite as the img2img pose reference.

Icons are saved to ~/.config/neko2020/resources/<name>/ as transparent
32x32 RGBA ICOs. Activate with `animal: <name>` in
~/.config/neko2020/config.yml.
"""
import argparse
import os
import re

import torch
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

ICON_SIZE = 32
GEN_SIZE = 512

_EXPAND_SYSTEM = """\
You are a prompt engineer for Stable Diffusion pixel art sprite generation.
Given a short character description, write a single detailed image-generation
prompt that will produce a consistent, high-quality pixel art desktop-pet
sprite. Cover: exact colours and markings, body shape, facial features, \
chibi/cute proportions, and any distinctive accessories. Do NOT include \
pose or animation instructions — those are added separately. Output only \
the prompt text, with no explanation, no quotes, and no preamble."""


def _user_resource_dir() -> str:
    xdg = os.getenv(
        "XDG_CONFIG_HOME",
        os.path.join(os.path.expanduser("~"), ".config"),
    )
    return os.path.join(xdg, "neko2020", "resources")


def _neko_dir() -> str:
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    return os.path.join(project_root, "resource", "neko")


def _load_neko_ref(name: str) -> Image.Image:
    path = os.path.join(_neko_dir(), f"{name}.ico")
    return (
        Image.open(path)
        .convert("RGB")
        .resize((GEN_SIZE, GEN_SIZE), Image.NEAREST)
    )


def _save_ico(img: Image.Image, path: str) -> None:
    rgba = img.convert("RGBA")
    resized = rgba.resize((ICON_SIZE, ICON_SIZE), Image.NEAREST)
    resized.save(path, format="ICO", sizes=[(ICON_SIZE, ICON_SIZE)])


def _generator(seed: int, device: str) -> torch.Generator:
    return torch.Generator(device=device).manual_seed(seed)


def _run_img2img(pipe, image, prompt, neg, seed, strength, steps, device):
    return pipe(
        prompt=prompt,
        image=image,
        negative_prompt=neg,
        num_inference_steps=steps,
        strength=strength,
        generator=_generator(seed, device),
    ).images[0]


def _expand_prompt(user_prompt: str, model: str) -> str:
    import ollama

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": _EXPAND_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = response["message"]["content"]
    # Qwen3 wraps chain-of-thought in <think>…</think>; strip it out.
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate custom pet sprites using Stable Diffusion.\n"
            "Requires: uv sync --group imgen"
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
        "--ollama-model",
        default="qwen3.5",
        help="Ollama model used to expand the prompt (default: qwen3.5)",
    )
    parser.add_argument(
        "--no-expand",
        action="store_true",
        help="Skip Ollama prompt expansion and use --prompt as-is",
    )
    parser.add_argument(
        "--model",
        default="Onodofthenorth/SD_PixelArt_SpriteSheet_Generator",
        help=(
            "Hugging Face model ID (default: "
            "Onodofthenorth/SD_PixelArt_SpriteSheet_Generator)"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=30,
        help="Number of diffusion inference steps (default: 30)",
    )
    parser.add_argument(
        "--strength",
        type=float,
        default=0.5,
        help=(
            "img2img denoising strength 0.0–1.0; lower = closer to "
            "the neko reference pose (default: 0.5)"
        ),
    )
    parser.add_argument(
        "--negative-prompt",
        default=(
            "blurry, low quality, deformed, extra limbs, "
            "watermark, text, background clutter"
        ),
        help="Negative prompt applied to every frame",
    )
    parser.add_argument(
        "--style",
        default=(
            "pixel art, small sprite, white background, "
            "cute, chibi, simple, clean lines"
        ),
        help=(
            "Style tokens appended to every frame prompt. "
            "Keep 'white background' so rembg produces a clean mask."
        ),
    )
    parser.add_argument(
        "--device",
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Compute device: cuda or cpu (auto-detected by default)",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------ #
    # Expand the user's short prompt into a detailed SD prompt            #
    # ------------------------------------------------------------------ #
    if args.no_expand:
        character_prompt = args.prompt
    else:
        print(f"Expanding prompt with {args.ollama_model}...")
        try:
            character_prompt = _expand_prompt(
                args.prompt, args.ollama_model
            )
            print(f"Expanded prompt:\n  {character_prompt}\n")
        except Exception as e:
            print(f"Ollama expansion failed ({e}), using prompt as-is.\n")
            character_prompt = args.prompt

    full_prompt = f"{character_prompt}, {args.style}"

    # ------------------------------------------------------------------ #
    # Set up                                                              #
    # ------------------------------------------------------------------ #
    out_dir = os.path.join(_user_resource_dir(), args.name)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Output directory : {out_dir}")
    print(f"Device           : {args.device}")
    print(f"Model            : {args.model}")
    print(f"Seed             : {args.seed}")
    print(f"Strength         : {args.strength}")
    print()

    from diffusers import StableDiffusionImg2ImgPipeline

    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        args.model,
        torch_dtype=(
            torch.float16 if args.device == "cuda" else torch.float32
        ),
        safety_checker=None,
        use_safetensors=False,
    ).to(args.device)

    # ------------------------------------------------------------------ #
    # Generate                                                            #
    # ------------------------------------------------------------------ #
    total = len(ICON_NAMES)
    for idx, name in enumerate(ICON_NAMES, start=1):
        print(f"[{idx}/{total}] {name}")
        neko_ref = _load_neko_ref(name)
        raw = _run_img2img(
            pipe,
            neko_ref,
            full_prompt,
            args.negative_prompt,
            args.seed,
            args.strength,
            args.steps,
            args.device,
        )
        frame = remove_bg(raw)
        _save_ico(frame, os.path.join(out_dir, f"{name}.ico"))

    print()
    print(
        f"Done! {total} icons saved to "
        f"~/.config/neko2020/resources/{args.name}/"
    )
    print("To use your new pet, add this to ~/.config/neko2020/config.yml:")
    print(f"    animal: {args.name}")


if __name__ == "__main__":
    main()
