# Deploy to Streamlit Cloud in 5 Minutes

## Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Streamlit web app for CTEV sentiment analysis"
git push origin main
```

## Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your repository: `ctev_investor_sentiment_analysis`
5. Set the main file path: `streamlit_app.py`
6. Click "Deploy!"

## Step 3: Your App is Live! 🎉
- Streamlit Cloud will automatically deploy your app
- You'll get a public URL like: `https://your-app-name.streamlit.app`
- Any future pushes to GitHub will automatically redeploy

## What Gets Deployed
- ✅ `streamlit_app.py` - Your Streamlit web app
- ✅ `requirements.txt` - Python dependencies
- ✅ `output/` folder - PNG heatmaps and JSON data
- ✅ All supporting files

## Troubleshooting
- **App not loading**: Check that `streamlit_app.py` is in the root directory
- **Missing dependencies**: Ensure `requirements.txt` is up to date
- **File not found errors**: Verify PNG files exist in `output/` folder

## Next Steps
- Share your app URL with stakeholders
- Monitor app performance in Streamlit Cloud dashboard
- Consider adding custom domain if needed

---
**Your CTEV sentiment analysis is now live on the web! 🌐**
