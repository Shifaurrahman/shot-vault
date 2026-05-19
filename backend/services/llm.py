"""
LLM Service — Claude Answer Generation
────────────────────────────────────────
After vector search returns top-K shots,
Claude reads those shots and generates a natural language answer.

Flow:
  User query: "what is an extreme wide shot?"
       ↓
  Vector search → top-K matched shots (title, desc, shot_type…)
       ↓
  Claude reads the shots as context
       ↓
  Claude answers: "An extreme wide shot (EWS) is used to show the
  subject within a vast environment. In your database, you have a
  beach scene shot at golden hour showing this technique…"
       ↓
  UI shows: Claude's answer + matched shot cards with images/videos
"""

import anthropic
from config import get_settings
from models.schemas import ShotResult
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    def __init__(self):
        if not settings.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not set — LLM answers disabled.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            logger.info(f"Anthropic client ready — model: {settings.anthropic_model}")

    def generate_answer(
        self,
        query: str,
        results: list[ShotResult],
    ) -> str:
        """
        Given the user query and retrieved shots,
        generate a helpful natural language answer using Claude.

        Returns a plain string answer.
        Falls back gracefully if API key is missing.
        """
        if not self.client:
            return ""

        if not results:
            # No matching shots — Claude answers from general knowledge
            context = "No matching shots were found in the database."
        else:
            # Build context from retrieved shots
            context_lines = []
            for i, r in enumerate(results, 1):
                line = f"[Shot {i}] Title: \"{r.title}\""
                if r.shot_type:
                    line += f" | Type: {r.shot_type}"
                line += f" | Description: {r.description}"
                if r.tags:
                    line += f" | Tags: {', '.join(r.tags)}"
                if r.media_type:
                    line += f" | Media: {r.media_type}"
                context_lines.append(line)

            context = "\n".join(context_lines)

        system_prompt = """You are ShotVault, an expert filmmaking assistant.
You help filmmakers understand shot types, cinematography techniques, and find relevant shots from their knowledge base.

When answering:
- Be concise and practical (2-4 sentences max)
- Reference the specific shots from the database when relevant
- Use proper filmmaking terminology
- If no shots match, still answer the question from general filmmaking knowledge"""

        user_message = f"""User query: "{query}"

Relevant shots from the database:
{context}

Answer the user's query. If relevant shots exist, mention them naturally in your answer."""

        try:
            response = self.client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )
            answer = response.content[0].text.strip()
            logger.info(f"LLM answer generated for query: '{query}'")
            return answer

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""


# Singleton
llm_service = LLMService()