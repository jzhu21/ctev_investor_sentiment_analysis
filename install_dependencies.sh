#!/bin/bash

# Install system dependencies for WeasyPrint on macOS (optional)
# This script helps resolve the libgobject-2.0-0 error if PDF generation is needed

echo "🔧 Installing system dependencies for WeasyPrint..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for this session
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ $(uname -m) == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
else
    echo "✅ Homebrew already installed"
fi

# Install required system libraries
echo "📚 Installing required system libraries..."
brew install cairo pango gdk-pixbuf libffi

# Verify installation
echo "🔍 Verifying installation..."
if brew list cairo &> /dev/null && brew list pango &> /dev/null && brew list gdk-pixbuf &> /dev/null && brew list libffi &> /dev/null; then
    echo "✅ All dependencies installed successfully!"
    echo ""
    echo "🎉 You should now be able to generate PDF reports without errors."
echo "   Note: The main Streamlit app no longer requires PDF generation."
echo "   Try running the Streamlit app:"
echo "   streamlit run streamlit_app.py"
else
    echo "❌ Some dependencies failed to install. Please check the error messages above."
    exit 1
fi

echo ""
echo "💡 If you still encounter issues, you can:"
echo "   1. Restart your terminal to ensure PATH changes take effect"
echo "   2. Try running: brew doctor"
echo "   3. Check the DEPLOYMENT_GUIDE.md for alternative solutions"
