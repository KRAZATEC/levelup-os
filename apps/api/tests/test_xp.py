from app.services.xp import level_from_xp, quest_xp


def test_quest_xp_scales_with_difficulty_and_effort():
    assert quest_xp(1, 30) == 40
    assert quest_xp(5, 120) == 115


def test_level_starts_at_one():
    assert level_from_xp(0) == 1
    assert level_from_xp(99) == 1


def test_level_increases_with_xp():
    assert level_from_xp(100) == 2
    assert level_from_xp(1000) > 2
