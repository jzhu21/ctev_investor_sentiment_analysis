#!/bin/bash

# Run Streamlit Web App for CTEV Earnings Call Sentiment Analysis

echo "🚀 Starting CTEV Earnings Call Sentiment Analysis Web App..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Installing requirements..."
    pip install -r requirements.txt
fi

# Check if output data exists
if [ ! -d "output" ]; then
    echo "⚠️  Warning: No output directory found."
    echo "   Please run the analysis first: python src/ctev_earnings_call_analysis.py"
    echo ""
fi

# Start Streamlit app
echo "🌐 Starting Streamlit web app..."
echo "   The app will open in your browser at: http://localhost:8501"
echo "   Press Ctrl+C to stop the app"
echo ""

streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
