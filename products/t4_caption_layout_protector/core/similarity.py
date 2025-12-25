import re
from dataclasses import dataclass
from typing import Iterable, Optional


_token_re = re.compile(r"[a-z0-9]+")


def normalize(text: str) -> str:
    return " ".join(_token_re.findall(text.lower()))


def tokenize(text: str) -> list[str]:
    return _token_re.findall(text.lower())


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            insert = curr[j - 1] + 1
            delete = prev[j] + 1
            replace = prev[j - 1] + (ca != cb)
            curr.append(min(insert, delete, replace))
        prev = curr
    return prev[-1]


def similarity_ratio(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    dist = levenshtein(a, b)
    return 1.0 - (dist / max(len(a), len(b)))


@dataclass
class MatchResult:
    candidate: str
    score: float
    method: str


def best_match(target: str, candidates: Iterable[str]) -> Optional[MatchResult]:
    normalized_target = normalize(target)
    best: Optional[MatchResult] = None
    for cand in candidates:
        norm_cand = normalize(cand)
        score = similarity_ratio(normalized_target, norm_cand)
        if best is None or score > best.score:
            best = MatchResult(candidate=cand, score=score, method="levenshtein")
    return best


def regex_match(target: str, patterns: Iterable[str]) -> Optional[str]:
    for pattern in patterns:
        if re.search(pattern, target, flags=re.IGNORECASE):
            return pattern
    return None
