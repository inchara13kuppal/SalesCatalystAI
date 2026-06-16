import os
import pandas as pd
import random
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. EXTRACT: Load credentials and connect to the database
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

print(" Starting ETL Pipeline...")
client = MongoClient(MONGO_URI)
db = client.salescatalyst

try:
    # Read the raw CSV file using Pandas
    print(" Reading raw data from Kaggle CSV...")
    df = pd.read_csv('sales_pipeline.csv')
    
    # 2. TRANSFORM: Clean and reshape the data to match our schema
    print(" Transforming data (Feature Engineering)...")
    
    # Drop rows that are completely empty to prevent database errors
    df = df.dropna(how='all')
    
    # Map Kaggle's columns to our Agent's expected schema
    # Rename 'opportunity_id' to 'lead_id', 'account' to 'company'
    df = df.rename(columns={'opportunity_id': 'lead_id', 'account': 'company'})
    
    # Standardize the 'status' column so our agent understands it
    status_mapping = {
        'Engaging': 'Stalled',
        'Prospecting': 'Cold',
        'Won': 'Closed',
        'Lost': 'Dead'
    }
    df['status'] = df['deal_stage'].map(status_mapping).fillna('Cold')
    
    # FEATURE ENGINEERING: Synthesize missing data that our AI Agent requires
    job_titles = ["Chief Technology Officer", "VP of Engineering", "IT Director", "Chief Information Security Officer"]
    pain_points = [
        "Struggling with remote multi-cloud access.",
        "Legacy systems slowing down team efficiency.",
        "Overwhelmed by compliance and SOC2 audit preparation.",
        "Needs rapid setup of firewall controls."
    ]
    company_sizes = ["Startup", "Mid-Market", "Enterprise"]
    
    # Assigning random realistic values to fill the gaps in the dataset
    df['title'] = [random.choice(job_titles) for _ in range(len(df))]
    df['pain_point'] = [random.choice(pain_points) for _ in range(len(df))]
    df['company_size'] = [random.choice(company_sizes) for _ in range(len(df))]
    df['name'] = "Contact at " + df['company'].astype(str) # Placeholder for missing names
    df['draft_status'] = "Not Started"
    
    # Select ONLY the columns our MongoDB schema actually needs
    final_columns = ['lead_id', 'name', 'title', 'company', 'company_size', 'status', 'pain_point', 'draft_status']
    df_clean = df[final_columns].head(100)
    
    # 🐛 THE SILVER BULLET BUG FIX
    # 1. Fill standard blanks with "Unknown"
    df_clean = df_clean.fillna("Unknown") 
    # 2. Force EVERY column to become a safe string so JSON serialization never fails
    df_clean = df_clean.astype(str)       
    # 3. Catch any Pandas float NaNs that sneaked through and became the literal string "nan"
    df_clean = df_clean.replace("nan", "Unknown") 
    
    # 3. LOAD: Push the cleaned data to MongoDB
    print(f" Pushing {len(df_clean)} cleaned records to MongoDB Atlas...")
    
    # Convert the Pandas DataFrame into a list of Python dictionaries
    records_to_insert = df_clean.to_dict(orient='records')
    
    # Clear old data and insert the new Kaggle data
    db.crm_leads.drop()
    db.crm_leads.insert_many(records_to_insert)
    
    print(" SUCCESS: ETL Pipeline complete. Real Kaggle data is now live and NaN-free in MongoDB.")

except Exception as e:
    print(f"❌ ETL Error: {e}")