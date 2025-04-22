import logging
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger(__name__)

# Mock databases
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


# Tool definitions for OpenAI Assistants API
tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the status of a customer's order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ID of the order to check"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "initiate_return",
            "description": "Start the return process for an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ID of the order to return"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the return"
                    }
                },
                "required": ["order_id", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "faq_lookup",
            "description": "Search the FAQ database for answers to common questions",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Question or keywords to search for in the FAQ"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Mapping function names to their implementations
tool_functions = {
    "get_order_status": get_order_status,
    "initiate_return": initiate_return,
    "faq_lookup": faq_lookup
} 