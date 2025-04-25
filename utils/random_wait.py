import random
import time

def random_wait(min_seconds=0.5, max_seconds=4, log_func=None):
    """
    Sleep for a random duration between min_seconds and max_seconds.

    Args:
        min_seconds (float): Minimum seconds to wait.
        max_seconds (float): Maximum seconds to wait.
        log_func (function): Optional logging function to log the wait duration.
    """
    delay = random.uniform(min_seconds, max_seconds)
    if log_func:
        log_func(f"Waiting for {delay:.2f} seconds")
    time.sleep(delay)