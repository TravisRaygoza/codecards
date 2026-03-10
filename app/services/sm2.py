"""
SM-2 Spaced Repetition Algorithm

Quality ratings (0-5):
  0 - Complete blackout, no recall at all
  1 - Wrong answer, but recognized the correct one
  2 - Wrong answer, but it felt familiar
  3 - Correct answer, but with serious difficulty
  4 - Correct answer, with some hesitation
  5 - Perfect recall, no hesitation

How it works:
  - If quality >= 3: correct answer → increase interval
  - If quality < 3: wrong answer → reset to beginning
  - ease_factor adjusts how fast intervals grow (minimum 1.3)
  - interval is the number of days until next review
"""

from datetime import datetime, timedelta, timezone


def calculate_sm2(
    quality: int,
    repetitions: int,
    ease_factor: float,
    interval: int,
) -> dict:
    """
    Calculate next review schedule using SM-2 algorithm.

    Args:
        quality: 0-5 rating of how well the user knew the answer
        repetitions: how many times they've gotten it right in a row
        ease_factor: how easy this card is for them (starts at 2.5)
        interval: current interval in days

    Returns:
        dict with new repetitions, ease_factor, interval, and next_review
    """

    # Correct answer (quality >= 3)
    if quality >= 3:
        if repetitions == 0:
            interval = 1          # first correct → review tomorrow
        elif repetitions == 1:
            interval = 6          # second correct → review in 6 days
        else:
            interval = round(interval * ease_factor)  # after that, multiply

        repetitions += 1

    # Wrong answer (quality < 3)
    else:
        repetitions = 0           # reset streak
        interval = 1              # review tomorrow

    # Update ease factor (how easy this card is)
    # Formula from the SM-2 paper
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Ease factor can't go below 1.3
    if ease_factor < 1.3:
        ease_factor = 1.3

    # Calculate next review date
    next_review = datetime.now(timezone.utc) + timedelta(days=interval)

    return {
        "repetitions": repetitions,
        "ease_factor": round(ease_factor, 2),
        "interval": interval,
        "next_review": next_review,
    }
