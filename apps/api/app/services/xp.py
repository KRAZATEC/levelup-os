def quest_xp(difficulty: int, estimated_minutes: int | None = None) -> int:
    base = 20 + difficulty * 15
    effort_bonus = min((estimated_minutes or 0) // 30, 4) * 5
    return base + effort_bonus


def level_from_xp(total_xp: int) -> int:
    if total_xp <= 0:
        return 1
    return max(1, int((total_xp / 100) ** (1 / 1.5)) + 1)
