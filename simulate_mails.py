import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def send_dummy_email():
    client = MongoClient(MONGO_URI)
    db = client.salescatalyst
    
    print("\n --- SIMULATE INBOUND EMAIL ---")
    print("Available Leads:")
    print("1. LEAD-101 (Sarah - CTO, FinTech Global)")
    print("2. LEAD-102 (Marcus - IT Dir, HealthCare Partners)")
    print("3. LEAD-103 (Anya - CTO, NeuraLaunch AI)")
    
    lead_id = input("\nEnter the Lead ID sending the email (e.g., LEAD-103): ").strip()
    message = input("Enter their email message: ").strip()
    
    email_doc = {
        "lead_id": lead_id,
        "message": message,
        "timestamp": datetime.now(),
        "status": "Unread"
    }
    
    db.inbound_emails.insert_one(email_doc)
    print(f"\n SUCCESS: Email from {lead_id} delivered to the MongoDB Inbox!")

if __name__ == "__main__":
    send_dummy_email()