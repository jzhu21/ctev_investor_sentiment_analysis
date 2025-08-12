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
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving
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
        self.model = os.getenv('OPENAI_MODEL', 'gpt-5')
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
        """Use OpenAI to analyze sentiment for LLM-identified topics from the transcript."""
        
        prompt = f"""
        Analyze the following {self.quarter_name} Claritev earnings call transcript and identify the key topics discussed.
        
        For each identified topic, provide:
        1. Topic name (maximum 2 words only - keep it concise)
        2. Word count in that topic section
        3. Sentiment score from -1.0 (very negative) to 1.0 (very positive)
        4. Reasoning for the sentiment score (brief explanation of why this score was assigned)
        
        Return the results as a JSON array with this exact format:
        [
            {{
                "topic": "Topic Name",
                "word_count": 150,
                "sentiment": 0.7,
                "reasoning": "Brief explanation of why this sentiment score was assigned"
            }}
        ]
        
        Guidelines:
        - Identify 8-15 key topics that are actually discussed in the transcript
        - Keep each topic name to exactly 2 words maximum (e.g., "Operating Costs", "Net Income", "Market Share")
        - Count actual words in each topic section
        - Assign sentiment based on the tone and content of each topic discussion
        - Consider financial performance, strategic initiatives, and market positioning
        - Ensure sentiment scores are between -1.0 and 1.0
        - Focus on business-relevant topics like financial metrics, operations, strategy, market conditions, etc.
        - Do not include generic topics like "Introduction" or "Conclusion"
        - Provide concise reasoning (1-2 sentences) explaining the sentiment score for each topic
        
        Transcript:
        {transcript}
        """
        
        try:
            print("Calling OpenAI API for LLM-identified topics and sentiment analysis...")
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                text={
                    "verbosity": "medium"
                },
                reasoning={
                    "effort": "medium"
                }
            )
            
            # Extract and parse JSON response
            print("Raw API response:")
            print(response)
            print(f"Response type: {type(response)}")
            
            # For GPT-5 responses API, extract content from the correct path
            try:
                if response.output and len(response.output) > 0:
                    # Find the ResponseOutputMessage item (not the ResponseReasoningItem)
                    message_item = None
                    for item in response.output:
                        if hasattr(item, 'content') and item.content:
                            message_item = item
                            break
                    
                    if message_item and message_item.content and len(message_item.content) > 0:
                        content = message_item.content[0].text
                        if content is None:
                            raise ValueError("Content text is None")
                    else:
                        raise ValueError("No content in output")
                else:
                    raise ValueError("No output in response")
                
                print(f"Extracted content: {content}")
                print(f"Content length: {len(content)} characters")
            except Exception as e:
                print(f"Error extracting content: {e}")
                print(f"Response output structure: {response.output}")
                if response.output and len(response.output) > 0:
                    for i, item in enumerate(response.output):
                        print(f"Output item {i}: {type(item).__name__} - {item}")
                        if hasattr(item, 'content'):
                            print(f"  Content: {item.content}")
                raise
            
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    topics_data = json.loads(json_match.group())
                    return topics_data
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Extracted content: {json_match.group()}")
                    raise ValueError(f"Could not parse JSON: {e}")
            else:
                print("No JSON array found in response")
                print("Trying to find any JSON content...")
                # Try to find any JSON-like content
                json_like = re.search(r'\{.*\}', content, re.DOTALL)
                if json_like:
                    print(f"Found JSON-like content: {json_like.group()}")
                raise ValueError("Could not extract JSON from LLM response")
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def save_results(self, topics_data):
        """Save the analysis results to a JSON file."""
        # Create filename based on quarter
        quarter_safe = self.quarter_name.replace(" ", "_").lower()
        output_file = f"output/{quarter_safe}_analysis_results.json"
        
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
        
        # Prepare data for squarify
        topics = df['topic'].values
        sizes = df['word_count'].values
        sentiment = df['sentiment'].values
        
        # Dynamically adjust color scheme based on sentiment range
        import matplotlib as mpl
        
        # Determine sentiment range for colorbar
        min_sentiment = df['sentiment'].min()
        max_sentiment = df['sentiment'].max()
        
        # If all scores are >= 0, use 0-1 range; if any < 0, use -1 to 1 range
        if min_sentiment >= 0:
            # All positive/neutral scores: use consistent 0-1 range for proper color mapping
            norm = mpl.colors.Normalize(vmin=0, vmax=1)
            cmap = mpl.cm.RdYlGn  # Green for positive, red for neutral
            print(f"Using positive-only color scheme (0-1) - all sentiment scores >= 0")
        else:
            # Has negative scores: use full -1 to 1 range
            norm = mpl.colors.Normalize(vmin=-1, vmax=1)
            cmap = mpl.cm.RdYlGn  # Red for negative, green for positive
            print(f"Using full-range color scheme (-1 to 1) - sentiment range: {min_sentiment:.2f} to {max_sentiment:.2f}")
        
        colors = [cmap(norm(s)) for s in sentiment]
        
        # Create the plot with same figsize as sentiment_treemap.py
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Plot treemap without labels first
        squarify.plot(
            sizes=sizes,
            label=None,  # Don't show labels initially
            color=colors,
            alpha=0.8,
            edgecolor='white',
            linewidth=5,
            ax=ax
        )
        
        # Manually add labels in lower left of each box
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
        
        # Colorbar styling
        sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.15, pad=0.08, aspect=30)
        cbar.outline.set_edgecolor('none')  # Remove the dark outline
        
        # Add custom tick labels based on sentiment range
        if min_sentiment >= 0:
            # All positive/neutral scores: show consistent 0-1 range
            cbar.set_ticks([0, 0.5, 1])
            cbar.set_ticklabels(['Neutral', 'Moderately Positive', 'Very Positive'])
        else:
            # Has negative scores: show full -1 to 1 range
            cbar.set_ticks([-1, 0, 1])
            cbar.set_ticklabels(['Very Negative', 'Neutral', 'Very Positive'])
        cbar.ax.tick_params(labelsize=10)
        
        # Title
        plt.title(title, fontsize=16, weight='bold', loc='left')
        
        # Save the plot first
        quarter_safe = self.quarter_name.replace(" ", "_").lower()
        output_file = f'output/{quarter_safe}_sentiment_heatmap.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"\nHeatmap saved as '{output_file}'")
        
        # Close the plot to free memory
        plt.close()
        
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
            if 'reasoning' in row and pd.notna(row['reasoning']):
                print(f"    Reasoning: {row['reasoning']}")
            print()
        
        print("\n" + "-"*80)
        print("TOPICS BY SIZE (Largest to Smallest)")
        print("-"*80)
        
        # Sort by word count
        size_sorted = df.sort_values('word_count', ascending=False)
        for idx, row in size_sorted.iterrows():
            sentiment_emoji = "🟢" if row['sentiment'] > 0.3 else "🟡" if row['sentiment'] > -0.3 else "🔴"
            print(f"{sentiment_emoji} {row['topic']:<40} | Words: {row['word_count']:>6} | Sentiment: {row['sentiment']:>6.2f}")
            if 'reasoning' in row and pd.notna(row['reasoning']):
                print(f"    Reasoning: {row['reasoning']}")
            print()
        
        print("\n" + "-"*80)
        print("DETAILED REASONING FOR EACH TOPIC")
        print("-"*80)
        
        for idx, row in df.iterrows():
            sentiment_emoji = "🟢" if row['sentiment'] > 0.3 else "🟡" if row['sentiment'] > -0.3 else "🔴"
            print(f"{sentiment_emoji} {row['topic']}")
            if 'reasoning' in row and pd.notna(row['reasoning']):
                print(f"    Sentiment: {row['sentiment']:.2f}")
                print(f"    Reasoning: {row['reasoning']}")
            else:
                print(f"    Sentiment: {row['sentiment']:.2f}")
                print(f"    Reasoning: Not provided")
            print()
        
        print("="*80)

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
                print(f"- output/{quarter_safe}_analysis_results.json (raw data)")
                print(f"- output/{quarter_safe}_sentiment_heatmap.png (visualization)")
        
        else:
            print("Failed to analyze transcript")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
