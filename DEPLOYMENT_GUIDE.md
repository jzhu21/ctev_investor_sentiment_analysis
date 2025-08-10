# Deployment Guide

## System Requirements

### Python Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### System Dependencies for PDF Generation (macOS)

The PDF generation feature requires WeasyPrint, which has system dependencies. On macOS, install them using Homebrew:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required system libraries
brew install pango gdk-pixbuf libffi cairo pango gdk-pixbuf libffi

# Alternative: Install all dependencies at once
brew install cairo pango gdk-pixbuf libffi
```

### Alternative: Use Docker

If you prefer to avoid system dependencies, you can run the app in Docker:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Running the Application

### Local Development
```bash
streamlit run streamlit_app.py
```

### Production Deployment
```bash
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

## Troubleshooting

### WeasyPrint Issues
If you encounter WeasyPrint errors:

1. **On macOS**: Install system dependencies with Homebrew (see above)
2. **On Ubuntu/Debian**: `sudo apt-get install libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev`
3. **On CentOS/RHEL**: `sudo yum install cairo-devel pango-devel gdk-pixbuf2-devel libffi-devel`

### Alternative PDF Generation
If WeasyPrint continues to cause issues, the app will gracefully fall back to HTML-only reports. PDF generation is optional and not required for core functionality.

## Environment Variables

Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Security Notes

- Never commit your `.env` file to version control
- The app processes transcripts locally and does not send data to external services (except OpenAI for analysis)
- Consider using environment-specific configuration for production deployments
