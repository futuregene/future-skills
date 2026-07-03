---
name: adapt-skill
description: Adapt third-party skills to FutureOS by replacing OpenRouter API dependencies with future CLI tools (image_gen, image_edit, read_image). Use when porting a skill that uses OPENROUTER_API_KEY, calls openrouter.ai API directly, or needs to switch from custom API credential code to automatic future auth. Trigger phrases include: "adapt this skill", "port to FutureOS", "remove OpenRouter", "convert to future CLI", "适配技能", "去除openrouter".
allowed-tools: Read Write Edit Bash
license: MIT license
metadata: {"version": "1.0.0", "skill-author": "K-Dense Inc."}
---

# Adapt Skill — Third-Party Skill Adaptation for FutureOS

Adapt third-party skills to use FutureOS platform tools instead of external API providers (OpenRouter). This skill documents the standard adaptation pattern and provides automated scripts.

## When to Use

Use this skill when:
- Porting a third-party skill that references `OPENROUTER_API_KEY` or `openrouter.ai`
- Adapting skills that call `https://openrouter.ai/api/v1` directly
- Replacing custom API credential management with `future auth credential`
- Converting Python scripts that use `requests` to call AI APIs → `future tools call`
- The user says "adapt this skill", "remove OpenRouter", "port to future CLI"

## Adaptation Principles

1. **Authentication**: Replace all API key management with `future auth credential` (automatic)
2. **Image generation**: Replace `requests.post(openrouter.ai/...)` with `future tools call image_gen`
3. **Image editing**: Replace API calls with `future tools call image_edit`
4. **Image review/analysis**: Replace API calls with `future tools call read_image`
5. **SKILL.md frontmatter**: Remove `OPENROUTER_API_KEY` from `required_environment_variables`

## Files That Typically Need Adaptation

| File | OpenRouter Pattern | FutureOS Replacement |
|---|---|---|
| `SKILL.md` | `required_environment_variables: [...OPENROUTER_API_KEY...]` | `required_environment_variables: []` |
| `SKILL.md` | `export OPENROUTER_API_KEY='...'` | `future auth login` |
| `scripts/generate_schematic_ai.py` | `requests.post("https://openrouter.ai/api/v1/chat/completions", ...)` | `future tools call image_gen` + `future tools call read_image` |
| `scripts/generate_schematic.py` | Checks `OPENROUTER_API_KEY` env var, passes it to subprocess | Pure passthrough wrapper |
| `scripts/generate_image.py` | `requests.post("https://openrouter.ai/api/v1/chat/completions", ...)` | `future tools call image_gen` / `future tools call image_edit` |

## Adaptation Workflow

### Step 1: Identify All OpenRouter References

```bash
grep -rni "openrouter\|OPENROUTER" <skill-directory>/
```

### Step 2: Adapt SKILL.md

Remove `OPENROUTER_API_KEY` from frontmatter and body. Replace with reference to `future auth login`.

**Before:**
```yaml
required_environment_variables: [{"name": "OPENROUTER_API_KEY", ...}]
```

**After:**
```yaml
required_environment_variables: []
```

Replace API key setup instructions:
```diff
- export OPENROUTER_API_KEY='your_api_key_here'
- Get a key at: https://openrouter.ai/keys
+ Authentication is automatic via `~/.future/agent/auth.json`.
+ Run `future auth login` to authenticate. No API key needed.
```

Run the automated script:
```bash
python scripts/adapt_skill_md.py <skill-directory>/SKILL.md
```

### Step 3: Adapt generate_schematic_ai.py

Replace the entire script with the FutureOS version that uses:
- `future tools call image_gen` for image generation
- `future tools call read_image` for quality review

The adapted script preserves:
- Quality thresholds by document type
- Smart iterative refinement logic
- Scientific diagram guidelines
- CLI interface (`--doc-type`, `--size`, `--iterations`, etc.)

Removes:
- All `requests` API calls
- `OPENROUTER_API_KEY` management
- `base_url` / endpoint configuration
- `load_dotenv` / `.env` file handling
- `_get_credential()` helpers

Run the automated script:
```bash
python scripts/adapt_schematic_ai.py <target-skill>/scripts/generate_schematic_ai.py
```

### Step 4: Adapt generate_image.py (if present)

Replace with FutureOS version using:
- `future tools call image_gen` for generation
- `future tools call image_edit` for editing

Run the automated script:
```bash
python scripts/adapt_image_gen.py <target-skill>/scripts/generate_image.py
```

### Step 5: Adapt generate_schematic.py (wrapper)

Replace with a pure passthrough wrapper. The wrapper just forwards all CLI arguments to `generate_schematic_ai.py`. No more API key checking or env var passing.

```python
#!/usr/bin/env python3
"""Thin wrapper around generate_schematic_ai.py — auth is automatic."""
import subprocess, sys
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    ai_script = script_dir / "generate_schematic_ai.py"
    if not ai_script.exists():
        print(f"Error: AI generation script not found: {ai_script}")
        sys.exit(1)
    cmd = [sys.executable, str(ai_script)] + sys.argv[1:]
    result = subprocess.run(cmd, check=False)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
```

### Step 6: Verify

```bash
# Zero OpenRouter references
grep -rni "openrouter\|OPENROUTER" <skill-directory>/ && echo "FAIL" || echo "✓ Clean"

# Zero API key code
grep -rni "api_key\|_get_credential\|check_env_file\|load_dotenv" <skill-directory>/ && echo "FAIL" || echo "✓ Clean"

# Scripts compile
python3 -c "import py_compile; py_compile.compile('<path>/generate_schematic_ai.py', doraise=True)"
```

## Future CLI Tools Reference

These tools replace direct API calls:

| Task | Future CLI Command |
|---|---|
| Generate image | `future tools call image_gen --args '{"prompt":"...","size":"1024x1024","quality":"high"}' --output ./out.png` |
| Edit image | `future tools call image_edit --args '{"prompt":"...","image_path":"/path/to/img.png"}' --output ./edited.png` |
| Analyze image | `future tools call read_image --args '{"image_path":"/path/to/img.png","question":"Describe this"}'` |

Authentication is automatic — the CLI reads credentials from `~/.future/agent/auth.json`. No API keys are needed.

## Known Third-Party Skills Requiring Adaptation

As of 2026-07-03, the following 13 skills have OpenRouter dependencies:

- `clinical-decision-support`
- `clinical-reports`
- `hypothesis-generation`
- `latex-posters`
- `peer-review`
- `pi-agent`
- `research-grants`
- `scholar-evaluation`
- `scientific-critical-thinking`
- `scientific-schematics`
- `scientific-writing`
- `treatment-plans`
- `venue-templates`

Common files in each: `SKILL.md`, `scripts/generate_schematic_ai.py`, `scripts/generate_schematic.py`. Some also have `scripts/generate_image.py`.

## Resources

- `references/patterns.md` — Detailed before/after code examples for each adaptation pattern
- `scripts/adapt_schematic_ai.py` — Automated replacement script for generate_schematic_ai.py
- `scripts/adapt_image_gen.py` — Automated replacement script for generate_image.py
- `scripts/adapt_skill_md.py` — Automated frontmatter cleanup for SKILL.md
