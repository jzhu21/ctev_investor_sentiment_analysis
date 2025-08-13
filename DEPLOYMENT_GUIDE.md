# Streamlit App Deployment Guide

This guide covers deploying the CTEV Earnings Call Sentiment Analysis Streamlit app to various platforms.

## Prerequisites

- Python 3.8+
- Git repository with your code
- Required dependencies (see `requirements.txt`)

## Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd ctev_investor_sentiment_analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app locally
streamlit run streamlit_app.py
```

## Deployment Options

### 1. Streamlit Cloud (Recommended)

**Pros:** Free, easy, automatic deployments
**Cons:** Limited customization

#### Steps:
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository
5. Set the main file path: `streamlit_app.py`
6. Deploy!

#### Requirements:
- Your `streamlit_app.py` must be in the root directory
- `requirements.txt` must be in the root directory
- No sensitive data in the code

### 2. Heroku

**Pros:** Full control, custom domains
**Cons:** Requires credit card, more complex setup

#### Steps:
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   " > ~/.streamlit/config.toml
   ```
4. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### 3. AWS/GCP/Azure

**Pros:** Enterprise-grade, scalable
**Cons:** Complex, requires cloud knowledge

#### Basic Docker Setup:
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Environment Variables

If you need to set environment variables (e.g., API keys):

### Streamlit Cloud:
- Go to your app settings
- Add environment variables in the "Secrets" section

### Heroku:
```bash
heroku config:set OPENAI_API_KEY=your_key_here
```

### Local:
Create `.env` file:
```env
OPENAI_API_KEY=your_key_here
```

## File Structure for Deployment

```
ctev_investor_sentiment_analysis/
├── streamlit_app.py          # Main app file
├── requirements.txt           # Dependencies
├── README.md                 # Documentation
├── DEPLOYMENT_GUIDE.md       # This file
├── output/                   # Analysis results (PNG files)
│   ├── q4_2024_sentiment_heatmap.png
│   ├── q1_2025_sentiment_heatmap.png
│   └── q2_2025_sentiment_heatmap.png
└── data/                     # Transcript data
    ├── Claritev Earnings Call Transcript 2024 Q4.txt
    ├── Claritev Earnings Call Transcript 2025 Q1.txt
    └── Claritev Earnings Call Transcript 2025 Q2.txt
```

## Troubleshooting

### Common Issues:

1. **Port already in use**: Change port in `streamlit run --server.port=8502`
2. **Dependencies not found**: Ensure `requirements.txt` is up to date
3. **File not found errors**: Check file paths are correct for your deployment
4. **CSS not working**: Clear browser cache, restart app

### Performance Tips:

1. **Image optimization**: Ensure PNG files are reasonable size (< 5MB each)
2. **Caching**: Use `@st.cache_data` for expensive operations
3. **Lazy loading**: Load data only when needed

## Security Considerations

- Never commit API keys or sensitive data
- Use environment variables for secrets
- Validate user inputs if adding forms
- Consider rate limiting for API calls

## Monitoring

- Streamlit Cloud provides basic analytics
- Heroku offers detailed logs and metrics
- Consider adding logging to your app

## Support

For deployment issues:
1. Check the platform's documentation
2. Review error logs
3. Test locally first
4. Ensure all dependencies are compatible

---

**Happy Deploying! 🚀**
