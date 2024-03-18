"""Timer."""

import time


class Timer:
    """Timer class."""

    def __init__(self) -> None:
        """Timer."""
        self.reset()

    @property
    def total(self):
        """Total time."""
        return self._total

    @property
    def average(self):
        """Average time."""
        denom = max(self._step, 1)
        return self._total / denom

    def reset(self):
        """Reset variables."""
        self._t_start = None
        self._running = False
        self._total = 0
        self._step = 0

    def start(self):
        """Start timer."""
        self._t_start = time.perf_counter()
        self._running = True

    def stop(self):
        """Stop timer."""
        self._total += self._elapsed()
        self._t_start = None
        self._running = False

    def pause(self):
        """Pause timer."""
        if self._running:
            self._total += self._elapsed()
            self._running = False

    def resume(self):
        """Resume paused timer."""
        if not self._running:
            self._t_start = time.perf_counter()
            self._running = True

    def step(self):
        """Step."""
        self._step += 1

    def _elapsed(self):
        """Delta."""
        return time.perf_counter() - self._t_start
