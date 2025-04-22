import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
API_URL = "http://localhost:8000/chat"

def send_message(message, thread_id=None, user_id=None):
    """Send a message to the agent and print the response."""
    payload = {
        "message": message,
        "thread_id": thread_id,
        "user_id": user_id
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    print(f"\nUser: {message}")
    
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Agent: {data['response']}")
        return data["thread_id"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def run_conversation(user_id=None):
    """Run a sample conversation with the agent."""
    
    # First message - check order status
    thread_id = send_message("I want to check my order status for ORD123456", user_id=user_id)
    
    if not thread_id:
        return
    
    # Second message - follow-up question about shipping
    send_message("How long does shipping usually take?", thread_id=thread_id, user_id=user_id)
    
    # Third message - initiate a return for a delivered order
    send_message("I need to return my headphones from order ORD789012. They're defective.", 
                thread_id=thread_id, user_id=user_id)
    
    # Fourth message - ask about warranty
    send_message("What's your warranty policy?", thread_id=thread_id, user_id=user_id)
    
    # Fifth message - order that doesn't exist
    send_message("Where is my order ORD999999?", thread_id=thread_id, user_id=user_id)

if __name__ == "__main__":
    # Test with a user ID for personalization
    run_conversation(user_id="test_user_123")
    
    # You can also run without a user ID
    # run_conversation() 