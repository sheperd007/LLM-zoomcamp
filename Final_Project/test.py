import pandas as pd
import requests

def get_random_question():
    """Get a random question from the dataset"""
    df = pd.read_csv("./data/data.csv")
    # Create a sample question based on the Title field
    sample_row = df.sample(n=1).iloc[0]
    question = f"What is {sample_row['Title']}?"
    return question

def test_api():
    """Test the API with a random question"""
    question = get_random_question()
    print(f"Question: {question}")
    
    url = "http://localhost:5000/question"
    data = {"question": question}
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"Answer: {result.get('answer', 'No answer provided')}")
        print(f"Conversation ID: {result.get('conversation_id', 'N/A')}")
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()