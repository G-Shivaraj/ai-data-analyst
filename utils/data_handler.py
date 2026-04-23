# utils/data_handler.py
import pandas as pd

def load_and_summarize_csv(uploaded_file):
    """Reads a CSV and returns the DataFrame and a schema summary."""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Generate a quick schema summary for the AI context
        schema = df.dtypes.astype(str).to_dict()
        summary = f"Dataset loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.\n\nSchema: {schema}"
        
        return df, summary
    except Exception as e:
        return None, f"Error loading file: {e}"