# oleds/displays/ui/trend.py
from __future__ import annotations
from collections import deque
from typing import List, Sequence

class Trend:
    def __init__(self, n_series: int, history: int = 120, alpha: float = 0.3, decay: float = 0.90):
        self.n = int(max(1, n_series))
        self.hist = [deque(maxlen=history) for _ in range(self.n)]
        self.ema  = [None] * self.n
        self.scale = 1.0
        self.alpha = max(0.0, min(1.0, float(alpha)))
        self.decay = max(0.0, min(1.0, float(decay)))

    def update(self, values: Sequence[float]) -> List[Sequence[float]]:
        vs = [float(v) if v is not None else 0.0 for v in (list(values) + [0.0] * self.n)[:self.n]]

        for i, v in enumerate(vs):
            if self.ema[i] is None: self.ema[i] = v
            self.ema[i] = self.alpha * v + (1.0 - self.alpha) * self.ema[i]
            self.hist[i].append(self.ema[i])

        local_max = max(max(h or [0.0]) for h in self.hist)
        local_max = max(local_max, 1.0)
        self.scale = max(local_max, self.scale * self.decay)

        s = max(self.scale, 1.0)
        norm = []
        for h in self.hist:
            norm.append([min(100.0, 100.0 * v / s) for v in h])
        
        return norm