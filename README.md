# /render — 3D Model Skill for Grok 

<img width="702" height="745" alt="Screenshot 2026-04-01 alle 00 15 56" src="https://github.com/user-attachments/assets/d6bca223-2d33-4342-9d16-20a3f593731e" />


A Grok skill that generates 3D models from text descriptions or reference images using [build123d](https://github.com/gumyr/build123d) and renders them in a browser viewer at http://localhost:3123.

```
/render a gear with 12 teeth
/render a phone case with rounded corners
/render a torus knot
```

Grok writes the parametric Python code using build123d, executes it via the skill, and the model appears in your browser within seconds. Open the code panel (</>) to tweak parameters and re-render with Ctrl+Enter.

## Install (Grok)

```bash
# The skill is already installed at ~/.grok/skills/render
# First run of /render will auto-run setup.sh and install build123d (~30s one-time)
```

That's it. Type `/render a box with a hole` (or just mention "render a gear") in any Grok session. The native ~/.grok version takes precedence.

## How it works

```
you: "/render a gear"
        │
        ▼
   Grok (via /render skill) writes build123d Python code
        │
        ▼
   Executes → exports .glb to viewer/models/
        │
        ▼
   Three.js viewer auto-loads the model
   http://localhost:3123
```

The viewer starts automatically on first render. It includes:
- Three.js 3D viewport with orbit controls
- Hamburger (☰) menu in the top-right with all toolbar actions
- Code editor panel (`</> code`) for tweaking parameters, Ctrl+Enter to re-render
- Model gallery (`▦ models`) to browse previous renders
- Render mode toggle (solid / wireframe / x-ray)
- Cross-section slice (`✂ slice`) — X/Y/Z axis, position slider, flip
- STEP export (`⬳ STEP`) for sending to a slicer or CAD tool
- Edit mode (`✎ edit`) — drag a box on the model, type an instruction, Grok (or Claude) applies it via the skill
- Auto-reload on new models

By default, `render("model", shape)` exports the authored build123d geometry
exactly. For a quick shell/infill preview, use `render("model", shape,
printable=True)` or `render_printable("model", shape)`.

## Region-based edits (✎)

Click `✎ edit` in the menu, drag a rectangle over the part of the model you
want to change, type an instruction ("make this hole bigger", "replace this
grid with dots", "add a Ø3 mm hole here"), and press send. The viewer captures
a screenshot with the red selection rectangle and queues it under
`viewer/edits/pending/`.

The agent (Grok via the skill, or Claude) picks up queued edits in one of two ways:

- **On-demand**: type `/render apply pending edits` — the skill processes every
  queued edit, modifies the relevant `viewer/models/<name>.py`, re-runs it,
  and the viewer reloads.
- **Hands-free**: the first time you run `/render` in a Grok session, the skill
  auto-arms a scheduler (using Grok's scheduler_create tool) that polls for
  new ✎ submissions. (Claude users can still use the old /loop method.)

Every applied edit is echoed back in chat as `📝 Edit prompt: "..."` so you
can see exactly what you asked for before the change lands.

## Files

```
├── SKILL.md           # Skill definition + build123d API reference
├── setup.sh           # One-time bootstrap (creates .venv, installs build123d)
├── viewer/
│   ├── index.html     # Three.js viewer, hamburger menu, edit/slice tools
│   ├── serve.py       # Local HTTP server (port 3123) + /api/edit endpoint
│   ├── render.py      # render() helper for exporting .glb + .step
│   ├── models/        # Generated .glb / .step files + scripts
│   └── edits/
│       ├── pending/   # Queued ✎ edits waiting for Claude
│       └── processed/ # Applied edits (kept for history)
└── README.md
```

## Requirements

- Python 3.10+

No other dependencies — `setup.sh` creates an isolated venv and installs everything.

## Manual / standalone usage

You can run the viewer directly (useful for testing or outside a Grok/Claude session):

```bash
# Grok location (preferred)
~/.grok/skills/render/.venv/bin/python3 ~/.grok/skills/render/viewer/serve.py

# Claude compatibility location (also works)
# ~/.claude/skills/render/.venv/bin/python3 ~/.claude/skills/render/viewer/serve.py

# Write a script (example)
cat > ~/.grok/skills/render/viewer/models/script.py << 'EOF'
from build123d import *
from viewer.render import render

box = Box(10, 10, 10) - Cylinder(4, 12)
box.color = Color("steelblue")
render("model", box)
EOF

# Run it (Grok skill dir)
PYTHONPATH=~/.grok/skills/render ~/.grok/skills/render/.venv/bin/python3 ~/.grok/skills/render/viewer/models/script.py
```
