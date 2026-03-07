"""
Quick MongoDB Atlas connection test.
Run from the talentflowHR folder:
    python test_atlas.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "")

if not MONGO_URI:
    print("❌ MONGO_URI not found in .env")
    sys.exit(1)

print(f"🔗 Connecting to: {MONGO_URI[:40]}...")

try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Force a real connection
    info = client.server_info()
    print(f"✅ Atlas connected! MongoDB version: {info['version']}")

    # Check/list databases
    db = client["talentflow"]
    collections = db.list_collection_names()
    print(f"✅ Database 'talentflow' accessible. Collections: {collections or '(empty — will be seeded on first run)'}")

    client.close()
    print("\n🎉 MongoDB Atlas is working correctly.")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nCheck:")
    print("  1. Your Atlas cluster is running (not paused)")
    print("  2. Your IP is whitelisted in Atlas → Network Access (or set 0.0.0.0/0 for all IPs)")
    print("  3. The username/password in MONGO_URI is correct")
    sys.exit(1)
