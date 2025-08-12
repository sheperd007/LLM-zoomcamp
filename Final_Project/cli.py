import json
import uuid
import argparse

import requests
import questionary
import pandas as pd


def get_random_question(file_path):
    """Get a random question from the dataset"""
    df = pd.read_csv(file_path)
    sample_row = df.sample(n=1).iloc[0]
    question = f"What is {sample_row['Title']}?"
    return question


def ask_question(url, question):
    """Send a question to the API and get response"""
    data = {"question": question}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


def send_feedback(url, conversation_id, feedback):
    """Send feedback to the API"""
    feedback_data = {"conversation_id": conversation_id, "feedback": feedback}
    try:
        response = requests.post(f"{url}/feedback", json=feedback_data)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error sending feedback: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Interactive CLI app for IT assistance questions and feedback"
    )
    parser.add_argument(
        "--random", action="store_true", help="Use random questions from the CSV file"
    )
    args = parser.parse_args()

    base_url = "http://localhost:5000"
    csv_file = "./data/data.csv"

    print("Welcome to the IT Group Assistant!")
    print("You can exit the program at any time when prompted.")

    while True:
        if args.random:
            question = get_random_question(csv_file)
            print(f"\nRandom question: {question}")
        else:
            question = questionary.text("Enter your IT question:").ask()

        if not question:
            print("Please enter a valid question.")
            continue

        response = ask_question(f"{base_url}/question", question)
        
        if response is None:
            print("Failed to get response from the API. Please try again.")
            continue

        print("\nAnswer:", response.get("answer", "No answer provided"))

        conversation_id = response.get("conversation_id", str(uuid.uuid4()))

        feedback = questionary.select(
            "How would you rate this response?",
            choices=["+1 (Positive)", "-1 (Negative)", "Pass (Skip feedback)"],
        ).ask()

        if feedback != "Pass (Skip feedback)":
            feedback_value = 1 if feedback == "+1 (Positive)" else -1
            status = send_feedback(base_url, conversation_id, feedback_value)
            if status:
                print(f"Feedback sent. Status code: {status}")
            else:
                print("Failed to send feedback.")
        else:
            print("Feedback skipped.")

        continue_prompt = questionary.confirm("Do you want to continue?").ask()
        if not continue_prompt:
            print("Thank you for using the IT Group Assistant. Goodbye!")
            break


if __name__ == "__main__":
    main()
