"""
MongoDB connection and data access layer for TalentFlow HR Agent.
Uses motor (async) for FastAPI endpoints and pymongo (sync) for LangChain tools.
"""
import os
import logging
from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson import ObjectId

logger = logging.getLogger("talentflow.db")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = "talentflow"

# ---------------------------------------------------------------------------
# Async client — used by FastAPI route handlers
# ---------------------------------------------------------------------------
_async_client: Optional[AsyncIOMotorClient] = None

def get_async_db():
    global _async_client
    if _async_client is None:
        _async_client = AsyncIOMotorClient(MONGO_URI)
    return _async_client[DB_NAME]

# ---------------------------------------------------------------------------
# Sync client — used by LangChain tools (they run in a thread-pool, not async)
# ---------------------------------------------------------------------------
_sync_client: Optional[MongoClient] = None

def get_sync_db():
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return _sync_client[DB_NAME]

# ---------------------------------------------------------------------------
# Seed data (mirrors the hardcoded arrays in tools.py)
# ---------------------------------------------------------------------------

SEED_EMPLOYEES = [
    {"id": "E001", "name": "Priya Sharma",   "role": "Senior Backend Engineer",  "skills": ["Python", "FastAPI", "PostgreSQL", "AWS"],      "years_exp": 5, "department": "Engineering", "overtime_hrs_last_month": 42, "days_since_last_leave": 87,  "open_tickets": 18, "last_appraisal_months_ago": 14, "tenure_years": 5,  "email": "priya.sharma@talentflow.com"},
    {"id": "E002", "name": "Arjun Mehta",    "role": "Data Analyst",             "skills": ["SQL", "Python", "Tableau", "Excel"],            "years_exp": 3, "department": "Analytics",   "overtime_hrs_last_month": 8,  "days_since_last_leave": 12,  "open_tickets": 4,  "last_appraisal_months_ago": 6,  "tenure_years": 3,  "email": "arjun.mehta@talentflow.com"},
    {"id": "E003", "name": "Sara Khan",       "role": "HR Generalist",            "skills": ["Recruitment", "Onboarding", "HRMS", "Excel"],   "years_exp": 4, "department": "HR",          "overtime_hrs_last_month": 31, "days_since_last_leave": 60,  "open_tickets": 11, "last_appraisal_months_ago": 11, "tenure_years": 4,  "email": "sara.khan@talentflow.com"},
    {"id": "E004", "name": "Rahul Nair",      "role": "Frontend Engineer",        "skills": ["React", "TypeScript", "CSS", "Node.js"],        "years_exp": 2, "department": "Engineering", "overtime_hrs_last_month": 15, "days_since_last_leave": 22,  "open_tickets": 6,  "last_appraisal_months_ago": 5,  "tenure_years": 2,  "email": "rahul.nair@talentflow.com"},
    {"id": "E005", "name": "Meena Iyer",      "role": "Product Manager",          "skills": ["Roadmapping", "Agile", "SQL", "Figma"],         "years_exp": 6, "department": "Product",     "overtime_hrs_last_month": 50, "days_since_last_leave": 120, "open_tickets": 22, "last_appraisal_months_ago": 18, "tenure_years": 6,  "email": "meena.iyer@talentflow.com"},
    {"id": "E006", "name": "Dev Patel",       "role": "ML Engineer",              "skills": ["Python", "TensorFlow", "LangChain", "AWS"],     "years_exp": 4, "department": "AI",          "overtime_hrs_last_month": 20, "days_since_last_leave": 30,  "open_tickets": 7,  "last_appraisal_months_ago": 8,  "tenure_years": 4,  "email": "dev.patel@talentflow.com"},
    {"id": "E007", "name": "Ananya Roy",      "role": "Junior Backend Engineer",  "skills": ["Python", "Django", "MySQL"],                    "years_exp": 1, "department": "Engineering", "overtime_hrs_last_month": 5,  "days_since_last_leave": 8,   "open_tickets": 2,  "last_appraisal_months_ago": 3,  "tenure_years": 1,  "email": "ananya.roy@talentflow.com"},
]


async def seed_database():
    """Seed MongoDB with initial data if collections are empty."""
    try:
        db = get_async_db()

        # Seed employees
        if await db.employees.count_documents({}) == 0:
            await db.employees.insert_many(SEED_EMPLOYEES)
            logger.info(f"✅ Seeded {len(SEED_EMPLOYEES)} employees into MongoDB")
        else:
            count = await db.employees.count_documents({})
            logger.info(f"ℹ️  MongoDB already has {count} employees — skipping seed")

        # Create indexes
        await db.candidates.create_index("submitted_at")
        await db.emails.create_index("sent_at")
        logger.info("✅ MongoDB indexes created")

    except Exception as e:
        logger.warning(f"⚠️  MongoDB seed failed (is MongoDB running?): {e}")


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialisation."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
