import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

print("1. Script started...")
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
print(f"2. MONGO_URI loaded from .env: {'Found (hidden for safety)' if MONGO_URI else 'MISSING'}")

def seed_database():
    if not MONGO_URI:
        print(" Error: MONGO_URI not found in .env file.")
        return

    try:
        print("3. Attempting to connect to MongoDB Atlas cluster...")
        # Adding a 5-second timeout so it doesn't freeze forever if blocked by a firewall
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        print("4. Sending ping to database to verify connection...")
        client.admin.command('ping')
        print(" 5. Connected successfully to MongoDB Atlas!")
        
        db = client.salescatalyst
        
        print("6. Clearing old tables...")
        db.inventory.drop()
        db.crm_leads.drop()
        
        inventory_data = [
            {
                "product_id": "PROD-001",
                "name": "Zero-Trust Cloud Shield",
                "category": "Cloud Security",
                "target_audience": "CTOs, VP of Engineering",
                "key_benefit": "Eliminates lateral movement in cloud environments.",
                "in_stock": True,
                "price_tier": "Enterprise ($50k/yr)"
            },
            {
                "product_id": "PROD-002",
                "name": "Endpoint Protection Plus",
                "category": "Device Security",
                "target_audience": "IT Directors",
                "key_benefit": "AI-driven malware detection with zero-day prevention.",
                "in_stock": True,
                "price_tier": "Mid-Market ($15k/yr)"
            }
        ]
        db.inventory.insert_many(inventory_data)
        print(f"7. Seeded {len(inventory_data)} inventory items.")

        leads_data = [
            {
                "lead_id": "LEAD-101",
                "name": "Sarah Jenkins",
                "title": "Chief Technology Officer",
                "company": "FinTech Global",
                "status": "Stalled",
                "last_engagement": "Attended Zero-Trust Webinar in Q1",
                "pain_point": "Currently struggling with securing remote developer access.",
                "draft_status": "Not Started" 
            },
            {
                "lead_id": "LEAD-102",
                "name": "Marcus Rossi",
                "title": "Director of IT Operations",
                "company": "HealthCare Partners",
                "status": "Cold",
                "last_engagement": "Downloaded Endpoint Security Whitepaper",
                "pain_point": "Dealing with legacy antivirus systems slowing down hospital workstations.",
                "draft_status": "Not Started"
            }
        ]
        db.crm_leads.insert_many(leads_data)
        print(f"8. Seeded {len(leads_data)} CRM leads.")
        print(" Final Status: Database seeding completely finished.")

    except (ConnectionFailure, OperationFailure) as e:
        print(f" MongoDB Connection Error details: {e}")
    except Exception as e:
        print(f" Unexpected Error: {e}")

if __name__ == "__main__":
    print("0. Main execution block triggered.")
    seed_database()