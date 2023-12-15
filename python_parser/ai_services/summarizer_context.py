from dataclasses import dataclass


@dataclass
class OpenAIReturnContext:
    prompt_tokens: int
    completion_tokens: int
    summary: str | None
