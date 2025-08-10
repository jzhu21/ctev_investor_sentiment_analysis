from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from .llm_client import LLMClient, ChunkAnalysis


@dataclass
class PipelineConfig:
    input_path: Path
    words_per_minute: int = 155
    model: str | None = None


def read_transcript(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def split_into_chunks(text: str, max_words: int = 180) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    for p in paragraphs:
        words = p.split()
        for i in range(0, len(words), max_words):
            segment = " ".join(words[i : i + max_words])
            if segment:
                chunks.append(segment)
    return chunks


def estimate_minutes(word_count: int, wpm: int) -> float:
    return word_count / max(wpm, 1)


def run_pipeline(config: PipelineConfig) -> pd.DataFrame:
    text = read_transcript(config.input_path)
    chunks = split_into_chunks(text)

    client = LLMClient(model=config.model)
    analyses: List[ChunkAnalysis] = client.analyze_chunks(chunks)

    records = []
    for chunk, analysis in zip(chunks, analyses):
        words = len(chunk.split())
        minutes = estimate_minutes(words, config.words_per_minute)
        records.append(
            {
                "topic": analysis.topic.strip()[:60],
                "sentiment": float(analysis.sentiment),
                "minutes": minutes,
                "words": words,
                "rationale": analysis.rationale,
            }
        )

    df = pd.DataFrame(records)
    if df.empty:
        return df

    # Aggregate by topic
    agg = (
        df.groupby("topic", as_index=False)
        .agg({"sentiment": "mean", "minutes": "sum", "words": "sum"})
        .sort_values("minutes", ascending=False)
    )
    # Normalize and keep useful ordering
    agg["sentiment"] = agg["sentiment"].clip(-1, 1)
    return agg