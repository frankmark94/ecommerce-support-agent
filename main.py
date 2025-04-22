import os
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from openai import OpenAI
from openai.types.beta.threads import Run

# Import config and tools
import config
from tools import tool_definitions, tool_functions

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(title="E-Commerce Customer Support Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory database for demo purposes
orders_db = {
    "ORD123456": {
        "status": "shipped",
        "tracking_number": "TRK789012",
        "estimated_delivery": "2024-06-15",
        "items": ["Red Sneakers", "Blue T-shirt"],
        "total": 89.99,
        "customer_id": "CUST001"
    },
    "ORD789012": {
        "status": "delivered",
        "delivery_date": "2024-06-01",
        "items": ["Wireless Headphones"],
        "total": 129.99,
        "customer_id": "CUST002"
    },
    "ORD345678": {
        "status": "processing",
        "items": ["Laptop Bag", "USB-C Cable"],
        "total": 45.50,
        "customer_id": "CUST001"
    }
}

faq_db = {
    "return policy": "You can return any item within 30 days of purchase for a full refund.",
    "shipping cost": "Standard shipping is free for orders over $50. Express shipping costs $9.99.",
    "shipping time": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days.",
    "payment methods": "We accept all major credit cards, PayPal, and Apple Pay.",
    "warranty": "Most products come with a 1-year manufacturer warranty."
}

# Store user sessions
sessions = {}

# Request and Response Models
class MessageRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    thread_id: str

# Tool Functions
def get_order_status(order_id: str) -> Dict:
    """Retrieve the status of an order."""
    logger.info(f"Tool called: get_order_status with order_id={order_id}")
    
    if order_id in orders_db:
        return {
            "success": True,
            "order": orders_db[order_id]
        }
    else:
        return {
            "success": False,
            "error": "Order not found"
        }

def initiate_return(order_id: str, reason: str) -> Dict:
    """Initiate a return for an order."""
    logger.info(f"Tool called: initiate_return with order_id={order_id}, reason={reason}")
    
    if order_id not in orders_db:
        return {
            "success": False,
            "error": "Order not found"
        }
    
    if orders_db[order_id]["status"] != "delivered":
        return {
            "success": False,
            "error": "Only delivered orders can be returned"
        }
    
    return {
        "success": True,
        "return_id": f"RET{order_id[3:]}",
        "message": f"Return initiated for order {order_id}",
        "instructions": "Please package the items and use the provided return label."
    }

def faq_lookup(query: str) -> Dict:
    """Look up information in the FAQ database."""
    logger.info(f"Tool called: faq_lookup with query={query}")
    
    # Simple matching - in a real system, this would be more sophisticated
    matches = {}
    query_lower = query.lower()
    
    for key, value in faq_db.items():
        if query_lower in key.lower():
            matches[key] = value
    
    if not matches:
        return {
            "success": False,
            "error": "No matching FAQs found"
        }
    
    return {
        "success": True,
        "matches": matches
    }

# Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Create or retrieve the assistant
def get_assistant():
    try:
        # Try to retrieve existing assistant first
        assistants = client.beta.assistants.list(
            order="desc",
            limit=100
        )
        
        for assistant in assistants.data:
            if assistant.name == config.ASSISTANT_NAME:
                logger.info(f"Found existing assistant with ID: {assistant.id}")
                return assistant.id
                
        # If not found, create a new one
        assistant = client.beta.assistants.create(
            name=config.ASSISTANT_NAME,
            instructions=config.ASSISTANT_INSTRUCTIONS,
            model=config.OPENAI_MODEL,
            tools=tool_definitions
        )
        logger.info(f"Created new assistant with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        logger.error(f"Error creating/retrieving assistant: {e}")
        raise

def process_tool_calls(run, thread_id):
    tool_outputs = []
    
    if run.required_action and run.required_action.type == "submit_tool_outputs":
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"Processing tool call: {function_name} with args: {function_args}")
            
            if function_name in tool_functions:
                result = tool_functions[function_name](**function_args)
            else:
                result = {"error": f"Unknown function: {function_name}"}
            
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
    
    return tool_outputs

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    try:
        assistant_id = get_assistant()
        
        # Create or retrieve thread
        if request.thread_id:
            thread_id = request.thread_id
            logger.info(f"Using existing thread with ID: {thread_id}")
        else:
            thread = client.beta.threads.create()
            thread_id = thread.id
            sessions[thread_id] = {
                "created_at": datetime.now().isoformat(),
                "user_id": request.user_id
            }
            logger.info(f"Created new thread with ID: {thread_id}")
        
        # Log user ID for personalization if provided
        if request.user_id and thread_id in sessions:
            sessions[thread_id]["user_id"] = request.user_id
            logger.info(f"Associated user ID {request.user_id} with thread {thread_id}")
            
        # Add the user's message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )
        logger.info(f"Added user message to thread {thread_id}: {request.message[:50]}...")
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        # Poll for completion or required actions
        while run.status in ["queued", "in_progress", "requires_action"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            # Handle tool calls
            if run.status == "requires_action":
                logger.info(f"Run requires action: {run.required_action.type}")
                tool_outputs = process_tool_calls(run, thread_id)
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
        
        # Check for errors
        if run.status == "failed":
            logger.error(f"Run failed: {run.last_error}")
            return {"response": "Sorry, I encountered an error processing your request.", "thread_id": thread_id}
        
        # Get the latest message from the assistant
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        
        # Find the first assistant message
        assistant_message = next(
            (msg for msg in messages.data if msg.role == "assistant"),
            None
        )
        
        if assistant_message:
            response_text = assistant_message.content[0].text.value
            logger.info(f"Assistant response: {response_text[:50]}...")
        else:
            response_text = "Sorry, I couldn't process your request."
            logger.warning(f"No assistant message found in thread {thread_id}")
            
        return {"response": response_text, "thread_id": thread_id}
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True) 