from __future__ import annotations

import os
from typing import List, Dict
from pydantic import BaseModel, Field
from openai import OpenAI


class ChunkAnalysis(BaseModel):
    topic: str = Field(..., description="Short topic label for this chunk")
    sentiment: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score in [-1, 1]")
    rationale: str = Field(..., description="Brief rationale for the score")


class TopicAnalysis(BaseModel):
    topic: str = Field(..., description="High-level topic category")
    sentiment: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score in [-1, 1]")
    minutes: float = Field(..., description="Estimated time spent on this topic")
    words: int = Field(..., description="Estimated word count for this topic")
    rationale: str = Field(..., description="Brief rationale for the sentiment score")


class FullTranscriptAnalysis(BaseModel):
    topics: List[TopicAnalysis] = Field(..., description="List of major topics with sentiment and time estimates")


SYSTEM_PROMPT = (
    "You analyze earnings call transcripts to identify major themes and estimate time spent on each. "
    "Return a list of 5-10 major topics that were discussed, with sentiment scores and time estimates.\n\n"
    "Use these high-level topic categories:\n"
    "- Financial Performance (revenue, earnings, margins, growth)\n"
    "- Business Operations (operations, efficiency, processes)\n"
    "- Market & Competition (market share, competitive position)\n"
    "- Strategy & Vision (long-term plans, strategic initiatives)\n"
    "- Risk & Challenges (risks, headwinds, challenges)\n"
    "- Growth & Expansion (new markets, products, acquisitions)\n"
    "- Customer & Demand (customer behavior, demand trends)\n"
    "- Regulatory & Compliance (regulatory issues, compliance)\n"
    "- Technology & Innovation (R&D, new technologies)\n"
    "- Management & Leadership (executive changes, leadership)\n\n"
    "For each topic, estimate the percentage of the call spent on it and convert to minutes. "
    "Provide sentiment scores reflecting positive vs negative tone regarding company performance, outlook, risks, and opportunities."
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

    def analyze_full_transcript(self, transcript: str, wpm: int) -> FullTranscriptAnalysis:
        """Analyze the full transcript to extract major themes and time estimates."""
        total_words = len(transcript.split())
        total_minutes = total_words / wpm
        
        user_prompt = (
            f"Transcript (total: {total_words} words, approximately {total_minutes:.1f} minutes):\n\n"
            f"{transcript[:8000]}...\n\n"  # Limit to first 8000 chars to avoid token limits
            "Return strict JSON with a 'topics' array. Each topic should have: topic, sentiment (-1 to 1), "
            f"minutes (estimated time spent, total should sum to approximately {total_minutes:.1f}), "
            "words (estimated word count), and rationale."
        )
        
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
            return FullTranscriptAnalysis(**data)
        except Exception as exc:
            # Fallback: create a basic analysis
            return FullTranscriptAnalysis(topics=[
                TopicAnalysis(
                    topic="Full Transcript Analysis",
                    sentiment=0.0,
                    minutes=total_minutes,
                    words=total_words,
                    rationale=f"Analysis error: {exc}. Raw: {content[:200]}"
                )
            ])

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

    def analyze_with_custom_topics(self, transcript: str, custom_topics: List[str], wpm: int) -> FullTranscriptAnalysis:
        """Analyze transcript using predefined custom topics."""
        total_words = len(transcript.split())
        total_minutes = total_words / wpm
        
        # Create a more focused prompt for custom topics
        custom_topics_text = "\n".join([f"- {topic}" for topic in custom_topics])
        
        system_prompt = f"""You analyze earnings call transcripts using predefined topics. Your task is to:
1. Categorize transcript content into these EXACT topics: {custom_topics_text}
2. Assign sentiment scores (-1 to +1) for each topic based on content
3. Estimate time spent on each topic (in minutes)
4. Provide brief rationale for sentiment scores

Return strict JSON with a 'topics' array. Each topic must match one of the predefined topics exactly.
If a predefined topic has no relevant content, assign 0 sentiment and 0 minutes."""
        
        user_prompt = (
            f"Transcript (total: {total_words} words, approximately {total_minutes:.1f} minutes):\n\n"
            f"{transcript[:8000]}...\n\n"
            f"Analyze using ONLY these topics: {custom_topics_text}\n\n"
            "Return strict JSON with a 'topics' array. Each topic should have: topic, sentiment (-1 to 1), "
            f"minutes (estimated time spent, total should sum to approximately {total_minutes:.1f}), "
            "words (estimated word count), and rationale."
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,  # Lower temperature for more consistent topic matching
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        try:
            from json import loads
            data: Dict = loads(content)
            return FullTranscriptAnalysis(**data)
        except Exception as exc:
            # Fallback: create analysis with custom topics but neutral sentiment
            fallback_topics = []
            for topic in custom_topics:
                fallback_topics.append(TopicAnalysis(
                    topic=topic,
                    sentiment=0.0,
                    minutes=total_minutes / len(custom_topics),
                    words=total_words // len(custom_topics),
                    rationale=f"Analysis error: {exc}. Using fallback values."
                ))
            return FullTranscriptAnalysis(topics=fallback_topics)