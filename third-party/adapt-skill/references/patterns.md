# Adaptation Patterns — Before & After

Detailed code examples showing the standard changes for adapting third-party skills.

## Pattern 1: SKILL.md Frontmatter

### Before
```yaml
---
name: example-skill
description: ...
required_environment_variables: [{"name": "OPENROUTER_API_KEY", "prompt": "OpenRouter API key for the skill's LLM-powered steps.", "required_for": "optional features"}]
metadata: {"openclaw": {"primaryEnv": "OPENROUTER_API_KEY", "envVars": [{"name": "OPENROUTER_API_KEY", "required": false, "description": "OpenRouter API key for the skill's LLM-powered steps."}]}}
---
```

### After
```yaml
---
name: example-skill
description: ...
required_environment_variables: []
metadata: {}
---
```

---

## Pattern 2: SKILL.md API Key Setup Section

### Before
```markdown
## Environment Setup

```bash
# Required
export OPENROUTER_API_KEY='your_api_key_here'

# Get key at: https://openrouter.ai/keys
```
```

### After
```markdown
## Authentication

Authentication is automatic via `~/.future/agent/auth.json`.
Run `future auth login` to authenticate. No API key needed.
```

---

## Pattern 3: generate_schematic_ai.py — Imports

### Before
```python
import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

try:
    import requests
except ImportError:
    print("Error: requests library not found.")
    sys.exit(1)

def _load_env_file():
    """Load .env file."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    ...
```

### After
```python
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Any

# No requests, no dotenv, no base64 needed
```

---

## Pattern 4: generate_schematic_ai.py — Class __init__

### Before
```python
def __init__(self, api_key=None, verbose=False):
    self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not self.api_key:
        _load_env_file()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
    if not self.api_key:
        raise ValueError("OPENROUTER_API_KEY not found...")
    self.base_url = "https://openrouter.ai/api/v1"
    self.image_model = "google/gemini-3.1-flash-image-preview"
    self.review_model = "google/gemini-3.1-pro-preview"
```

### After
```python
def __init__(self, verbose=False):
    self.verbose = verbose
    self._last_error = None
    # No API key, no base URL, no model IDs
```

---

## Pattern 5: generate_schematic_ai.py — _make_request → _run_future

### Before
```python
def _make_request(self, model, messages, modalities=None):
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "...",
        "X-Title": "..."
    }
    response = requests.post(
        f"{self.base_url}/chat/completions",
        headers=headers,
        json={"model": model, "messages": messages, ...},
        timeout=120
    )
    return response.json()
```

### After
```python
def _run_future(args, timeout=600):
    """Run a future CLI command."""
    result = subprocess.run(
        ["future"] + args,
        capture_output=True, text=True, timeout=timeout
    )
    return result
```

---

## Pattern 6: generate_schematic_ai.py — generate_image

### Before
```python
def generate_image(self, prompt):
    messages = [{"role": "user", "content": prompt}]
    response = self._make_request(
        model=self.image_model,
        messages=messages,
        modalities=["image", "text"]
    )
    image_data = self._extract_image_from_response(response)
    return image_data  # bytes
```

### After
```python
def generate_image(self, prompt, output_path, size="1024x1024"):
    args_dict = {
        "prompt": prompt,
        "size": size,
        "quality": "high",
        "output_format": Path(output_path).suffix.lstrip(".") or "png",
    }
    result = _run_future([
        "tools", "call", "image_gen",
        "--args", json.dumps(args_dict),
        "--output", output_path,
    ])
    if result.returncode != 0:
        # parse error, return False
        return False
    return True  # File saved by --output
```

---

## Pattern 7: generate_schematic_ai.py — review_image

### Before
```python
def review_image(self, image_path, original_prompt, ...):
    image_data_url = self._image_to_base64(image_path)
    messages = [{"role": "user", "content": [
        {"type": "text", "text": review_prompt},
        {"type": "image_url", "image_url": {"url": image_data_url}}
    ]}]
    response = self._make_request(model=self.review_model, messages=messages)
    content = response["choices"][0]["message"]["content"]
    # parse score, verdict...
```

### After
```python
def review_image(self, image_path, original_prompt, ...):
    args_dict = {
        "image_path": str(Path(image_path).resolve()),
        "question": review_question,
    }
    result = _run_future([
        "tools", "call", "read_image",
        "--args", json.dumps(args_dict),
    ])
    response = json.loads(result.stdout)
    content = response.get("answer", "")
    # parse score, verdict...
```

---

## Pattern 8: generate_image.py

### Before
```python
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", ...},
    json={"model": model, "messages": [...], "modalities": ["image", "text"]}
)
result = response.json()
# Extract image from response["choices"][0]["message"]["images"]
# Save base64-decoded image
```

### After
```python
result = subprocess.run(
    ["future", "tools", "call", "image_gen",
     "--args", json.dumps({"prompt": prompt, "size": size, "quality": quality}),
     "--output", output_path],
    capture_output=True, text=True, timeout=600
)
# Image already saved to output_path by --output flag
```

---

## Pattern 9: generate_schematic.py (wrapper)

### Before
```python
api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("Error: OPENROUTER_API_KEY environment variable not set")
    print("Get one at: https://openrouter.ai/keys")
    sys.exit(1)
env = os.environ.copy()
env["OPENROUTER_API_KEY"] = api_key
result = subprocess.run(cmd, check=False, env=env)
```

### After
```python
# No API key check. Auth is automatic.
result = subprocess.run(cmd, check=False)
```

---

## Removed Dependencies

After adaptation, these are no longer needed:
- `requests` library
- `python-dotenv` library
- `.env` files
- `OPENROUTER_API_KEY` environment variable
- Any `_get_credential()` / `check_env_file()` / `_load_env_file()` functions
- `base64` encoding/decoding of images
- Model ID strings (`google/gemini-3.1-flash-image-preview`, etc.)
- `base_url` / endpoint configuration
