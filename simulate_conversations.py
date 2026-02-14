import json
import random
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'bot_stats.json')

INTENTS = ['Order Status', 'Product Info', 'Return Policy', 'Technical Support', 'Billing']

def simulate_conversations():
    # Load existing data or create new structure
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = {"history": []}
    else:
        # Create directory if needed
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        data = {"history": []}

    # Simulate a batch of cleaning
    # Keep only last 50 entries
    if len(data["history"]) > 50:
        data["history"] = data["history"][-50:]
        
    # Generate new session data
    session = {
        "timestamp": datetime.now().isoformat(),
        "total_messages": random.randint(2, 15),
        "primary_intent": random.choice(INTENTS),
        "avg_response_time_ms": random.randint(50, 800),
        "user_satisfaction": random.randint(1, 5),
        "resolution_status": random.choice(['Resolved', 'Escalated', 'Pending'])
    }
    
    data["history"].append(session)
    
    # Calculate aggregate metrics
    total_rating = sum(s["user_satisfaction"] for s in data["history"])
    avg_rating = round(total_rating / len(data["history"]), 2)
    data["average_satisfaction"] = avg_rating

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Simulated conversation: {session['primary_intent']} - Satisfaction: {session['user_satisfaction']}/5")

if __name__ == "__main__":
    simulate_conversations();
