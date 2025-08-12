#!/usr/bin/env python3
"""
Earnings Call Sentiment Analysis
Analyzes Claritev earnings call transcripts to extract topics,
word counts, and sentiment scores using OpenAI API.
Supports Q4 2024, Q1 2025, and Q2 2025 transcripts.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import squarify
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import re

# Load environment variables
load_dotenv()

class EarningsCallAnalyzer:
    def __init__(self, quarter_name):
        """Initialize the analyzer with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.quarter_name = quarter_name
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        print(f"Using OpenAI model: {self.model}")
        print(f"Analyzing: {quarter_name}")
    
    def read_transcript(self, file_path):
        """Read the transcript file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def analyze_transcript(self, transcript):
        """Use OpenAI to analyze sentiment for predefined topics from sentiment_treemap.py."""
        
        # Use exactly the same topics as sentiment_treemap.py
        predefined_topics = [
            "Operating Costs",
            "Technology", 
            "EBITDA",
            "Net Income",
            "Guidance",
            "Capital",
            "Revenue",
            "Products",
            "Debt",
            "Sales",
            "Customers",
            "Govt.",
            "Margins",
            "Market Share"
        ]
        
        prompt = f"""
        Analyze the following Q4 2024 Claritev earnings call transcript and provide sentiment scores for each of these specific topics.
        
        For each topic, provide:
        1. Topic name (exactly as listed)
        2. Word count in that topic section
        3. Sentiment score from -1.0 (very negative) to 1.0 (very positive)
        
        Return the results as a JSON array with this exact format:
        [
            {{
                "topic": "Operating Costs",
                "word_count": 150,
                "sentiment": 0.7
            }}
        ]
        
        Guidelines:
        - Use exactly the topic names provided (do not change or modify them)
        - Count actual words in each topic section
        - Assign sentiment based on the tone and content of each topic discussion
        - Consider financial performance, strategic initiatives, and market positioning
        - Ensure sentiment scores are between -1.0 and 1.0
        - If a topic is not discussed, assign a middle value (0.5) and set word count to 0
        
        Topics to analyze: {', '.join(predefined_topics)}
        
        Transcript:
        {transcript}
        """
        
        try:
            print("Calling OpenAI API for sentiment analysis of predefined topics...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Extract and parse JSON response
            content = response.choices[0].message.content
            print("Raw API response:")
            print(content)
            
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                topics_data = json.loads(json_match.group())
                return topics_data
            else:
                raise ValueError("Could not extract JSON from LLM response")
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def save_results(self, topics_data):
        """Save the analysis results to a JSON file."""
        # Create filename based on quarter
        quarter_safe = self.quarter_name.replace(" ", "_").lower()
        output_file = f"{quarter_safe}_analysis_results.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(topics_data, f, indent=2)
            print(f"Analysis results saved to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def generate_heatmap(self, topics_data, title):
        """Generate squarify heatmap with box sizes based on word counts and colors based on sentiment."""
        
        if not topics_data:
            print("No topics data available")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(topics_data)
        
        # Validate data
        print("\nTopics data:")
        print(df)
        print(f"\nData types: {df.dtypes}")
        
        # Ensure numeric columns
        df['word_count'] = pd.to_numeric(df['word_count'], errors='coerce')
        df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
        
        # Remove any invalid rows
        df = df.dropna()
        
        if df.empty:
            print("No valid data after cleaning")
            return
        
        # Filter out topics with 0 word count to avoid squarify division by zero error
        df = df[df['word_count'] > 0]
        
        if df.empty:
            print("No topics with word counts > 0 after filtering")
            return
        
        # Sort by word count for better visualization
        df = df.sort_values('word_count', ascending=False)
        
        print(f"Visualizing {len(df)} topics with word counts > 0")
        
        # Prepare data for squarify - using exact same format as sentiment_treemap.py
        topics = df['topic'].values
        sizes = df['word_count'].values
        sentiment = df['sentiment'].values
        
        # Use color scheme from 0 to 1 (red to green) since all scores are positive
        import matplotlib as mpl
        norm = mpl.colors.Normalize(vmin=0, vmax=1)
        cmap = mpl.cm.RdYlGn
        colors = [cmap(norm(s)) for s in sentiment]
        
        # Create the plot with same figsize as sentiment_treemap.py
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Plot treemap without labels first - using exact same parameters
        squarify.plot(
            sizes=sizes,
            label=None,  # Don't show labels initially
            color=colors,
            alpha=0.8,
            edgecolor='white',
            linewidth=5,
            ax=ax
        )
        
        # Manually add labels in lower left of each box - exact same code as sentiment_treemap.py
        for i, topic in enumerate(topics):
            # Get the rectangle coordinates from squarify
            rect = ax.patches[i]
            x, y = rect.get_xy()
            width, height = rect.get_width(), rect.get_height()
            
            # Position text in lower left with some padding
            text_x = x + width * 0.05  # 5% from left edge
            text_y = y + height * 0.1   # 10% from bottom edge
            
            # Choose text color based on background color for better contrast
            bg_color = colors[i]
            # Convert RGB to brightness and choose text color accordingly
            if bg_color[0] * 0.299 + bg_color[1] * 0.587 + bg_color[2] * 0.114 > 0.5:
                text_color = 'black'  # Light background, use black text
            else:
                text_color = 'white'  # Dark background, use white text
            
            ax.text(text_x, text_y, topic, 
                    fontsize=10, weight='bold', 
                    ha='left', va='bottom',
                    color=text_color)
        
        plt.axis('off')
        
        # Colorbar - using exact same styling as sentiment_treemap.py
        sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.15, pad=0.08, aspect=30)
        cbar.outline.set_edgecolor('none')  # Remove the dark outline
        
        # Add custom tick labels - updated for 0-1 range
        cbar.set_ticks([0, 0.5, 1])
        cbar.set_ticklabels(['Neutral', 'Moderate', 'Very Positive'])
        cbar.ax.tick_params(labelsize=10)
        
        # Title - using exact same format as sentiment_treemap.py
        plt.title(title, fontsize=16, weight='bold', loc='left')
        
        plt.show()
        
        # Save the plot
        quarter_safe = self.quarter_name.replace(" ", "_").lower()
        output_file = f'{quarter_safe}_sentiment_heatmap.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\nHeatmap saved as '{output_file}'")
        
        return df
    
    def print_summary(self, df):
        """Print a detailed summary of the analysis."""
        if df is None or df.empty:
            print("No data to summarize")
            return
        
        print("\n" + "="*80)
        print(f"{self.quarter_name.upper()} CLARITEV EARNINGS CALL ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\nTotal Topics Analyzed: {len(df)}")
        print(f"Total Words: {df['word_count'].sum():,}")
        print(f"Average Sentiment: {df['sentiment'].mean():.3f}")
        print(f"Sentiment Range: {df['sentiment'].min():.3f} to {df['sentiment'].max():.3f}")
        
        print("\n" + "-"*80)
        print("TOPICS BY SENTIMENT (Most Positive to Most Negative)")
        print("-"*80)
        
        # Sort by sentiment
        sentiment_sorted = df.sort_values('sentiment', ascending=False)
        for idx, row in sentiment_sorted.iterrows():
            sentiment_emoji = "🟢" if row['sentiment'] > 0.3 else "🟡" if row['sentiment'] > -0.3 else "🔴"
            print(f"{sentiment_emoji} {row['topic']:<40} | Sentiment: {row['sentiment']:>6.2f} | Words: {row['word_count']:>6}")
        
        print("\n" + "-"*80)
        print("TOPICS BY SIZE (Largest to Smallest)")
        print("-"*80)
        
        # Sort by word count
        size_sorted = df.sort_values('word_count', ascending=False)
        for idx, row in size_sorted.iterrows():
            sentiment_emoji = "🟢" if row['sentiment'] > 0.3 else "🟡" if row['sentiment'] > -0.3 else "🔴"
            print(f"{sentiment_emoji} {row['topic']:<40} | Words: {row['word_count']:>6} | Sentiment: {row['sentiment']:>6.2f}")
        
        print("\n" + "="*80)

def main():
    """Main function to run earnings call transcript analysis."""
    
    # Available transcript options
    transcript_options = {
        "1": {
            "name": "Q4 2024",
            "file": "data/Claritev Earnings Call Transcript 2024 Q4.txt",
            "title": "Claritev Earnings Call Sentiment Analysis | 2024 Q4"
        },
        "2": {
            "name": "Q1 2025", 
            "file": "data/Claritev Earnings Call Transcript 2025 Q1.txt",
            "title": "Claritev Earnings Call Sentiment Analysis | 2025 Q1"
        },
        "3": {
            "name": "Q2 2025",
            "file": "data/Claritev Earnings Call Transcript 2025 Q2.txt", 
            "title": "Claritev Earnings Call Sentiment Analysis | 2025 Q2"
        }
    }
    
    # Display selection menu
    print("="*60)
    print("CLARITEV EARNINGS CALL SENTIMENT ANALYSIS")
    print("="*60)
    print("Select an earnings call to analyze:")
    for key, option in transcript_options.items():
        print(f"  {key}. {option['name']}")
    print("  q. Quit")
    print("-"*60)
    
    # Get user selection
    while True:
        choice = input("Enter your choice (1-3 or q): ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            return
        elif choice in transcript_options:
            selected_option = transcript_options[choice]
            transcript_file = selected_option['file']
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or q.")
    
    print(f"\nSelected: {selected_option['name']}")
    
    if not os.path.exists(transcript_file):
        print(f"Transcript file not found: {transcript_file}")
        return
    
    try:
        # Initialize analyzer
        analyzer = EarningsCallAnalyzer(selected_option['name'])
        
        # Read transcript
        print(f"Reading {selected_option['name']} transcript...")
        transcript = analyzer.read_transcript(transcript_file)
        print(f"Transcript loaded: {len(transcript)} characters")
        
        # Analyze with OpenAI
        print("\nAnalyzing transcript with OpenAI...")
        topics_data = analyzer.analyze_transcript(transcript)
        
        if topics_data:
            print(f"\nExtracted {len(topics_data)} topics")
            
            # Save results
            analyzer.save_results(topics_data)
            
            # Generate heatmap
            print("\nGenerating sentiment heatmap...")
            df = analyzer.generate_heatmap(topics_data, selected_option['title'])
            
            if df is not None:
                # Print detailed summary
                analyzer.print_summary(df)
                print("\nAnalysis complete! Check the generated files:")
                quarter_safe = selected_option['name'].replace(" ", "_").lower()
                print(f"- {quarter_safe}_analysis_results.json (raw data)")
                print(f"- {quarter_safe}_sentiment_heatmap.png (visualization)")
        
        else:
            print("Failed to analyze transcript")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
