---
name: render
description: >
  Generate a 3D model from a text description or reference image using build123d,
  execute the Python script, and display the result in the interactive browser viewer
  at http://localhost:3123. Supports "apply pending edit" (or "apply pending edits")
  to process ✎ region edits submitted from the viewer. Use when the user says
  "render", "/render", "make a 3D model", "create a part", "design a", "model a",
  "model from image", "recreate this", "build123d", supplies an image path + optional
  description, or refers to the 3D viewer / edits / code panel. Slash command:
  /render [image path and/or description of the 3D model].
argument-hint: [image path and/or description of the 3D model]
allowed-tools:
  - run_terminal_command
  - read_file
  - write
  - search_replace
  - scheduler_create
  - scheduler_list
  - scheduler_delete
  - list_dir
  - grep
metadata:
  short-description: "3D CAD modeling with build123d + local Three.js viewer (http://localhost:3123)"
---

# /render — Generate & View 3D Models (Grok)

Generate build123d Python code from a description (and optionally a reference
image), execute it, and display the result in the browser viewer at
http://localhost:3123.

## Preamble (run first)

Use the `run_terminal_command` tool with this command (it is idempotent and fast
after the first run):

```bash
bash ~/.grok/skills/render/setup.sh
```

If this prints `READY`, continue. If not, the setup will install build123d
into the skill's own venv (one-time, ~30s). The venv lives at
`~/.grok/skills/render/.venv`.

## Detect mode

Look at `$ARGUMENTS` (or the current user request):

- **Edit mode**: the arguments contain the phrase `apply pending edit` (singular
  or plural) or start with `edit`. The user has submitted one or more ✎ edits
  from the viewer and they are queued in `~/.grok/skills/render/viewer/edits/pending/`.
  Skip to the **Edit mode** steps below — process every pending edit, not just one.
  Example: `/render apply pending edits`

- **Image mode**: the arguments contain a file path to an image (`.png`, `.jpg`,
  `.jpeg`, `.webp`, `.gif`, `.bmp`, `.svg`). The path may be followed by an
  optional text description.
  Example: `/render ~/photos/bracket.jpg a mounting bracket`

- **Text mode**: no image path — just a text description.
  Example: `/render a gear with 20 teeth`

## Steps — Text mode (no image)

1. **Start the viewer** (if not already running):
   Use `run_terminal_command` with:
   ```bash
   lsof -i :3123 -t >/dev/null 2>&1 && echo "VIEWER_RUNNING" || (bash -c 'cd ~/.grok/skills/render/viewer && ~/.grok/skills/render/.venv/bin/python3 serve.py &>/tmp/build123d-viewer.log &' && sleep 1 && echo "VIEWER_STARTED" && open http://localhost:3123)
   ```
   Set `background: true` if you want the command to run detached (recommended for the server).

2. **Derive a slug** from the description: lowercase, underscores, max 30 chars.
   Examples: "a gear with 12 teeth" → `gear_12_teeth`, "phone case" → `phone_case`,
   "torus knot" → `torus_knot`.

3. **Write the script**: Create `~/.grok/skills/render/viewer/models/<slug>.py` using
   the `search_replace` tool with an **empty `old_string`** (this creates a new file).
   The script must:
   - Import `from build123d import *`
   - Import `from viewer.render import render`
   - Build the requested 3D model using build123d algebra or builder API
   - Call `render("<slug>", result)` at the end — use the same slug as the
     filename. Use `render("<slug>", result, printable=True)` only when the
     user asks for a shell/infill printable preview.

4. **Run it**:
   Use `run_terminal_command`:
   ```bash
   PYTHONPATH=~/.grok/skills/render ~/.grok/skills/render/.venv/bin/python3 ~/.grok/skills/render/viewer/models/<slug>.py
   ```

5. **Confirm** the model was rendered and tell the user to check http://localhost:3123.
   The viewer auto-reloads — the model appears within 1 second.
   The user can open the code panel (</> button) in the browser to tweak parameters
   and re-render with Ctrl+Enter. The □ dims button toggles a bounding-box overlay
   with W/D/H dimension labels. The slice (✂) button enables a cross-section clipping
   plane. The edit (✎) button lets the user drag a box over an area, type an
   instruction, and queue it for this session to modify that part of the model.

6. **Auto-arm the edit-apply loop** (do this on every text/image render; it's
   idempotent). Use the `scheduler_create` tool with:
   - `interval`: "60s" (or "1m")
   - `prompt`: "/render apply pending edits"
   - `recurring`: true
   - `description`: "auto-apply ✎ edits from the 3D viewer"
   Tell the user one line: "auto-apply loop armed via scheduler — ✎ edits will be picked up within ~60s".

## Steps — Image mode (reference image provided)

1. **Start the viewer** (exact same command as text mode step 1, using
   `run_terminal_command` with `background: true` for the server).

2. **Read the image**: Use the `read_file` tool directly on the image file path.
   Grok's multimodal vision will receive the image contents.

3. **Analyze the image**: Study the image carefully and identify:
   - What the object is (type, category, common name)
   - Overall shape and geometry (prismatic, cylindrical, organic, etc.)
   - Key features (holes, slots, fillets, chamfers, ribs, bosses, etc.)
   - Approximate proportions and relative dimensions
   - Any visible text, labels, or dimension callouts
   - Material appearance (helps choose colors)

4. **Research online**: Use `web_search` (the web_search tool) to find more
   information about the object. Search for standard dimensions, technical
   drawings, or build123d examples of similar geometry. Use `web_fetch` on
   promising results that contain dimension tables. Real-world dimensions make
   the model accurate.

5. **Plan the geometry**: Before writing code, outline your modeling strategy:
   - Base shape and dimensions (in mm)
   - Boolean operations needed (cuts, fuses)
   - Features to add (fillets, chamfers, patterns)
   - Which build123d API to use (algebra for simple, builder for complex)

6. **Derive a slug** from the object name (e.g. "ESP32 board" → `esp32_board`).
   Max 30 chars, lowercase, underscores.

7. **Write the script**: Create `~/.grok/skills/render/viewer/models/<slug>.py`
   using `search_replace` (empty old_string for new file).
   Include a comment block at the top noting:
   - Source: reference image
   - Estimated/researched dimensions
   - Any assumptions made
   Call `render("<slug>", result)` using the same slug.

8. **Run it** (same command as text mode).

9. **Confirm** and mention dimensions/assumptions.

10. **Auto-arm the edit-apply loop** (same as text-mode step 6) using
    `scheduler_create`.

## Steps — Edit mode (apply pending edits)

The browser viewer lets the user draw a rectangle on the 3D model and type an
instruction. Each ✎ submission writes one pair of files under
`~/.grok/skills/render/viewer/edits/pending/`:
- `<id>.png` — screenshot with a **red rectangle** marking the area to change.
- `<id>.json` — metadata: `prompt`, `model`, `script`, `rect`, `timestamp`.

Process them oldest-first, then move each pair to `viewer/edits/processed/`.

1. **List pending edits** (oldest first):
   Use `run_terminal_command`:
   ```bash
   ls -1tr ~/.grok/skills/render/viewer/edits/pending/*.json 2>/dev/null || echo "none"
   ```
   If the list is empty, report **"no pending edits"** and stop.

2. **For each pending `.json`** (oldest to newest):

   a. **Read the metadata**: Use `run_terminal_command` with `cat <path>` or
      `read_file` on the .json.

   b. **Echo the prompt to the chat** (required):
      ```
      📝 Edit prompt: "<prompt verbatim>"  (model: <model>, id: <id>)
      ```

   c. **Read the screenshot**: Use the `read_file` tool on `<id>.png`. The red
      rectangle marks the region.

   d. **Read the model script** at the path from the metadata (under
      `~/.grok/skills/render/...`). Fall back to `viewer/models/script.py` if needed.

   e. **Modify the script** to address the prompt *for the highlighted region only*.
      Use `search_replace` on the .py file.

   f. **Run it** (same python command as above).

   g. **Move the edit files**:
      ```bash
      mkdir -p ~/.grok/skills/render/viewer/edits/processed
      mv ~/.grok/skills/render/viewer/edits/pending/<id>.{png,json} ~/.grok/skills/render/viewer/edits/processed/
      ```

3. **Confirm**: one line per applied edit.

### Auto-apply (hands-free)

Use `scheduler_create` (interval "60s", recurring true, prompt "/render apply pending edits")
the first time you render in a session. When the queue is empty the tick is a no-op.
The user can also manually invoke `/render apply pending edits`.

## Description: $ARGUMENTS

## build123d Quick Reference

### Algebra mode (preferred — simpler)
```python
from build123d import *
from viewer.render import render

# Primitives
box = Box(width, depth, height)
cyl = Cylinder(radius, height)
sphere = Sphere(radius)
cone = Cone(bottom_radius, top_radius, height)
torus = Torus(major_radius, minor_radius)

# Booleans
result = box - cyl          # cut
result = box + cyl          # fuse
result = box & cyl          # intersect

# Positioning
part = Pos(x, y, z) * Box(1, 1, 1)
part = Rot(x_deg, y_deg, z_deg) * Cylinder(1, 2)

# Fillets and chamfers (on specific edges)
result = fillet(box.edges().filter_by(Axis.Z), radius=0.5)

# 2D sketches → 3D
sketch = Rectangle(10, 5)
solid = extrude(sketch, amount=3)

# Colors — never use black; always use clear/light colors
result.color = Color("steelblue")

render("gear_12_teeth", result)
```

### Builder mode (for complex models)
```python
from build123d import *
from viewer.render import render

with BuildPart() as part:
    Box(10, 10, 5)
    with BuildSketch(part.faces().sort_by(Axis.Z)[-1]):
        Circle(3)
    extrude(amount=-5, mode=Mode.SUBTRACT)
    fillet(part.edges().filter_by(Axis.Z), radius=0.5)

render("model", part.part)
```

### Key operations & selectors (same as original)

## Important (Grok-specific notes)

- The skill directory is `~/.grok/skills/render`. Use this for all absolute paths
  in commands and file operations.
- Always use `search_replace` with empty `old_string` to create new model .py files.
- For long-running viewer server, prefer `background: true` in `run_terminal_command`.
- For the edit auto-loop, use the `scheduler_create` tool (not the old Claude /loop).
- **Never use black or near-black colors.** Use light/saturated colors (steelblue,
  cornflowerblue, mediumseagreen, tomato, etc.).
- If the script fails, show the error and fix the code — do NOT ask the user to debug.
- The viewer at http://localhost:3123 works the same as the original (gallery, code
  panel, slice, dimensions, ✎ edits).
- Image input: just give `read_file` the path to any .png/.jpg/etc. Grok will see it.

## Image mode tips

- **Always research dimensions online** when possible.
- Mention your dimension sources and assumptions.
- For technical drawings with dimensions marked, use those directly.
