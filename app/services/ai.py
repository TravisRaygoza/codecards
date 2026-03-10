import json

import anthropic
from fastapi import HTTPException

from app.config import ai_settings
from app.api.schemas.ai import GenerateCardsRequest, GeneratedCard

client = anthropic.Anthropic(api_key=ai_settings.ANTHROPIC_API_KEY)


async def generate_cards(request: GenerateCardsRequest) -> list[GeneratedCard]:
    """Use Claude to generate flashcards based on the request parameters."""

    prompt = f"""Generate {request.count} flashcards for studying programming.

Topic: {request.topic.value}
Programming Language: {request.language.value}
Card Type: {request.card_type.value}
Difficulty: {request.difficulty}/5

Rules:
- Each card should have a clear "front" (the question) and "back" (the answer)
- If the card type is "code", include a "code_template" field with example code
- If the card type is "qa", set "code_template" to null
- Keep questions concise but specific
- Answers should be thorough but not overly long
- Match the difficulty level (1=beginner, 5=expert)
- Set the "difficulty" field to {request.difficulty}

Return ONLY a JSON array of objects with these exact fields:
[
  {{
    "front": "...",
    "back": "...",
    "code_template": "..." or null,
    "difficulty": {request.difficulty}
  }}
]

Return ONLY the JSON array, no other text."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        # Parse the response
        response_text = message.content[0].text

        # Try to parse as JSON
        cards_data = json.loads(response_text)

        # Validate each card
        cards = [GeneratedCard(**card) for card in cards_data]

        return cards

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="AI returned invalid format. Please try again.",
        )
    except anthropic.APIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}",
        )
