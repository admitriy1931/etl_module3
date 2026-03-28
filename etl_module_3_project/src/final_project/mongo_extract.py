"""Extract documents from MongoDB collections."""

from typing import List, Dict, Any

from pymongo.database import Database as MongoDatabase

from utils.logger import get_logger

log = get_logger(__name__)

COLLECTIONS = [
    "user_sessions",
    "event_logs",
    "support_tickets",
    "user_recommendations",
    "moderation_queue",
]


def extract_collection(db: MongoDatabase, collection_name: str) -> List[Dict[str, Any]]:
    """Extract all documents from a MongoDB collection."""
    docs = list(db[collection_name].find({}, {"_id": 0}))
    log.info("Extracted %d documents from '%s'", len(docs), collection_name)
    if not docs:
        log.warning("Collection '%s' is empty", collection_name)
    return docs


def extract_all(db: MongoDatabase) -> Dict[str, List[Dict[str, Any]]]:
    """Extract all collections at once."""
    result = {}
    for coll_name in COLLECTIONS:
        result[coll_name] = extract_collection(db, coll_name)
    return result
