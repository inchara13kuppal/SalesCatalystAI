import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# Import your modular tools
from email_service import send_sales_email
from agent import run_sales_catalyst_agent 

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

app = Flask(__name__)
CORS(app) 

client = MongoClient(MONGO_URI)
db = client.salescatalyst

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Endpoint for the frontend to fetch and display all leads."""
    try:
        leads = list(db.crm_leads.find({}, {"_id": 0}).limit(20))
        return jsonify({"status": "success", "data": leads}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/run-agent', methods=['POST'])
def trigger_agent():
    """Triggers the AI Agent to process un-drafted Kaggle leads."""
    try:
        print(" Waking up AI Co-Pilot...")
        
        # 1. Find 1 lead to process (Limiting to 1 prevents the UI from timing out)
        pending_leads = list(db.crm_leads.find({"draft_status": "Not Started"}).limit(1))
        
        if not pending_leads:
            return jsonify({"status": "success", "logs": "No new leads require attention."}), 200

        # 2. Command the agent for this specific Kaggle lead
        for lead in pending_leads:
            lead_id = lead['lead_id']
            company = lead['company']
            pain_point = lead['pain_point']
            
            print(f"Commanding Agent to process {company} ({lead_id})...")
            
            # The dynamic prompt that connects your data to the AI
            prompt = f"""
            You are an expert Enterprise SDR. 
            Look up the lead with ID '{lead_id}' at the company '{company}'.
            Their primary pain point is: "{pain_point}".
            Call the `check_inbound_emails` tool to see if there are any unread messages from this lead.
            Draft a highly personalized sales email addressing their pain point and replying to any inbound messages.
            You MUST use the `save_draft_for_review` tool to save the final draft.
            """
            
            # TRIGGERING THE AI
            run_sales_catalyst_agent(custom_prompt=prompt)
            
        return jsonify({"status": "success", "logs": "Agent successfully processed the lead."}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/approve/<lead_id>', methods=['POST'])
def approve_lead(lead_id):
    """Endpoint to handle human-in-the-loop email approvals, edits, and live dispatch."""
    try:
        # 1. Fetch the lead info from MongoDB to get the recipient email address
        lead = db.crm_leads.find_one({"lead_id": lead_id})
        if not lead:
            return jsonify({"status": "error", "message": "Lead not found in database."}), 404

        # Grab the email field (handles 'email' or 'email_address' depending on your schema)
        recipient_email = lead.get("email") or lead.get("email_address")
        if not recipient_email:
            return jsonify({"status": "error", "message": "This lead does not have a valid email address associated."}), 400

        # 2. Capture the edited text sent from the React frontend
        data = request.json or {}
        edited_text = data.get("draft_text")

        # Determine final text content to send (fallback to existing draft if no edits made)
        final_email_content = edited_text if edited_text else lead.get("draft_text", "")
        
        if not final_email_content:
            return jsonify({"status": "error", "message": "No email content draft available to send."}), 400

        # 3. Fire the real email through your SMTP transmission service!
        # Converting linebreaks to HTML tags ensures formatting matches what was in your text box
        body_html = f"<html><body style='font-family: Arial, sans-serif;'>{final_email_content.replace('\n', '<br>')}</body></html>"
        subject = f"Optimizing Solutions for {lead.get('company', 'Your Team')}"
        
        email_sent = send_sales_email(
            to_email=recipient_email,
            subject=subject,
            body_html=body_html
        )

        if not email_sent:
            return jsonify({"status": "error", "message": "Failed to route email through SMTP server."}), 500

        # 4. If email transmission succeeds, update the database flags
        update_fields = {
            "draft_status": "Email Sent ", 
            "status": "Engaging"
        }
        if edited_text:
            update_fields["draft_text"] = edited_text

        db.crm_leads.update_one(
            {"lead_id": lead_id},
            {"$set": update_fields}
        )
        
        return jsonify({"status": "success", "message": f"Lead {lead_id} approved and email dispatched successfully!"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(" Starting SalesCatalyst API Server on http://localhost:5000...")
    app.run(debug=True, port=5000)