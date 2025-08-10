from __future__ import annotations

import argparse
from pathlib import Path
from dotenv import load_dotenv

from .pipeline import PipelineConfig, run_pipeline
from .report import generate_treemap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Earnings Call Sentiment Reporter")
    parser.add_argument("--input", required=True, type=Path, help="Path to transcript .txt file")
    parser.add_argument("--wpm", type=int, default=155, help="Words per minute estimate")
    parser.add_argument("--model", type=str, default=None, help="OpenAI model to use")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/workspace/reports/report.html"),
        help="Output HTML path",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    cfg = PipelineConfig(input_path=args.input, words_per_minute=args.wpm, model=args.model)
    df = run_pipeline(cfg)

    if df.empty:
        raise SystemExit("No data produced from transcript.")

    output_path = generate_treemap(df, args.output)
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    main()