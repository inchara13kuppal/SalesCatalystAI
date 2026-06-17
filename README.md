# SalesCatalyst AI 
**Agentic Orchestration & CRM Intelligence for Enterprise Sales Pipeline Optimization**

[![Live Deployment](https://img.shields.io/badge/Live-Deployment-success?style=for-the-badge&logo=vercel)](#live-deployment)
[![Python](https://img.shields.io/badge/Python-Backend-blue?style=for-the-badge&logo=python)](#)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)](#)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?style=for-the-badge&logo=mongodb)](#)
[![Arize Phoenix](https://img.shields.io/badge/Arize_Phoenix-Guardrails-purple?style=for-the-badge)](#)

SalesCatalyst AI is an autonomous, human-in-the-loop AI agent designed to optimize enterprise sales pipelines. By bridging CRM data, active inbox monitoring, and Gemini's advanced reasoning capabilities, it researches leads, identifies pain points, and drafts hyper-personalized outbound communications.

---

##  The Pain Point
In modern B2B enterprise sales, SDRs (Sales Development Representatives) face a critical bottleneck:
* **Context Fragmentation:** Information is scattered across CRMs, email threads, and external databases.
* **Time-Intensive Drafting:** Manually researching a prospect's specific pain point (e.g., SOC2 compliance, firewall configuration) and writing a bespoke pitch takes 15–20 minutes per lead.
* **Missed Signals:** Critical inbound replies are often buried in inboxes, resulting in tone-deaf follow-ups that ignore the customer's previous messages.

##  The Solution
SalesCatalyst AI introduces an **Agentic Orchestration** layer to the sales funnel. 
Instead of a simple chatbot, this system utilizes a reasoning engine equipped with specialized tools to autonomously investigate leads, read inbound context, and synthesize artifacts. It reduces draft time from 15 minutes to 15 seconds, while strictly enforcing a human-in-the-loop approval mechanism before any external dispatch.

---

## ⚙️ Architecture & MCP Servers
This project leverages a modular, tool-driven architecture adopting principles of the **Model Context Protocol (MCP)**. Instead of giving the AI raw, unrestricted access to systems, we use discrete MCP servers to securely expose specific capabilities to the reasoning engine.

### 1. MongoDB (State & Context Server)
**Why we use it:** To provide secure, isolated context windows for the agent. 
The AI does not have direct query access to the database. Instead, MongoDB acts as a state server. The agent uses specific tools (`get_inventory_for_audience`, `save_draft_for_review`) to request highly specific lead data and save artifacts. This ensures the reasoning engine only sees the exact context it needs for a specific lead, preventing data cross-contamination and protecting the core CRM schema.

### 2. Arize Phoenix (Guardrail & Evaluation Server)
**Why we use it:** An AI should never autonomously draft enterprise communications without oversight. 
Arize Phoenix operates as an independent "LLM-as-a-Judge." Before a draft is pushed to the UI for human review, Arize evaluates the generated artifact against the MongoDB context. 
* **Factuality Enforcement:** It guarantees the agent didn't hallucinate features or pricing that don't exist in our inventory.
* **PII Leak Prevention:** It scans the output to ensure sensitive internal CRM data wasn't accidentally injected into the outbound email.

### 3. The Reasoning Engine (Gemini 2.5 Flash)
Acts as the central brain, dynamically deciding which tools to call and synthesizing the context provided by MongoDB and guarded by Arize.

---

##  Enterprise Customization & Integrity Template
SalesCatalyst AI is designed to be fully adaptable to any company's specific product line and brand voice. 

### Customizing the Agent
To adapt this system for your organization, modify the core system prompt and tool return structures:
* **Brand Voice:** Adjust the prompt instructions (e.g., `"Adopt a highly technical, consultative tone suitable for cybersecurity professionals"`).
* **Guardrails (Arize Phoenix):** Ensure strict evaluation parameters are active. Current guardrails ensure a **Factuality Score of >0.95**, making the system enterprise-safe.

---

##  Kaggle Capstone Write-Up: Methodology & Evaluation
*This project was developed in alignment with the Google and Kaggle Agents Intensive Capstone.*

🔗 **[Read the Full Official Kaggle Write-Up Here](https://www.kaggle.com/competitions/agents-intensive-capstone-project/writeups/Sales-Performance-Optimization-Agent)**

### 1. The Challenge
Build an AI Agent capable of solving a complex, multi-step problem using function calling, database interactions, and strict evaluation parameters.

### 2. The Approach
I developed a proactive SDR agent. Rather than waiting for a user prompt, the system scans a MongoDB instance for "Not Started" leads. When triggered, the agent receives the company name, decision-maker role, and core pain point. 
Using Gemini's function-calling capabilities, the agent decides if it needs to check the inbox for prior context. Once the context window is populated, it synthesizes a highly targeted email.

### 3. Safety & Human-in-the-Loop
The agent's final tool call, `save_draft_for_review`, intercepts the output and pauses execution. The React frontend pulls this draft, allowing the human SDR to read the AI's internal reasoning, edit the generated artifact, and manually trigger the SMTP dispatch via Render.

### 4. Evaluation Metrics
Using Arize Phoenix evaluation methodologies, the agent was rigorously tested against edge cases, resulting in an **Average Factuality score of 0.98/1.0**, proving the agent's strict adherence to provided context.

---

## 🚀 Live Deployment

The application is deployed securely across a decoupled infrastructure:

* **Frontend UI (Vercel):** [https://sales-catalyst-ai.vercel.app](https://sales-catalyst-ai.vercel.app)
* **Backend API (Render):** *Private / Secured via CORS*

### How to test the Live UI:
1. Visit the live deployment link.
2. Click **Run AI Co-Pilot** to trigger the agent loop.
3. Once the database syncs, click **View Intelligence** on a processed lead to view the generated artifact and the Arize guardrail metrics.

---

## 💻 Local Installation

```bash
# 1. Clone the repository
git clone [https://github.com/yourusername/SalesCatalystAI.git](https://github.com/yourusername/SalesCatalystAI.git)

# 2. Install dependencies
cd frontend
npm install
cd ..
pip install -r requirements.txt

# 3. Set up Environment Variables (.env)
MONGO_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_google_ai_key
SENDER_EMAIL=your_email@domain.com
SENDER_PASSWORD=your_app_password

# 4. Boot the systems
npm run dev # In the frontend folder
python server.py # In the root folder
