import time
from pandanite.core.constants import DECIMAL_SCALE_FACTOR, MIN_DIFFICULTY
from pandanite.core.common import TransactionAmount


def get_current_time():
    return int(1000 * time.time())


def PDN(amount: float) -> TransactionAmount:
    return TransactionAmount(amount * DECIMAL_SCALE_FACTOR)


def compute_difficulty(
    current_difficulty: int, elapsed_time: int, expected_time: int
) -> int:
    new_difficulty = current_difficulty

    if elapsed_time > expected_time:
        k = 2
        last_k = 1
        while new_difficulty > MIN_DIFFICULTY:
            if abs(elapsed_time // k - expected_time) > abs(
                elapsed_time // last_k - expected_time
            ):
                break
            new_difficulty -= 1
            last_k = k
            k *= 2
        return new_difficulty
    else:
        k = 2
        last_k = 1
        while new_difficulty < 254:
            if abs(elapsed_time * k - expected_time) > abs(
                elapsed_time * last_k - expected_time
            ):
                break
            new_difficulty += 1
            last_k = k
            k *= 2
        return new_difficulty
