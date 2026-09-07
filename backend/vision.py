"""
vision.py — provider-agnostic multimodal (text + images -> text) client for the mock-quiz
photo pipeline. Defaults to Claude (Anthropic), but works with any OpenAI-compatible vision
endpoint (OpenAI, local servers, gateways). Returns None on ANY failure so the pipeline
degrades to manual self-grading (Atlas invariant 12) — a mock is still valuable without a key.

Provider selection (auto unless MULTIMODAL_PROVIDER forces it):
  - anthropic : ANTHROPIC_API_KEY set. Model: MULTIMODAL_MODEL or claude-fable-5.
  - openai    : OPENAI_API_KEY set. Base: OPENAI_BASE_URL or https://api.openai.com/v1.
                Model: MULTIMODAL_MODEL or gpt-4o. (Any OpenAI-compatible server works.)
  - none      : no key -> capability() reports False; callers self-grade.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.request

_ANTHROPIC_MODEL = "claude-fable-5"
_OPENAI_MODEL = "gpt-4o"


def _provider() -> str:
    forced = os.environ.get("MULTIMODAL_PROVIDER", "").strip().lower()
    if forced:
        return forced
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "none"


def capability() -> dict:
    """What the UI shows: is auto transcription/grading available, and via whom."""
    p = _provider()
    model = os.environ.get("MULTIMODAL_MODEL") or (
        _ANTHROPIC_MODEL if p == "anthropic" else _OPENAI_MODEL if p == "openai" else None)
    return {"available": p != "none", "provider": p, "model": model}


def _media_type(data: bytes, filename: str = "") -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if data[:3] == b"\xff\xd8\xff" or ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n" or ext == "png":
        return "image/png"
    if ext in ("webp",) or data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _call_anthropic(system: str, text: str, images: list[tuple[bytes, str]], max_tokens: int):
    key = os.environ["ANTHROPIC_API_KEY"]
    model = os.environ.get("MULTIMODAL_MODEL", _ANTHROPIC_MODEL)
    content = []
    for data, fn in images:
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": _media_type(data, fn),
                       "data": base64.b64encode(data).decode()},
        })
    content.append({"type": "text", "text": text})
    body = json.dumps({
        "model": model, "max_tokens": max_tokens, "system": system,
        "messages": [{"role": "user", "content": content}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read())
    return data["content"][0]["text"].strip()


def _call_openai(system: str, text: str, images: list[tuple[bytes, str]], max_tokens: int):
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("MULTIMODAL_MODEL", _OPENAI_MODEL)
    parts = [{"type": "text", "text": text}]
    for data, fn in images:
        uri = f"data:{_media_type(data, fn)};base64,{base64.b64encode(data).decode()}"
        parts.append({"type": "image_url", "image_url": {"url": uri}})
    body = json.dumps({
        "model": model, "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": parts}],
    }).encode()
    req = urllib.request.Request(
        base + "/chat/completions", data=body,
        headers={"authorization": f"Bearer {key}", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read())
    return data["choices"][0]["message"]["content"].strip()


def ask(system: str, text: str, images: list[tuple[bytes, str]] | None = None,
        max_tokens: int = 1500) -> str | None:
    """Send a prompt (+ optional images as (bytes, filename)) and return text, or None."""
    images = images or []
    p = _provider()
    try:
        if p == "anthropic":
            return _call_anthropic(system, text, images, max_tokens)
        if p == "openai":
            return _call_openai(system, text, images, max_tokens)
        return None
    except Exception:
        return None


def ask_json(system: str, text: str, images: list[tuple[bytes, str]] | None = None,
             max_tokens: int = 2000) -> dict | list | None:
    """Like ask(), but parse the first JSON object/array out of the response. None on failure."""
    raw = ask(system, text, images, max_tokens)
    if raw is None:
        return None
    try:
        # tolerate code fences / prose around the JSON
        for opener, closer in (("{", "}"), ("[", "]")):
            if opener in raw:
                start = raw.index(opener)
                end = raw.rindex(closer) + 1
                return json.loads(raw[start:end])
    except Exception:
        return None
    return None
