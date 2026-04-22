from dataclasses import dataclass
from datetime import date, timedelta


LEVEL_THRESHOLDS = [
    (5, 400),
    (4, 250),
    (3, 120),
    (2, 50),
    (1, 0),
]


MOTIVATIONS = [
    "今天推进一章，就比昨天更清楚一点。",
    "连续学习比一次学很多更厉害。",
    "你已经在稳定积累了。",
    "再完成一章，进度条就更好看了。",
]


@dataclass
class RewardResult:
    xp_gained: int
    streak: int
    reached_seven_day_bonus: bool


def level_from_xp(total_xp: int) -> int:
    for level, threshold in LEVEL_THRESHOLDS:
        if total_xp >= threshold:
            return level
    return 1


def next_level_gap(total_xp: int) -> int:
    level = level_from_xp(total_xp)
    if level >= 5:
        return 0
    next_threshold = dict(LEVEL_THRESHOLDS)[level + 1]
    return max(next_threshold - total_xp, 0)


def apply_daily_streak(last_log_date: date | None, today: date) -> tuple[int, int]:
    if not last_log_date:
        return 1, 5
    if last_log_date == today:
        return 0, 0
    if last_log_date == today - timedelta(days=1):
        return 1, 5
    return -1, 5


def reward_for_unit_completion(
    current_streak: int, last_log_date: date | None, today: date
) -> RewardResult:
    base = 10
    streak_delta, daily_bonus = apply_daily_streak(last_log_date, today)

    if streak_delta == 1:
        new_streak = current_streak + 1
    elif streak_delta == -1:
        new_streak = 1
    else:
        new_streak = current_streak

    seven_day_bonus = new_streak > 0 and new_streak % 7 == 0 and streak_delta != 0
    xp = base + daily_bonus + (30 if seven_day_bonus else 0)
    return RewardResult(xp_gained=xp, streak=new_streak, reached_seven_day_bonus=seven_day_bonus)
