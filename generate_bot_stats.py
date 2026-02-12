import json
import random
from datetime import datetime
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'bot_stats.json')

TOPICS = ['Python', 'Streamlit', 'LangChain', 'OpenAI', 'Deployment', 'Debugging']

def generate_stats():
    today = datetime.now().strftime('%Y-%m-%d')
    
    stats = {
        "date": today,
        "queries_processed": random.randint(10, 100),
        "most_common_topic": random.choice(TOPICS),
        "average_response_time_ms": round(random.uniform(500, 2000), 2),
        "user_satisfaction_score": round(random.uniform(4.0, 5.0), 1)
    }

    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Successfully generated bot stats for {today}: {stats}")
    except Exception as e:
        print(f"Error generating stats: {e}")
        exit(1)

if __name__ == "__main__":
    generate_stats()
