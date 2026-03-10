

from app.services.sm2 import calculate_sm2

def test_first_correct_answer():
    result = calculate_sm2(quality=4, repetitions=0, ease_factor=2.5, interval=0)
    assert result["interval"] == 1
    assert result["repetitions"] == 1

def test_second_correct_answer():
    result = calculate_sm2(quality=5, repetitions=1, ease_factor=2.5, interval=0)
    assert result["interval"] == 6
    assert result["repetitions"] == 2

def test_first_incorrect_answer():
    result = calculate_sm2(quality=1, repetitions= 1, ease_factor=5, interval=0)
    assert result["interval"] == 1
    assert result["repetitions"] == 0

def test_ease_factor_minimum():
    result = calculate_sm2(quality=0, repetitions=4, ease_factor=1.3, interval=10)
    assert result["interval"] == 1
    assert result["repetitions"] == 0
    assert result["ease_factor"] == 1.3

