from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional
from dotenv import load_dotenv

import pandas as pd

from .llm_client import LLMClient, ChunkAnalysis

# Load environment variables
load_dotenv()


@dataclass
class PipelineConfig:
    input_path: Path
    words_per_minute: int = 155
    model: str = "gpt-5"
    max_topics: int = 10
    custom_topics: Optional[List[str]] = None


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
    """Run the sentiment analysis pipeline."""
    text = config.input_path.read_text(encoding="utf-8")
    
    client = LLMClient(model=config.model)
    
    if config.custom_topics:
        # Use custom topics defined by user
        analysis = client.analyze_with_custom_topics(text, config.custom_topics, config.words_per_minute)
    else:
        # Use AI-generated topics
        analysis = client.analyze_full_transcript(text, config.words_per_minute)
    
    # Convert to DataFrame
    records = []
    for topic_analysis in analysis.topics:
        records.append({
            "topic": topic_analysis.topic,
            "sentiment": topic_analysis.sentiment,
            "minutes": topic_analysis.minutes,
            "words": topic_analysis.words,
            "rationale": topic_analysis.rationale,
        })
    
    df = pd.DataFrame(records)
    
    if df.empty:
        return df
    
    # Sort by time spent and limit topics
    df = df.sort_values("minutes", ascending=False)
    if len(df) > config.max_topics:
        df = df.head(config.max_topics)
    
    return df