"""
LLM interface voor Claude API calls.
"""
import asyncio
from typing import Optional

import anthropic

from config import ANTHROPIC_API_KEY


client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


async def call_claude(
    model: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    retries: int = 5,
) -> tuple[str, int, int]:
    """
    Roep Claude API aan.
    Returns: (response_text, input_tokens, output_tokens)
    """
    attempt = 0
    while attempt < retries:
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            text = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return text, input_tokens, output_tokens

        except anthropic.RateLimitError as e:
            attempt += 1
            if attempt >= retries:
                raise
            wait_time = 30 * attempt  # Exponential: 30, 60, 90, 120...
            print(f"Rate limit hit, waiting {wait_time}s... (attempt {attempt}/{retries})")
            await asyncio.sleep(wait_time)

        except anthropic.InternalServerError as e:
            # 529 Overloaded errors
            attempt += 1
            if attempt >= retries:
                raise
            wait_time = 15 * (2 ** (attempt - 1))  # Exponential: 15, 30, 60, 120...
            print(f"API overloaded (529), waiting {wait_time}s... (attempt {attempt}/{retries})")
            await asyncio.sleep(wait_time)

        except anthropic.APIError as e:
            attempt += 1
            if attempt >= retries:
                raise
            wait_time = 5 * attempt  # 5, 10, 15, 20...
            print(f"API error: {e}, retrying in {wait_time}s... (attempt {attempt}/{retries})")
            await asyncio.sleep(wait_time)

    raise RuntimeError("Max retries exceeded")
