from typing import Iterable, Tuple

class Chunker:
    def __init__(self, soft_limit: int = 4000):
        if soft_limit <= 0:
            raise ValueError("soft_limit must be positive")
        self.soft_limit = soft_limit

    def _find_best_split_pos(self, text: str, start_offset: int) -> int:

        end_offset = start_offset + self.soft_limit
        
        para_split_pos = text.rfind('\n\n', start_offset, end_offset)
        if para_split_pos > start_offset:
            return para_split_pos

        line_split_pos = text.rfind('\n', start_offset, end_offset)
        if line_split_pos > start_offset:
            return line_split_pos
        
        return end_offset

    def split(self, text: str) -> Iterable[str]:
        if not text:
            return
        for chunk, offset in self.split_with_offsets(text):
            yield chunk

    def split_with_offsets(self, text: str) -> Iterable[Tuple[str, int]]:
        if not text:
            return

        text_len = len(text)
        current_offset = 0
        
        while current_offset < text_len:
            if text_len - current_offset <= self.soft_limit:
                yield text[current_offset:], current_offset
                break

            split_pos = self._find_best_split_pos(text, current_offset)
            
            chunk = text[current_offset:split_pos]
            yield chunk, current_offset

            current_offset = split_pos
            while current_offset < text_len and text[current_offset].isspace():
                current_offset += 1