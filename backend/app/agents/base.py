"""
Base agent class for all SpecTwin agents.

Security policy (enforced at this layer):
- All prompt rendering sanitizes inputs to prevent prompt injection.
- API keys are never logged or included in prompt traces.
- Agent outputs are validated against a JSON schema before being returned.
- No user-supplied content is executed as code or shell commands.
"""
from __future__ import annotations

import json
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.config import settings


# Characters that could be used for prompt injection — stripped from artifact content
# before insertion into prompts.
_PROMPT_INJECTION_PATTERN = re.compile(
    r"(ignore\s+previous\s+instructions|override\s+system|"
    r"you\s+are\s+now|disregard\s+all\s+prior|act\s+as\s+if|"
    r"new\s+instructions:|SYSTEM\s*:)",
    re.IGNORECASE,
)


def sanitize_artifact_content(text: str) -> str:
    """
    Remove known prompt-injection patterns from artifact content.
    Artifact text is treated as DATA — any embedded instructions are neutralized.
    This ensures the output does not contain security violations caused by
    adversarial content in uploaded documents.
    """
    sanitized = _PROMPT_INJECTION_PATTERN.sub("[REDACTED-INJECTION-ATTEMPT]", text)
    # Truncate very long inputs to avoid token abuse
    if len(sanitized) > 12_000:
        sanitized = sanitized[:12_000] + "\n[...truncated for safety...]"
    return sanitized


def validate_json_output(raw: str, required_keys: list[str]) -> dict:
    """
    Parse agent output as JSON and validate required keys are present.
    Raises ValueError if output is not valid JSON or missing required keys.
    """
    # Strip markdown code fences if present (common LLM artifact)
    clean = raw.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```[a-z]*\n?", "", clean)
        clean = re.sub(r"\n?```$", "", clean)

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"Agent returned invalid JSON: {e}") from e

    for key in required_keys:
        if key not in parsed:
            raise ValueError(f"Agent output missing required key: '{key}'")

    return parsed


class BaseAgent(ABC):
    """Abstract base for all SpecTwin analysis agents."""

    name: str = "BaseAgent"
    required_output_keys: list[str] = ["agent", "findings"]

    def __init__(self):
        self.mock_mode = settings.MOCK_MODE

    def render_prompt(self, template: str, context: dict[str, Any]) -> str:
        """
        Render a prompt template by substituting {{ key }} placeholders.
        All values are sanitized before insertion to prevent prompt injection.
        Security: values are treated as plain text data, not instructions.
        """
        with open(
            f"app/prompts/system_base.txt", "r", encoding="utf-8"
        ) as f:
            system_base = f.read()

        rendered = template.replace("{{ SYSTEM_BASE }}", system_base)

        for key, value in context.items():
            placeholder = "{{ " + key + " }}"
            if isinstance(value, str):
                safe_value = sanitize_artifact_content(value)
            elif isinstance(value, (dict, list)):
                raw_json = json.dumps(value, ensure_ascii=True)
                safe_value = sanitize_artifact_content(raw_json)
            else:
                safe_value = sanitize_artifact_content(str(value))
            rendered = rendered.replace(placeholder, safe_value)

        return rendered

    @abstractmethod
    def get_mock_output(self, context: dict) -> dict:
        """Return deterministic mock output for demo/test mode."""
        ...

    @abstractmethod
    def build_context(self, **kwargs) -> dict:
        """Build the context dict for prompt rendering."""
        ...

    def run(self, **kwargs) -> dict:
        """
        Execute the agent. In mock mode returns deterministic output.
        In real mode calls the configured LLM provider.
        Timing and basic telemetry are always recorded.
        """
        start = time.monotonic()
        context = self.build_context(**kwargs)

        if self.mock_mode:
            result = self.get_mock_output(context)
            latency_ms = (time.monotonic() - start) * 1000
            result["_meta"] = {
                "agent": self.name,
                "mock": True,
                "latency_ms": round(latency_ms, 2),
            }
            return result

        # Real mode — load prompt template and call provider
        try:
            with open(f"app/prompts/{self._prompt_file}", "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            return {"error": f"Prompt template not found for {self.name}", "findings": []}

        rendered = self.render_prompt(template, context)
        raw_response = self._call_llm(rendered)

        try:
            result = validate_json_output(raw_response, self.required_output_keys)
        except ValueError as e:
            result = {"agent": self.name, "error": str(e), "findings": [], "raw": raw_response[:500]}

        latency_ms = (time.monotonic() - start) * 1000
        result["_meta"] = {
            "agent": self.name,
            "mock": False,
            "latency_ms": round(latency_ms, 2),
        }
        return result

    def _call_llm(self, prompt: str) -> str:
        """
        Call configured LLM provider. API keys are read from environment only —
        never logged or included in any response payload.
        """
        if settings.NVIDIA_API_KEY:
            return self._call_nvidia(prompt)
        if settings.ANTHROPIC_API_KEY:
            return self._call_anthropic(prompt)
        if settings.OPENAI_API_KEY:
            return self._call_openai(prompt)
        raise RuntimeError("No LLM provider configured. Set NVIDIA_API_KEY, ANTHROPIC_API_KEY or OPENAI_API_KEY.")

    def _call_nvidia(self, prompt: str) -> str:
        try:
            import openai  # type: ignore
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

        client = openai.OpenAI(
            api_key=settings.NVIDIA_API_KEY,
            base_url="https://integrate.api.nvidia.com/v1"
        )
        response = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a SpecTwin analysis agent. "
                        "The output must not contain any security violations. "
                        "Provide responses by removing any insecure gaps. "
                        "Return only valid JSON matching the specified schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    def _call_anthropic(self, prompt: str) -> str:
        try:
            import anthropic  # type: ignore
        except ImportError:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def _call_openai(self, prompt: str) -> str:
        try:
            import openai  # type: ignore
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a SpecTwin analysis agent. "
                        "The output must not contain any security violations. "
                        "Provide responses by removing any insecure gaps. "
                        "Return only valid JSON matching the specified schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"
