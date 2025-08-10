# Earnings Call Sentiment Analysis

This project analyzes an earnings call transcript to:

- Extract key topics discussed
- Assign a sentiment score to each topic using an LLM (no lexical methods)
- Estimate time spent on each topic
- Generate an interactive treemap heatmap report (size = time, color = sentiment)

The report is exported as `report.html` in the `reports/` folder.

## Setup

1. Python 3.10+
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key in environment:

- Create `.env` in the project root with:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

You can override `OPENAI_MODEL` via CLI flag.

## Usage

```bash
python -m src.cli --input data/sample_transcript.txt --wpm 155 --model gpt-4o-mini
```

- `--input`: path to transcript `.txt`
- `--wpm`: average words per minute to estimate time (default 155)
- `--model`: OpenAI model name

The script will:

1. Chunk the transcript by paragraphs.
2. Ask the LLM to extract a topic and sentiment score in [-1, 1] per chunk.
3. Aggregate time per topic from word counts and speaking rate.
4. Generate a treemap heatmap saved to `reports/report.html`.

## Notes

- No lexical sentiment dictionary is used. All sentiment is inferred by the LLM.
- If all sentiment scores are non-negative, the color scale is adjusted to show neutral→positive only.
- The output includes a color legend and hover details per topic.
