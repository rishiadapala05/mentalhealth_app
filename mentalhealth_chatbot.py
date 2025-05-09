import re
import random
from datetime import datetime
import requests
import json
import os

# Initialize conversation history
_conversation_history = {}

# Create a directory for user conversations if it doesn't exist
if not os.path.exists('user_conversations'):
    os.makedirs('user_conversations')

# Function to interact with Ollama API
def generate_ollama_response(messages, model="llama3:8b"):
    """
    Generate response using Ollama API
    """
    try:
        url = "http://localhost:11434/api/chat"  
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()['message']['content']
        else:
            print(f"Error from Ollama API: {response.status_code}, {response.text}")
            return "I'm having trouble processing your request right now. Please try again later."
    except Exception as e:
        print(f"Exception when calling Ollama API: {str(e)}")
        return "Sorry, I encountered an error while processing your request."

# Function to generate a response based on user input
def generate_response(user_input, user_id):
    """
    Generate a response based on user input and update conversation history
    """
    if user_id not in _conversation_history:
        _conversation_history[user_id] = []
    
    _conversation_history[user_id].append({"role": "user", "content": user_input})
    
    # Get response from Ollama
    ai_response = generate_ollama_response(_conversation_history[user_id])
    
    _conversation_history[user_id].append({"role": "assistant", "content": ai_response})
    
    # Save conversation to file
    save_conversation(user_id)
    
    return ai_response

# Function to generate affirmation
def generate_affirmation():
    """
    Generate a positive affirmation
    """
    prompt = "Provide a short positive affirmation to encourage someone who is feeling stressed or overwhelmed"
    messages = [{"role": "user", "content": prompt}]
    return generate_ollama_response(messages)

# Function to generate meditation guide
def generate_meditation_guide():
    """
    Generate a meditation guide
    """
    prompt = "Provide a 5-minute guided meditation script to help someone relax and reduce stress."
    messages = [{"role": "user", "content": prompt}]
    return generate_ollama_response(messages)

# Function to save conversation history
def save_conversation(user_id):
    """
    Save conversation history to file
    """
    if user_id in _conversation_history:
        with open(f'user_conversations/{user_id}_conversation.json', 'w') as f:
            json.dump(_conversation_history[user_id], f)

# Function to load conversation history
def load_conversation(user_id):
    """
    Load conversation history from file
    """
    try:
        with open(f'user_conversations/{user_id}_conversation.json', 'r') as f:
            _conversation_history[user_id] = json.load(f)
    except FileNotFoundError:
        _conversation_history[user_id] = []
    return _conversation_history[user_id]

# Function to clear chat history
def clear_chat_history(user_id):
    """
    Clear chat history for a user
    """
    if user_id in _conversation_history:
        _conversation_history[user_id] = []
        # Remove the file if it exists
        try:
            os.remove(f'user_conversations/{user_id}_conversation.json')
        except FileNotFoundError:
            pass

# Function to get chat history
def get_chat_history(user_id):
    """
    Get chat history for a user
    """
    if user_id not in _conversation_history:
        load_conversation(user_id)
    return _conversation_history[user_id]

# Backward compatibility with previous API
def process_message(message):
    """
    Process user message (for backward compatibility)
    """
    # Default user ID for compatibility with old code
    user_id = "default_user"
    
    response = generate_response(message, user_id)
    
    # Format in the style expected by existing code
    return {
        "isGreeting": False,
        "message": response,
        "emotion": "mixed",  # We don't detect emotions specifically now
        "questions": [],
        "motivation": response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Function to add to chat history (for backward compatibility)
def add_to_chat_history(user_id, message, is_bot=False):
    """
    Add a message to chat history (for backward compatibility)
    """
    if user_id not in _conversation_history:
        _conversation_history[user_id] = []
    
    _conversation_history[user_id].append({
        "role": "assistant" if is_bot else "user",
        "content": message
    })
    
    # Save conversation to file
    save_conversation(user_id)