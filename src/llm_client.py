from __future__ import annotations

import os
from typing import List, Dict
from pydantic import BaseModel, Field
from openai import OpenAI


class ChunkAnalysis(BaseModel):
    topic: str = Field(..., description="Short topic label for this chunk")
    sentiment: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score in [-1, 1]")
    rationale: str = Field(..., description="Brief rationale for the score")


SYSTEM_PROMPT = (
    "You analyze earnings call transcript chunks. For each chunk, return: "
    "a concise topic label summarizing the main theme, and a sentiment score in [-1, 1]. "
    "The score should reflect positive vs negative tone regarding company performance, outlook, risks, and opportunities. "
    "Avoid lexical heuristics; base your judgment on the described outcomes and tone. Keep rationale short."
)

USER_PROMPT_TEMPLATE = (
    "Transcript chunk:\n\n{chunk}\n\n"
    "Return strict JSON with keys: topic, sentiment, rationale."
)


class LLMClient:
    def __init__(self, model: str | None = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Add it to your environment or .env file.")
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def analyze_chunks(self, chunks: List[str]) -> List[ChunkAnalysis]:
        results: List[ChunkAnalysis] = []
        for chunk in chunks:
            user_prompt = USER_PROMPT_TEMPLATE.format(chunk=chunk.strip())
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            try:
                from json import loads

                data: Dict = loads(content)
                results.append(ChunkAnalysis(**data))
            except Exception as exc:
                results.append(
                    ChunkAnalysis(
                        topic="Uncategorized",
                        sentiment=0.0,
                        rationale=f"Parsing error: {exc}. Raw: {content[:200]}",
                    )
                )
        return results