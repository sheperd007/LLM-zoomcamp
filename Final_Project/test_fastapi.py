#!/usr/bin/env python3
"""
Test script to verify FastAPI conversion works correctly
"""
import requests
import json

def test_fastapi_endpoints():
    """Test the FastAPI endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing FastAPI endpoints...")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        health_data = response.json()
        print(f"✅ Health check passed: {health_data}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test question endpoint
    print("\n2. Testing question endpoint...")
    test_question = "What is Docker?"
    try:
        response = requests.post(
            f"{base_url}/question",
            json={"question": test_question}
        )
        response.raise_for_status()
        question_data = response.json()
        print(f"✅ Question endpoint passed")
        print(f"   Question: {question_data.get('question')}")
        print(f"   Answer: {question_data.get('answer', 'N/A')[:100]}...")
        print(f"   Conversation ID: {question_data.get('conversation_id')}")
        
        conversation_id = question_data.get('conversation_id')
        
    except Exception as e:
        print(f"❌ Question endpoint failed: {e}")
        return False
    
    # Test feedback endpoint
    print("\n3. Testing feedback endpoint...")
    try:
        response = requests.post(
            f"{base_url}/feedback",
            json={"conversation_id": conversation_id, "feedback": 1}
        )
        response.raise_for_status()
        feedback_data = response.json()
        print(f"✅ Feedback endpoint passed: {feedback_data}")
    except Exception as e:
        print(f"❌ Feedback endpoint failed: {e}")
        return False
    
    # Test API documentation
    print("\n4. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API documentation available at /docs")
        else:
            print("⚠️  API documentation not available")
    except Exception as e:
        print(f"⚠️  Could not access API documentation: {e}")
    
    print("\n🎉 All tests completed successfully!")
    return True

if __name__ == "__main__":
    test_fastapi_endpoints()
