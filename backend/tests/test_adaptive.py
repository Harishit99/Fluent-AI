from app.services.adaptive_learning.engine import AdaptiveLearningEngine


def test_adaptive_smoothing_and_progression():
    # Smoothing test: single 100% test does not jump CEFR level prematurely when attempts are low
    update1 = AdaptiveLearningEngine.smooth_skill_update(
        current_level="A2",
        current_accuracy=60.0,
        total_attempts=1,
        latest_score=100.0,
    )
    assert update1["estimated_level"] == "A2"
    assert update1["accuracy_percentage"] == 70.0  # 60*0.75 + 100*0.25 = 45 + 25 = 70.0

    # Sustained high accuracy across >= 5 attempts promotes level to B1
    update_high = AdaptiveLearningEngine.smooth_skill_update(
        current_level="A2",
        current_accuracy=90.0,
        total_attempts=5,
        latest_score=95.0,
    )
    assert update_high["estimated_level"] == "B1"


def test_supermemo_srs_spacing():
    # Perfect recall (rating 5)
    srs1 = AdaptiveLearningEngine.calculate_srs_next_review(
        rating=5,
        repetition_count=0,
        interval_days=1,
        ease_factor=2.5,
    )
    assert srs1["repetition_count"] == 1
    assert srs1["interval_days"] == 1

    srs2 = AdaptiveLearningEngine.calculate_srs_next_review(
        rating=5,
        repetition_count=1,
        interval_days=1,
        ease_factor=2.5,
    )
    assert srs2["repetition_count"] == 2
    assert srs2["interval_days"] == 3

    # Failed recall (rating 1) resets interval to 1 day
    srs_fail = AdaptiveLearningEngine.calculate_srs_next_review(
        rating=1,
        repetition_count=3,
        interval_days=7,
        ease_factor=2.5,
    )
    assert srs_fail["repetition_count"] == 0
    assert srs_fail["interval_days"] == 1
