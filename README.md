# Earnings Call Sentiment Analyzer

A comprehensive tool for analyzing earnings call transcripts to extract sentiment, key topics, and insights using AI-powered analysis.

## 🏗️ Repository Structure

```
ctev_investor_sentiment_analysis/
├── src/                           # Source code
│   ├── ctev_earnings_call_analysis.py  # Main analysis script
│   ├── pipeline.py               # Analysis pipeline
│   ├── llm_client.py             # OpenAI API client
│   ├── report.py                 # Report generation
│   ├── cli.py                    # Command line interface
│   └── __init__.py               # Package initialization
├── data/                          # Transcript data
│   ├── Claritev Earnings Call Transcript 2024 Q4.txt
│   ├── Claritev Earnings Call Transcript 2025 Q1.txt
│   └── Claritev Earnings Call Transcript 2025 Q2.txt
├── output/                        # Generated outputs
│   ├── q4_2024_analysis_results.json
│   ├── q4_2024_sentiment_heatmap.png
│   ├── q1_2025_analysis_results.json
│   ├── q1_2025_sentiment_heatmap.png
│   ├── q2_2025_analysis_results.json
│   └── q2_2025_sentiment_heatmap.png
├── archive/                       # Unused/legacy files
│   ├── reports/                   # Old report files
│   ├── sentiment_treemap.py      # Old treemap implementation
│   ├── transcript_analyzer.py    # Old transcript analyzer
│   └── ...                       # Other legacy files
├── requirements.txt               # Python dependencies
├── install_dependencies.sh        # System dependencies installer
├── DEPLOYMENT_GUIDE.md           # Deployment instructions
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd ctev_investor_sentiment_analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Note: Virtual environment is not included in the repository
# Create a fresh one for each new setup to avoid conflicts
```

### Run the Application
```bash
# Run the main analysis script
python src/ctev_earnings_call_analysis.py

# Or run individual modules
python src/pipeline.py
python src/cli.py

# Run the Streamlit web app (after analysis is complete)
streamlit run streamlit_app.py

# Or use the provided script
./run_streamlit.sh
```

The script will prompt you to select an earnings call transcript to analyze.



## 📊 Features

### Core Analysis
- **Sentiment Analysis**: AI-powered sentiment scoring for each topic using GPT-5
- **Topic Extraction**: Automatic identification of key discussion areas (8-15 topics, max 2 words each)
- **Word Count Analysis**: Count of words discussed for each topic
- **Reasoning Generation**: AI explanations for each sentiment score

### Visualization
- **Sentiment Heatmap**: Squarify treemap showing topic size (word count) and color (sentiment)
- **Dynamic Color Scaling**: Automatically adjusts colorbar based on sentiment range
- **Detailed Analysis**: Comprehensive breakdown of analysis results with reasoning

### Web Application
- **Streamlit Dashboard**: Interactive web interface with separate tabs for each quarter
- **Interactive Treemaps**: Hover-like functionality using topic selectors to explore sentiment details
- **Real-time Metrics**: Key performance indicators and sentiment analysis for each quarter

## 🌐 Deployment

### Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo
4. Set main file: `streamlit_app.py`
5. Deploy!

### Other Platforms
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment options including:
- Heroku
- AWS/GCP/Azure
- Docker containers
- Local production servers
- **Responsive Design**: Modern UI with intuitive navigation and data exploration




## 🎯 Usage

### Running the Analysis
1. **Set up environment variables**: Create `.env` file with your OpenAI API key
2. **Run the main script**: `python src/ctev_earnings_call_analysis.py`
3. **Select transcript**: Choose from Q4 2024, Q1 2025, or Q2 2025
4. **View results**: Check the generated JSON and PNG files in the `output/` folder

### Output Files
- **JSON Analysis**: Detailed sentiment scores, word counts, and reasoning for each topic
- **Sentiment Heatmap**: Visual representation of topics with color-coded sentiment scores

## 🚨 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure virtual environment is activated and requirements are installed
2. **API Errors**: Verify OpenAI API key is set in `.env` file
3. **Memory Issues**: Use gpt-5 for best results, ensure sufficient API credits

## 🙏 Acknowledgments

- OpenAI for providing the GPT-5 model
- Matplotlib and Squarify for treemap visualization
- The open-source community for various supporting libraries
