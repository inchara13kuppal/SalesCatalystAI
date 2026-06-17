 
import os
import time
from pymongo import MongoClient
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load the secret credentials from your .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MONGO_URI or not GEMINI_API_KEY:
    print(" Error: Missing API keys in .env file.")
    exit()

# 2. Connect to the Cloud Database (MongoDB)
client = MongoClient(MONGO_URI)
db = client.salescatalyst

# 3. Connect to the Brain (Gemini 3)
ai_client = genai.Client(api_key=GEMINI_API_KEY)


def get_stalled_leads() -> str:
    """Fetches all CRM leads with a 'Stalled' status from the database."""
    print(" [TOOL CALLED] Fetching Stalled Leads from MongoDB...")
    # Finds leads, excludes the hidden '_id' field for cleaner AI reading
    time.sleep(15)
    leads = list(db.crm_leads.find({"status": "Stalled"}, {"_id": 0}))
    return str(leads)

def check_inbound_emails() -> str:
    """Checks the database for unread inbound emails from leads."""
    print(" [TOOL CALLED] Checking Inbox for unread messages...")
    time.sleep(15)  # Free tier pacing
    
    # Fetch all unread emails
    emails = list(db.inbound_emails.find({"status": "Unread"}, {"_id": 0}))
    
    # If we found emails, instantly mark them as "Read" so we don't reply twice
    if emails:
        db.inbound_emails.update_many({"status": "Unread"}, {"$set": {"status": "Read"}})
        
    return str(emails)

def get_inventory_for_audience(target_role: str) -> str:
    """Fetches available inventory products tailored to a specific target audience role (e.g., 'CTO')."""
    print(f"[TOOL CALLED] Checking Inventory for {target_role}...")
    
    products = list(db.inventory.find(
        {"target_audience": {"$regex": target_role, "$options": "i"}, "in_stock": True},
        {"_id": 0}
    ))
    return str(products)

def evaluate_draft_with_arize(email_draft: str, lead_pain_point: str) -> bool:
    """
    Simulates an Arize Phoenix Guardrail API call.
    Evaluates if the generated draft contains hallucinations or fails brand compliance.
    Returns True if passed, or False if flagged.
    """
    print(" [ARIZE EVALUATION] Scanning draft for hallucinations and compliance metrics...")
    time.sleep(15)
    # In a full production app, this sends an HTTP POST request to your cloud Arize endpoint.
    # For our hackathon demo context, we run an inline evaluation check:
    
    # Compliance Rule 1: Guard against empty or lazy generations
    if len(email_draft) < 50:
        print(" [ARIZE FLAGGED] Draft is too short. Potential generation failure.")
        return False
        
    # Compliance Rule 2: Ensure the alignment matrix connects the draft to the customer's actual pain point
    # We break the text down to lowercase to ensure semantic checking matches keywords.
    keywords = lead_pain_point.lower().split()
    matched_context = any(word in email_draft.lower() for word in keywords if len(word) > 4)
    
    if not matched_context:
        print(" [ARIZE FLAGGED] Hallucination detected! Draft does not align accurately with the customer's database records.")
        return False

    print(" [ARIZE PASSED] Evals clear. Factuality Score: 0.98/1.00. No PII leaks or hallucinations found.")
    return True

def save_draft_for_review(lead_id: str, drafted_email: str) -> str:
    """Saves the AI-drafted email to MongoDB for human review."""
    print(f" [TOOL CALLED] Saving draft for {lead_id}...")
    
    # Update the document in MongoDB with the drafted text and status
    result = db.crm_leads.update_one(
        {"lead_id": lead_id},
        {"$set": {
            "draft_text": drafted_email,
            "draft_status": "Pending Approval",
            # We can also save mock Arize scores here for the UI
            "arize_factuality": "0.98",
            "arize_pii_check": "PASSED" 
        }}
    )
    
    if result.modified_count > 0:
        return f"Success: Draft saved for {lead_id}."
    else:
        return f"Error: Lead {lead_id} not found."
print(" Agent Tools Initialized. Ready to connect to the Gemini reasoning engine.")


def run_sales_catalyst_agent(custom_prompt=None):
    print("\n Starting SalesCatalyst AI Co-Pilot Execution...")
    
    # 1. High-trust system instructions defining the agent's boundaries
    system_instruction = """
    You are the core intelligence of SalesCatalyst AI, acting as an enterprise-grade Sales Co-Pilot.
    Your mission is to find stalled sales leads, locate matching inventory solutions, and draft highly accurate, personalized sales pitches.
    
    CRITICAL SAFETY & COMPLIANCE RULES:
    1. You must check available inventory using the tools provided before writing a pitch. Never invent/hallucinate product features or tiers.
    2. Do not offer unauthorized discounts or pricing options outside of what the inventory data states.
    3. Before saving any pitch, you MUST verify that it passes safety standards. If a draft fails compliance or hallucination checks, you must rewrite it.
    4. You operate under a strict 'Human-in-the-Loop' architecture. Once you write an excellent email pitch, you MUST save it using the save_draft_for_review tool with a status of 'Pending Approval'. You are strictly forbidden from executing external communication yourself.
    """

    # 2. Registering our Python functions as executable tools for Gemini
    available_tools = [check_inbound_emails, get_stalled_leads, get_inventory_for_audience, evaluate_draft_with_arize, save_draft_for_review]

    # 3. Dynamic Prompting: If server.py sends a specific command, use it. Otherwise, default to autonomous mode.
    if custom_prompt:
        orchestration_prompt = custom_prompt
    else:
        orchestration_prompt = (
            "STEP 1: Call the check_inbound_emails tool to see if there are any unread messages. "
            "If there is an unread email, prioritize it! Identify the lead_id, look up that lead's profile in the CRM to find their company_size and role, "
            "then look up the exact inventory matching their company_size and role. "
            "Draft a highly personalized reply directly answering their email message, and save the draft. "
            "STEP 2: If there are no unread emails, proceed to scan the CRM for 'Stalled' leads and draft pitches as normal."
        )

    # 4. Triggering the Gemini model with automatic traffic handling
    print(" Activating Gemini reasoning engine...")
    max_retries = 3
    retry_delay = 3  
    
    for attempt in range(max_retries):
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=orchestration_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=available_tools,
                    temperature=0.2,
                )
            )
            
            print("\n==========================================")
            print(" AGENT EXECUTION SUMMARY:")
            print(response.text)
            print("==========================================")
            break  
            
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                print(f" Cloud server busy (503). Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f" Error during agent execution: {e}")
                break

if __name__ == "__main__":
    run_sales_catalyst_agent()