# Fallback: Manim Community instead of ManimGX

Use this only if ManimGX will not install or will not render on the machine (setup.sh's test frame fails). Say so to the user. The goal is the same look: same palette, fonts, layout, captions, background, timing and audio. This path has not been run end to end; follow it step by step and verify with `check`.

## What stays the same

Everything that is not drawing: `timeline.py` (timing, captions, `.srt`), `music.py`, `mix.py`, `background.py`'s ffmpeg filter and glow images, `checks.py`, `join.py`, `claims.py`, `leakcheck.py`, `estimate.py`, and the CLI. Chapter files keep their structure because ManimGX follows Manim Community's Python API: `Text`, `RoundedRectangle`, `Circle`, `Arc`, `ArcBetweenPoints`, `VGroup`, `FadeIn(shift=, scale=)`, `Create`, `GrowArrow`, `LaggedStart`, `Transform`, `.animate`, updaters, `add_foreground_mobjects`, `there_and_back`.

## Steps

1. Install Manim Community in the same venv: `$VG_VENV/bin/pip install manim` (it needs Cairo and Pango system libraries; on Debian/Ubuntu `apt install libcairo2-dev libpango1.0-dev pkg-config`). Install the Noto Sans font system-wide (`fonts-noto-core`), since manimgx-fonts will not be used.
2. Copy `engine/` to `engine_ce/` and work there, so the ManimGX engine stays intact.
3. In every engine module and chapter file, `import manimgx as m` becomes `import manim as m`.
4. `style.setup_config()`: keep `pixel_width`, `pixel_height`, `frame_rate`, `background_color`; add `m.config.frame_height = 8.0` and `m.config.frame_width = 8.0 * 16 / 9` so units match (1 unit = 180 px).
5. `render.py`: Manim Community writes a file instead of handing over frames. Render each scene with a transparent background (`m.config.transparent = True`, `m.config.movie_file_extension = ".mov"`, output into a temp folder), then composite it with the same background: run ffmpeg with the `.mov` as input 0 instead of the raw pipe, `background.ffmpeg_inputs()` after it, and `background.ffmpeg_filter()` with `overlay=alpha=premultiplied` changed to plain `overlay` (the `.mov` alpha is straight, not premultiplied). Keep `-frames:v` at `round(dur * 30)`, CRF 18, yuv420p, `+faststart`.
6. `stills.py`: render the scene the same way, then pull frames with `ffmpeg -ss <t> -i scene.mov -frames:v 1` and composite each with `background.composite_still` after converting straight alpha to premultiplied (multiply RGB by alpha).
7. `narrated.py`: `self.time` exists in Manim Community too. Manim Community does not add ManimGX's closing frame, so in `finish()` drop the "one frame early" adjustment (use `end = round(dur * 30) / 30 - 1e-4`) if `check` reports scenes one frame short. Manim Community writes every frame, so frame counts follow `run_time` directly.
8. `Text(..., weight="BOLD")` works with Pango; if a font name is not found, Pango substitutes silently: compare a still with the test frame.
9. Run the scratch test from `examples/` (or a 2-segment chapter with placeholder WAVs): `timing`, `stills`, `render-all`, `audio`, `assemble`, `check` must end with ALL SCENES MATCH and the video duration equal to the timing total.

## Expect

Rendering with Cairo is slower than ManimGX on the same CPU; budget render-all accordingly (`--budget`). If the look differs (stroke widths, text size), adjust in `style.py`, never per scene.
