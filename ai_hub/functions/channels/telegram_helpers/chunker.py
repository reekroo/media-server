from typing import Iterable

class Chunker:
    def __init__(self, soft_limit: int = 3900):
        self.soft_limit = soft_limit

    def split(self, text: str) -> Iterable[str]:
        if not text or len(text) <= self.soft_limit:
            yield text
            return

        paragraphs = text.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            if len(para) > self.soft_limit:
                if current_chunk:
                    yield current_chunk.strip()
                    current_chunk = ""

                lines = para.split('\n')
                current_para_chunk = ""
                for line in lines:
                    if len(current_para_chunk) + len(line) + 1 > self.soft_limit:
                        yield current_para_chunk.strip()
                        current_para_chunk = line
                    else:
                        current_para_chunk += '\n' + line
                if current_para_chunk:
                    yield current_para_chunk.strip()
                continue

            if len(current_chunk) + len(para) + 2 > self.soft_limit:
                yield current_chunk.strip()
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += '\n\n' + para
                else:
                    current_chunk = para

        if current_chunk:
            yield current_chunk.strip()