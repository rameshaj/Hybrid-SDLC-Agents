#!/usr/bin/env python3
"""
OpenAI fallback client (chat completions).
Reads API key from OPENAI_API_KEY.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Tuple, Dict, Any


def openai_chat_completion(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
) -> Tuple[str, Dict[str, Any]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    url = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")

    body = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer. "
                    "Return ONLY a unified diff patch. "
                    "First line must start with: diff --git. "
                    "No explanations."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        raise RuntimeError(f"OpenAI HTTPError: {e.code} {e.reason} {body}".strip())
    except urllib.error.URLError as e:
        raise RuntimeError(f"OpenAI URLError: {e.reason}")

    content = ""
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = ""

    return content, data
