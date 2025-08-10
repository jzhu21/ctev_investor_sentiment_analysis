#!/usr/bin/env python3
"""
Transcript Analyzer
Extracts topics, counts words, assigns sentiment scores, and generates a squarify heatmap.
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

class TranscriptAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def read_transcript(self, file_path):
        """Read the transcript file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def clear_cache(self):
        """Clear the cached LLM analysis results."""
        cache_file = "llm_analysis_cache.json"
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"Cleared cache file: {cache_file}")
        else:
            print("No cache file found to clear")
    
    def analyze_transcript(self, transcript, force_new_analysis=False):
        """Use LLM to analyze transcript and extract topics with word counts and sentiment."""
        
        # Check if we have cached analysis results
        cache_file = "llm_analysis_cache.json"
        
        if not force_new_analysis and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                print(f"Loaded cached analysis results from {cache_file}")
                return cached_data
            except Exception as e:
                print(f"Error loading cached data: {e}")
                print("Will perform new analysis...")
        
        prompt = f"""
        Analyze the following earnings call transcript and extract the main topics discussed.
        
        For each topic, provide:
        1. Topic name (be specific and concise)
        2. Word count in that topic section
        3. Sentiment score from -1.0 (very negative) to 1.0 (very positive)
        
        Return the results as a JSON array with this exact format:
        [
            {{
                "topic": "Topic Name",
                "word_count": 150,
                "sentiment": 0.7
            }}
        ]
        
        Guidelines:
        - Identify 8-15 main topics
        - Be specific about topic names (e.g., "Revenue Growth" not just "Revenue")
        - Count actual words in each topic section
        - Assign sentiment based on the tone and content of each topic discussion
        - Ensure sentiment scores are between -1.0 and 1.0
        
        Transcript:
        {transcript[:8000]}  # Limit to first 8000 chars to stay within token limits
        """
        
        try:
            print("Calling OpenAI API for transcript analysis...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract and parse JSON response
            content = response.choices[0].message.content
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                topics_data = json.loads(json_match.group())
                
                # Cache the results
                try:
                    with open(cache_file, 'w') as f:
                        json.dump(topics_data, f, indent=2)
                    print(f"Analysis results cached to {cache_file}")
                except Exception as e:
                    print(f"Warning: Could not cache results: {e}")
                
                return topics_data
            else:
                raise ValueError("Could not extract JSON from LLM response")
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def generate_heatmap(self, topics_data):
        """Generate squarify heatmap with box sizes based on word counts and colors based on sentiment."""
        
        if not topics_data:
            print("No topics data available")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(topics_data)
        
        # Validate data
        print("Topics data:")
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
        
        # Sort by word count for better visualization
        df = df.sort_values('word_count', ascending=False)
        
        # Prepare data for squarify
        sizes = df['word_count'].values
        labels = df['topic'].values
        sentiments = df['sentiment'].values
        
        # Create color map based on sentiment (-1 to 1)
        # Use RdYlGn colormap for professional appearance
        colors = []
        for sentiment in sentiments:
            # Normalize sentiment from -1,1 to 0,1 for colormap
            normalized = (sentiment + 1) / 2
            # Use RdYlGn colormap: Red (negative) -> Yellow (neutral) -> Green (positive)
            if normalized <= 0.5:
                # Red to Yellow (negative to neutral)
                red = 1.0
                green = 2 * normalized
                blue = 0.0
            else:
                # Yellow to Green (neutral to positive)
                red = 2 * (1 - normalized)
                green = 1.0
                blue = 0.0
            
            colors.append((red, green, blue))
        
        # Create the plot
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Create a professional treemap visualization
        try:
            # Use squarify.plot for the main treemap with better text styling
            squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.9, ax=ax, 
                         text_kwargs={'fontsize': 8, 'fontweight': 'bold', 'color': 'black'})
            print("Successfully generated professional treemap")
            
            # Customize the treemap appearance
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Add professional title
            ax.set_title('Earnings Call Sentiment Analysis | Company Topics – 2025 Q2', 
                        fontsize=18, fontweight='bold', pad=30, loc='center')
            
        except Exception as e:
            print(f"Squarify failed: {e}")
            print("Falling back to horizontal bar chart...")
            
            # Clear the axis and create a horizontal bar chart
            ax.clear()
            
            # Create horizontal bar chart
            y_pos = np.arange(len(labels))
            bars = ax.barh(y_pos, sizes, color=colors, alpha=0.8)
            
            # Customize the chart
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_xlabel('Word Count')
            ax.set_title('Transcript Topics by Word Count and Sentiment\nColor = Sentiment (Red=Negative, Blue=Positive)', 
                        fontsize=14, fontweight='bold', pad=20)
            
            # Add value labels on bars
            for i, (bar, size, sentiment) in enumerate(zip(bars, sizes, sentiments)):
                width = bar.get_width()
                ax.text(width + max(sizes) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'{size} words\n{sentiment:.2f}', ha='left', va='center', fontsize=8)
            
            # Add legend
            legend_elements = [
                plt.Rectangle((0, 0), 1, 1, facecolor='red', alpha=0.8, label='Negative Sentiment'),
                plt.Rectangle((0, 0), 1, 1, facecolor='white', alpha=0.8, label='Neutral Sentiment'),
                plt.Rectangle((0, 0), 1, 1, facecolor='blue', alpha=0.8, label='Positive Sentiment')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            # Remove y-axis lines
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        # Set up the plot (only for squarify, bar chart is handled above)
        if 'squarify.plot' in str(ax.get_children()):
            # Add sentiment colorbar
            sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=plt.Normalize(-1, 1))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8, aspect=20, pad=0.1)
            cbar.set_label('Avg. Sentiment', rotation=270, labelpad=15, fontsize=12, fontweight='bold')
            cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
            cbar.set_ticklabels(['-1.0', '-0.5', '0.0', '0.5', '1.0'])
            cbar.ax.tick_params(labelsize=10)
            
            # Add key takeaways text box
            takeaways_text = f"""Key Takeaways:
• Total topics analyzed: {len(df)}
• Total words: {df['word_count'].sum():,}
• Average sentiment: {df['sentiment'].mean():.3f}
• Most positive topic: {df.loc[df['sentiment'].idxmax(), 'topic']} ({df['sentiment'].max():.2f})
• Largest topic: {df.loc[df['word_count'].idxmax(), 'topic']} ({df['word_count'].max()} words)"""
            
            # Position text box on the right side
            ax.text(105, 80, takeaways_text, transform=ax.transData, 
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8),
                   fontsize=10, verticalalignment='top', fontweight='bold')
            
            # Add methodology note
            note_text = """Note:
• Graph displays topics by word count and sentiment scores
• Topics are themes discussed during the earnings call
• Sentiment scores range from -1.0 (negative) to 1.0 (positive)
• Box size represents relative word count in each topic"""
            
            ax.text(105, 30, note_text, transform=ax.transData,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
                   fontsize=9, verticalalignment='top')
        
        plt.tight_layout()
        plt.show()
        
        # Also save the plot
        plt.savefig('transcript_heatmap.png', dpi=300, bbox_inches='tight')
        print("\nHeatmap saved as 'transcript_heatmap.png'")
        
        return df

def main():
    """Main function to run the transcript analysis."""
    
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze earnings call transcript and generate sentiment heatmap')
    parser.add_argument('--force-new', action='store_true', 
                       help='Force new LLM analysis instead of using cached results')
    parser.add_argument('--transcript', default="data/ctev_transcript_2025Q2.txt",
                       help='Path to transcript file (default: data/ctev_transcript_2025Q2.txt)')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear cached LLM analysis results')
    
    args = parser.parse_args()
    
    # Handle clear cache option
    if args.clear_cache:
        analyzer = TranscriptAnalyzer()
        analyzer.clear_cache()
        return
    
    # Check if transcript file exists
    transcript_file = args.transcript
    
    if not os.path.exists(transcript_file):
        print(f"Transcript file not found: {transcript_file}")
        return
    
    try:
        # Initialize analyzer
        analyzer = TranscriptAnalyzer()
        
        # Read transcript
        print("Reading transcript...")
        transcript = analyzer.read_transcript(transcript_file)
        print(f"Transcript loaded: {len(transcript)} characters")
        
        # Analyze with LLM (or load from cache)
        print("\nAnalyzing transcript...")
        topics_data = analyzer.analyze_transcript(transcript, force_new_analysis=args.force_new)
        
        if topics_data:
            print(f"\nExtracted {len(topics_data)} topics")
            
            # Generate heatmap
            print("\nGenerating heatmap...")
            df = analyzer.generate_heatmap(topics_data)
            
            if df is not None:
                print("\nAnalysis complete!")
                print("\nSummary:")
                print(f"Total topics: {len(df)}")
                print(f"Total words: {df['word_count'].sum()}")
                print(f"Average sentiment: {df['sentiment'].mean():.3f}")
                print(f"Sentiment range: {df['sentiment'].min():.3f} to {df['sentiment'].max():.3f}")
                
                print(f"\nTo force new LLM analysis, run: python transcript_analyzer.py --force-new")
        
        else:
            print("Failed to analyze transcript")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
