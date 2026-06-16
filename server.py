import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, jsonify, request

#  THE MAGIC LINK: Import your agent directly!
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
            
            #  TRIGGERING THE AI
            run_sales_catalyst_agent(custom_prompt=prompt)
            
        return jsonify({"status": "success", "logs": "Agent successfully processed the lead."}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/approve/<lead_id>', methods=['POST'])
def approve_lead(lead_id):
    """Endpoint to handle human-in-the-loop email approvals and edits."""
    try:
        # Capture the edited text sent from the React frontend
        data = request.json or {}
        edited_text = data.get("draft_text")

        # Prepare the fields to update
        update_fields = {
            "draft_status": "Email Sent ", 
            "status": "Engaging"
        }
        
        # If the SDR edited the text, update the database with their new version
        if edited_text:
            update_fields["draft_text"] = edited_text

        # Update MongoDB
        db.crm_leads.update_one(
            {"lead_id": lead_id},
            {"$set": update_fields}
        )
        
        return jsonify({"status": "success", "message": f"Lead {lead_id} approved!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(" Starting SalesCatalyst API Server on http://localhost:5000...")
    app.run(debug=True, port=5000)