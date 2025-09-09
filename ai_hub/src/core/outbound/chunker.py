from __future__ import annotations
from typing import Iterable

class Chunker:
    def __init__(self, soft_limit: int) -> None:
        self.soft_limit = soft_limit

    def split(self, text: str) -> Iterable[str]:
        size = self.soft_limit
        if not text:
            return
        def join_pars(buf: list[str]) -> str:
            return "\n\n".join(buf)

        pars = text.split("\n\n")
        buf: list[str] = []

        for p in pars:
            if len(p) <= size:
                candidate = (join_pars(buf) + ("\n\n" if buf else "") + p) if buf else p
                if len(candidate) <= size:
                    buf.append(p)
                else:
                    if buf:
                        yield join_pars(buf)
                    buf = [p]
                continue

            if buf:
                yield join_pars(buf)
                buf = []

            lines = p.split("\n")
            current = ""
            for line in lines:
                if not current:
                    current = line
                elif len(current) + 1 + len(line) <= size:
                    current += "\n" + line
                else:
                    if current:
                        yield current
                    start = 0
                    n = len(line)
                    while start < n:
                        end = min(start + size, n)
                        cut = line.rfind(" ", start, end)
                        if cut == -1 or cut <= start:
                            cut = end
                        yield line[start:cut]
                        start = cut + (1 if cut < n and line[cut:cut + 1] == " " else 0)
                    current = ""
            if current:
                yield current

        if buf:
            out = "\n\n".join(buf)
            if len(out) <= size:
                yield out
            else:
                start = 0
                n = len(out)
                while start < n:
                    end = min(start + size, n)
                    cut = out.rfind("\n", start, end)
                    if cut == -1 or cut <= start:
                        cut = end
                    yield out[start:cut]
                    start = cut
