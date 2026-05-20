"""
LLM Service — Answer Generation
─────────────────────────────────
Supports three providers, switched via LLM_PROVIDER in .env:

  anthropic → Claude (Anthropic API)
  openai    → GPT (OpenAI API)
  local     → LM Studio / Ollama (OpenAI-compatible local server)

No code changes needed to switch — just edit .env and restart.

Flow:
  User query: "what is an extreme wide shot?"
       ↓
  Vector search → top-K matched shots
       ↓
  LLM reads shots as context
       ↓
  LLM answers in natural language
       ↓
  UI shows answer + matched shot cards
"""

import anthropic
import openai
from config import get_settings
from models.schemas import ShotResult
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def _build_context(results: list[ShotResult]) -> str:
    """Build context string from retrieved shots."""
    if not results:
        return "No matching shots were found in the database."

    lines = []
    for i, r in enumerate(results, 1):
        line = f"[Shot {i}] Title: \"{r.title}\""
        if r.shot_type:
            line += f" | Type: {r.shot_type}"
        line += f" | Description: {r.description}"
        if r.tags:
            line += f" | Tags: {', '.join(r.tags)}"
        if r.media_type:
            line += f" | Media: {r.media_type}"
        lines.append(line)

    return "\n".join(lines)


SYSTEM_PROMPT = """You are ShotVault, an expert filmmaking assistant.
You help filmmakers understand shot types, cinematography techniques, and find relevant shots from their knowledge base.

When answering:
- Be concise and practical (2-4 sentences max)
- Reference the specific shots from the database when relevant
- Use proper filmmaking terminology
- If no shots match, still answer the question from general filmmaking knowledge"""


def _build_user_message(query: str, context: str) -> str:
    return f"""User query: "{query}"

Relevant shots from the database:
{context}

Answer the user's query. If relevant shots exist, mention them naturally in your answer."""


class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider
        self.client = self._init_client()

    def _init_client(self):
        if self.provider == "anthropic":
            if not settings.anthropic_api_key:
                logger.warning("ANTHROPIC_API_KEY not set — LLM answers disabled.")
                return None
            logger.info(f"LLM provider: Anthropic — model: {settings.anthropic_model}")
            return anthropic.Anthropic(api_key=settings.anthropic_api_key)

        elif self.provider == "openai":
            if not settings.openai_api_key:
                logger.warning("OPENAI_API_KEY not set — LLM answers disabled.")
                return None
            logger.info(f"LLM provider: OpenAI — model: {settings.openai_model}")
            return openai.OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

        elif self.provider == "local":
            logger.info(f"LLM provider: Local ({settings.local_base_url}) — model: {settings.local_model}")
            return openai.OpenAI(
                api_key=settings.local_api_key,
                base_url=settings.local_base_url,
            )

        else:
            logger.error(f"Unknown LLM_PROVIDER: {self.provider}")
            return None

    def generate_answer(self, query: str, results: list[ShotResult]) -> str:
        """
        Generate a natural language answer from the query + retrieved shots.
        Returns empty string if client is not configured.
        """
        if not self.client:
            return ""

        context = _build_context(results)
        user_message = _build_user_message(query, context)

        try:
            if self.provider == "anthropic":
                return self._call_anthropic(user_message)
            else:
                # Both openai and local use the same OpenAI-compatible call
                return self._call_openai_compatible(user_message)

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""

    def _call_anthropic(self, user_message: str) -> str:
        response = self.client.messages.create(
            model=settings.anthropic_model,
            max_tokens=settings.anthropic_max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        answer = response.content[0].text.strip()
        logger.info("LLM answer generated (Anthropic)")
        return answer

    def _call_openai_compatible(self, user_message: str) -> str:
        model = settings.openai_model if self.provider == "openai" else settings.local_model
        max_tokens = settings.anthropic_max_tokens  # reuse same limit

        response = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        answer = response.choices[0].message.content.strip()
        logger.info(f"LLM answer generated ({self.provider})")
        return answer


# Singleton
llm_service = LLMService()