# E-Commerce Customer Support Agent

An agentic system built with OpenAI Agents SDK that simulates a customer support assistant for an e-commerce website.

<img width="953" alt="image" src="https://github.com/user-attachments/assets/d3067f38-e71c-425b-8a73-3f6aa8513295" />


## Features

- Natural language interactions with customers
- Order status inquiries
- Return initiation
- FAQ lookup
- Conversation memory across multiple turns
- User ID personalization
- Tool invocation logging

## Requirements

- Python 3.8+
- OpenAI API key

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```
4. Add your OpenAI API key to the `.env` file

## Security Note

- Never commit your `.env` file with real API keys to version control
- The `.env` file is included in `.gitignore` to prevent accidental exposure
- When deploying, use environment variables or secure secrets management

## Running the API

Start the FastAPI server:

```
python main.py
```

The API will be available at http://localhost:8000

## API Endpoints

### POST /chat

Send a message to the customer support agent.

Request body:
```json
{
  "message": "Where is my order ORD123456?",
  "thread_id": "optional_thread_id_for_continuing_conversations",
  "user_id": "optional_user_id_for_personalization"
}
```

Response:
```json
{
  "response": "Your order ORD123456 has been shipped and is expected to be delivered by June 15, 2024. The tracking number is TRK789012.",
  "thread_id": "thread_id_for_continuing_the_conversation"
}
```

## Example Interactions

### Order Status Check
```
User: "I ordered some sneakers last week, order number ORD123456. Where are they?"
Agent: "Your order ORD123456 has been shipped and is expected to be delivered by June 15, 2024. The tracking number is TRK789012."
```

### Return Initiation
```
User: "I want to return my headphones from order ORD789012. They don't work properly."
Agent: "I've initiated a return for your order ORD789012. Your return ID is RET789012. Please package the items and use the provided return label."
```

### FAQ Query
```
User: "What's your return policy?"
Agent: "You can return any item within 30 days of purchase for a full refund."
```

## License

MIT
