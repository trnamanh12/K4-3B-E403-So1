import hashlib
import re
import unicodedata

import httpx
import tiktoken
from tokenizers import Tokenizer

from .config import Settings


def normalize(text):
    return unicodedata.normalize("NFC", text).replace("\x00", "").strip()


def lexical_tokens(text):
    return re.findall(r"\w+(?:[-_./]\w+)*", normalize(text).lower())


class TokenCounter:
    def __init__(self, settings: Settings):
        self.name = settings.tokenizer
        if self.name == "auto":
            if settings.embedding_model.startswith("liquid/lfm-2.5-embedding"):
                self.name = "hf:LiquidAI/LFM2.5-Embedding-350M"
            elif settings.embedding_model.startswith("openai/"):
                self.name = "cl100k_base"
            else:
                self.name = "bytes"
        self.encoder = None
        self.fingerprint = self.name
        if self.name.startswith("hf:"):
            repo = self.name[3:]
            if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
                raise ValueError("Use RAG_TOKENIZER=hf:owner/model")
            path = settings.artifacts_dir / "tokenizers" / (repo.replace("/", "--") + ".json")
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                response = httpx.get(f"https://huggingface.co/{repo}/resolve/main/tokenizer.json",
                                     follow_redirects=True, timeout=60)
                response.raise_for_status()
                # Parse data only: no model code or trust_remote_code is executed.
                Tokenizer.from_str(response.text)
                temp = path.with_suffix(".tmp")
                temp.write_bytes(response.content)
                temp.replace(path)
            self.encoder = Tokenizer.from_file(str(path))
            self.encoder.no_truncation()
            self.encoder.no_padding()
            self.fingerprint += ":" + hashlib.sha256(path.read_bytes()).hexdigest()
        elif self.name != "bytes":
            self.encoder = tiktoken.get_encoding(self.name)

    def count(self, text):
        if self.name.startswith("hf:"):
            return len(self.encoder.encode(text, add_special_tokens=True).ids)
        if self.name == "bytes":
            return len(text.encode("utf-8"))
        return len(self.encoder.encode(text, disallowed_special=()))

    def end_within(self, text, start, budget):
        low, high = start, len(text)
        while low < high:
            mid = (low + high + 1) // 2
            if self.count(text[start:mid]) <= budget:
                low = mid
            else:
                high = mid - 1
        return low

    def truncate(self, text, budget):
        return text[:self.end_within(text, 0, budget)]


def split_spans(text, counter, budget, overlap):
    """Character spans into canonical text; never split Unicode bytes or lose a suffix."""
    start = 0
    while start < len(text):
        end = counter.end_within(text, start, budget)
        if end <= start:
            raise ValueError("Chunk budget cannot fit one character")
        if end < len(text):
            boundaries = list(re.finditer(r"(?<=[.!?])\s+|\n+|\s+", text[start:end]))
            candidates = [start + m.end() for m in boundaries if m.end() > (end-start) * .55]
            if candidates:
                end = candidates[-1]
        a, b = start, end
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b-1].isspace():
            b -= 1
        if a < b:
            yield a, b
        if end == len(text):
            break
        if overlap:
            new_start = end
            for match in reversed(list(re.finditer(r"\S+", text[start:end]))):
                candidate = start + match.start()
                if counter.count(text[candidate:end]) > overlap:
                    break
                new_start = candidate
            start = max(start + 1, new_start)
        else:
            start = end
