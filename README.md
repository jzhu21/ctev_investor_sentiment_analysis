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
```

The script will prompt you to select an earnings call transcript to analyze.

## 🔧 Recent Fixes

### Issue 1: Heatmap "Earnings Call" Outline ✅ FIXED
- **Problem**: The treemap was showing an unnecessary "Earnings Call" root node
- **Solution**: Removed the `px.Constant("Earnings Call")` from the treemap path
- **Result**: Clean, direct topic visualization without extra hierarchy

### Issue 2: Index Numbers in Table ✅ FIXED
- **Problem**: The detailed analysis table was showing pandas index numbers
- **Solution**: Added `reset_index(drop=True)` to remove index column
- **Result**: Clean table with only relevant data columns

### Issue 3: Transcript Noise ✅ FIXED
- **Problem**: Transcript displayed with speaker labels and formatting artifacts
- **Solution**: Added `clean_transcript_text()` function to remove:
  - Speaker labels (e.g., "Travis Dalton:")
  - Bracketed text and parenthetical content
  - Multiple spaces and newlines
  - Header lines
- **Result**: Clean, readable transcript text

### Issue 4: WeasyPrint Library Error ✅ FIXED
- **Problem**: `libgobject-2.0-0` system dependency missing on macOS
- **Solution**: 
  - Graceful error handling with helpful error messages
  - Automatic fallback to HTML-only reports
  - Installation script for system dependencies
- **Result**: App works regardless of PDF generation capability

## 📊 Features

### Core Analysis
- **Sentiment Analysis**: AI-powered sentiment scoring for each topic
- **Topic Extraction**: Automatic identification of key discussion areas
- **Time Analysis**: Estimate time spent on each topic based on word count
- **Rationale Generation**: AI explanations for sentiment scores

### Visualization
- **Sentiment Heatmap**: Interactive squarify treemap showing topic size (time) and color (sentiment)
- **Detailed Tables**: Comprehensive breakdown of analysis results
- **Transcript Highlighting**: Negative sentiment sentences highlighted for quick review

### Export Options
- **HTML Reports**: Self-contained reports with interactive visualizations
- **PDF Reports**: Professional reports for presentations (requires system dependencies)

## 🛠️ System Dependencies

### For PDF Generation (Optional)
If you want to generate PDF reports, install system dependencies:

#### macOS
```bash
# Run the automated installer
./install_dependencies.sh

# Or manually install with Homebrew
brew install cairo pango gdk-pixbuf libffi
```

#### Ubuntu/Debian
```bash
sudo apt-get install libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev
```

#### CentOS/RHEL
```bash
sudo yum install cairo-devel pango-devel gdk-pixbuf2-devel libffi-devel
```

### Alternative: Docker
If you prefer to avoid system dependencies, use the provided Dockerfile:
```bash
docker build -t sentiment-analyzer .
docker run -p 8501:8501 sentiment-analyzer
```

## 📁 Project Structure

```
ctev_investor_sentiment_analysis/
├── data/                          # Sample transcript data
├── src/                           # Core analysis modules
│   ├── pipeline.py               # Main analysis pipeline
│   ├── llm_client.py            # OpenAI API client
│   └── report.py                # Report generation
├── streamlit_app.py              # Web application
├── requirements.txt              # Python dependencies
├── install_dependencies.sh       # System dependency installer
├── DEPLOYMENT_GUIDE.md          # Detailed deployment instructions
└── README.md                    # This file
```

## 🎯 Usage

### 1. Upload Transcript
- Support for `.txt` and `.docx` files
- Use the sample transcript for testing

### 2. Configure Analysis
- **Model Selection**: Choose OpenAI model (gpt-5 recommended for accuracy)
- **WPM Setting**: Adjust speaking speed for time calculations
- **Max Topics**: Control number of topics to analyze
- **Custom Topics**: Define specific topics of interest

### 3. Run Analysis
- Click "Run Report" to start analysis
- View results in interactive visualizations
- Download reports in HTML or PDF format

### 4. Interpret Results
- **Sentiment Scores**: -1.0 (very negative) to +1.0 (very positive)
- **Topic Size**: Represents time spent discussing each topic
- **Color Coding**: Red (negative) to Green (positive) sentiment

## 🔍 Sample Analysis

The app includes a sample transcript from Claritev Corp's Q2 2025 earnings call for testing and demonstration purposes.

## 🚨 Troubleshooting

### Common Issues

1. **WeasyPrint Errors**: Run `./install_dependencies.sh` or check DEPLOYMENT_GUIDE.md
2. **Import Errors**: Ensure virtual environment is activated and requirements are installed
3. **API Errors**: Verify OpenAI API key is set in `.env` file
4. **Memory Issues**: Use gpt-5 for best results, ensure sufficient API credits

### Getting Help
- Check the DEPLOYMENT_GUIDE.md for detailed troubleshooting
- Review error messages in the Streamlit interface
- Ensure all dependencies are properly installed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- Streamlit for the web framework
- Plotly for interactive visualizations
- Matplotlib and Squarify for treemap visualization
- The open-source community for various supporting libraries
