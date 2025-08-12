import uuid
from flask import Flask, request, jsonify
from rag import rag
import db

app = Flask(__name__)


@app.route("/question", methods=["POST"])
def handle_question():
    """Handle incoming questions and return AI-generated answers"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        question = data.get("question")
        if not question or not question.strip():
            return jsonify({"error": "No question provided"}), 400

        conversation_id = str(uuid.uuid4())

        # Get answer from RAG system
        answer_data = rag(question.strip())

        result = {
            "conversation_id": conversation_id,
            "question": question,
            "answer": answer_data["answer"],
        }

        # Save conversation to database
        db.save_conversation(
            conversation_id=conversation_id,
            question=question,
            answer_data=answer_data,
        )

        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/feedback", methods=["POST"])
def handle_feedback():
    """Handle user feedback for conversations"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        conversation_id = data.get("conversation_id")
        feedback = data.get("feedback")

        if not conversation_id:
            return jsonify({"error": "No conversation_id provided"}), 400
            
        if feedback not in [1, -1]:
            return jsonify({"error": "Invalid feedback value. Must be 1 or -1"}), 400

        # Save feedback to database
        db.save_feedback(
            conversation_id=conversation_id,
            feedback=feedback,
        )

        result = {
            "message": f"Feedback received for conversation {conversation_id}: {feedback}"
        }
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "IT Group Assistant"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
