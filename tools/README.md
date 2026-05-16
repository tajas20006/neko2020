# tools/

Standalone scripts for generating custom pet sprites. These are not
included in the exe and require separate dependency groups.

---

## generate_pet_gpt.py — gpt-image-2 (recommended)

Uses OpenAI's gpt-image-2 to generate all 32 animation frames.
Requires an OpenAI API key (`OPENAI_API_KEY` environment variable).

**Cost: ~$1.50 per full set of 32 icons.**

```bash
uv sync --extra imgen-gpt

# From a text prompt
uv run --extra imgen-gpt python tools/generate_pet_gpt.py \
    --name mycat --prompt "cute orange tabby cat"

# From a hand-drawn character (recommended for best results)
uv run --extra imgen-gpt python tools/generate_pet_gpt.py \
    --name mycat --prompt "cute orange tabby cat" \
    --base-image mycharacter.png
```

Key options:

| Flag | Default | Description |
|---|---|---|
| `--name` | required | Output dir under `~/.config/neko2020/resources/` |
| `--prompt` | required | Short character description |
| `--base-image` | — | Hand-drawn reference image |
| `--no-expand` | off | Skip gpt-5.4-mini prompt expansion |
| `--expand-model` | `gpt-5.4-mini` | Model used for prompt expansion |
| `--workers` | `4` | Parallel API calls (lower if you hit rate limits) |
| `--style` | pixel art tokens | Style tokens appended to every prompt |

---

## generate_pet.py — Stable Diffusion (local GPU)

Uses Stable Diffusion locally via diffusers. No API cost, but requires
a CUDA GPU and several GB of VRAM.

```bash
uv sync --extra imgen

uv run --extra imgen python tools/generate_pet.py \
    --name mycat --prompt "cute orange tabby cat"
```

Key options:

| Flag | Default | Description |
|---|---|---|
| `--name` | required | Output dir under `~/.config/neko2020/resources/` |
| `--prompt` | required | Short character description |
| `--ollama-model` | `qwen3.5` | Local model for prompt expansion |
| `--no-expand` | off | Skip Ollama prompt expansion |
| `--model` | `Onodofthenorth/SD_PixelArt_SpriteSheet_Generator` | HuggingFace model ID |
| `--seed` | `42` | Random seed |
| `--strength` | `0.5` | img2img strength (lower = closer to neko reference) |
| `--workers` | — | Not parallelized (GPU is the bottleneck) |

---

## Activating a generated pet

Add this to `~/.config/neko2020/config.yml`:

```yaml
animal: <name>
```
