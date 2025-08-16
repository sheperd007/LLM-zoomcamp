import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from rag import rag
import db

app = FastAPI(
    title="IT Group Assistant API",
    description="An AI-powered IT assistance system with RAG capabilities",
    version="1.0.0"
)


# Pydantic models for request/response validation
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The IT question to be answered")


class QuestionResponse(BaseModel):
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="The AI-generated answer")


class FeedbackRequest(BaseModel):
    conversation_id: str = Field(..., description="The conversation ID to provide feedback for")
    feedback: int = Field(..., ge=-1, le=1, description="Feedback value: 1 for positive, -1 for negative")


class FeedbackResponse(BaseModel):
    message: str = Field(..., description="Confirmation message for the feedback")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


@app.post("/question", response_model=QuestionResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_question(request: QuestionRequest):
    """Handle incoming questions and return AI-generated answers"""
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="No question provided")

        conversation_id = str(uuid.uuid4())

        # Get answer from RAG system
        answer_data = rag(question)

        result = QuestionResponse(
            conversation_id=conversation_id,
            question=question,
            answer=answer_data["answer"],
        )

        # Save conversation to database
        db.save_conversation(
            conversation_id=conversation_id,
            question=question,
            answer_data=answer_data,
        )

        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/feedback", response_model=FeedbackResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_feedback(request: FeedbackRequest):
    """Handle user feedback for conversations"""
    try:
        conversation_id = request.conversation_id
        feedback = request.feedback

        if not conversation_id:
            raise HTTPException(status_code=400, detail="No conversation_id provided")
            
        if feedback not in [1, -1]:
            raise HTTPException(status_code=400, detail="Invalid feedback value. Must be 1 or -1")

        # Save feedback to database
        db.save_feedback(
            conversation_id=conversation_id,
            feedback=feedback,
        )

        result = FeedbackResponse(
            message=f"Feedback received for conversation {conversation_id}: {feedback}"
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="IT Group Assistant"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
