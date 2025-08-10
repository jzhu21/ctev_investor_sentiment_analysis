from __future__ import annotations

import argparse
from pathlib import Path
from dotenv import load_dotenv

from .pipeline import PipelineConfig, run_pipeline
from .report import generate_treemap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze earnings call transcript sentiment.")
    parser.add_argument("--input", type=Path, required=True, help="Path to transcript file (e.g., data/ctev_transcript_2025Q2.txt)")
    parser.add_argument("--output", type=Path, default=Path("reports/report.html"), help="Output HTML path")
    parser.add_argument("--wpm", type=int, default=155, help="Words per minute (default: 155)")
    parser.add_argument("--model", type=str, default=None, help="OpenAI model to use")
    parser.add_argument("--max-topics", type=int, default=10, help="Maximum number of topics to display (default: 10)")
    parser.add_argument("--custom-topics", type=str, nargs="+", help="Custom topics to analyze (space-separated)")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    cfg = PipelineConfig(
        input_path=args.input, 
        words_per_minute=args.wpm, 
        model=args.model,
        max_topics=args.max_topics,
        custom_topics=args.custom_topics
    )
    df = run_pipeline(cfg)

    if df.empty:
        raise SystemExit("No data produced from transcript.")

    # Read transcript text for highlighting
    transcript_text = args.input.read_text(encoding="utf-8")
    
    output_path = generate_treemap(df, args.output, transcript_text)
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    main()