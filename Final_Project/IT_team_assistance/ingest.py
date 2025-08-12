import os
import pandas as pd
import minsearch

DATA_PATH = os.getenv("DATA_PATH", "../data/data.csv")


def load_index(data_path=DATA_PATH):
    """Load and index the IT knowledge dataset"""
    try:
        # Read the CSV file
        df = pd.read_csv(data_path)
        
        # Convert to list of dictionaries
        documents = df.to_dict(orient="records")

        # Create search index
        index = minsearch.Index(
            text_fields=[
                "Title",
                "Text", 
                "alt_Text"
            ],
            keyword_fields=[],
        )

        # Fit the index with documents
        index.fit(documents)
        print(f"Successfully loaded {len(documents)} IT knowledge items into search index")
        return index
        
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        raise
    except Exception as e:
        print(f"Error loading data: {e}")
        raise