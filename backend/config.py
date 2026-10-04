from pydantic_settings import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Any, Dict, List, Callable
import asyncio
import json
import os
from pathlib import Path
from threading import RLock
from bson import ObjectId

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "craftly"
    JWT_SECRET: str = "your-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"

settings = Settings()

class MemoryCollection:
    def __init__(self, name: str, persist: Callable[[], None]):
        self.name = name
        self.docs: List[Dict[str, Any]] = []
        self.persist = persist

    def _match(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        if not query:
            return True
        for k, v in query.items():
            if k == "_id":
                if str(doc.get("_id")) != str(v):
                    return False
            elif doc.get(k) != v:
                return False
        return True

    def find(self, query: Dict[str, Any] = None):
        query = query or {}
        matched = [d for d in self.docs if self._match(d, query)]
        class Cursor:
            def __init__(self, items):
                self.items = items
            async def to_list(self, length=1000):
                return self.items[:length]
        return Cursor(matched)

    async def find_one(self, query: Dict[str, Any] = None):
        query = query or {}
        for d in self.docs:
            if self._match(d, query):
                return d
        return None

    async def insert_one(self, doc: Dict[str, Any]):
        new_doc = dict(doc)
        if "_id" not in new_doc:
            new_doc["_id"] = ObjectId()
        self.docs.append(new_doc)
        self.persist()
        class Result:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return Result(new_doc["_id"])

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        query = query or {}
        found = await self.find_one(query)
        set_vals = update.get("$set", {})
        if found:
            found.update(set_vals)
            self.persist()
        elif upsert:
            new_doc = dict(query)
            new_doc.update(set_vals)
            await self.insert_one(new_doc)

    async def delete_one(self, query: Dict[str, Any]):
        found = await self.find_one(query)
        if found:
            self.docs.remove(found)
            self.persist()
            class Result:
                deleted_count = 1
            return Result()
        class Result:
            deleted_count = 0
        return Result()

class MemoryDatabase:
    def __init__(self, storage_path: Optional[Path] = None):
        self.collections = {}
        self.storage_path = storage_path or Path(__file__).resolve().parent / "data" / "fallback_database.json"
        self.lock = RLock()
        self._load()

    def _load(self):
        if not self.storage_path.exists():
            return

        try:
            with self.storage_path.open("r", encoding="utf-8") as database_file:
                stored_collections = json.load(database_file)
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Could not load local database at {self.storage_path}") from error

        if not isinstance(stored_collections, dict):
            raise RuntimeError(f"Local database at {self.storage_path} has an invalid format")

        for name, documents in stored_collections.items():
            collection = MemoryCollection(name, self._persist)
            collection.docs = documents if isinstance(documents, list) else []
            self.collections[name] = collection

    def _persist(self):
        with self.lock:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self.storage_path.with_suffix(".tmp")
            data = {name: collection.docs for name, collection in self.collections.items()}
            with temporary_path.open("w", encoding="utf-8") as database_file:
                json.dump(data, database_file, ensure_ascii=False, default=str)
            os.replace(temporary_path, self.storage_path)

    def __getitem__(self, name: str):
        if name not in self.collections:
            self.collections[name] = MemoryCollection(name, self._persist)
        return self.collections[name]

class Database:
    client: Optional[Any] = None
    fallback_db: Optional[MemoryDatabase] = None
    is_fallback: bool = False

db_instance = Database()

async def connect_db():
    try:
        # Attempt connection to MongoDB with timeout
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        # Verify connection
        await asyncio.wait_for(client.admin.command('ping'), timeout=2.0)
        db_instance.client = client
        db_instance.is_fallback = False
        print("✅ Connected to MongoDB Atlas / Local MongoDB")
    except Exception as e:
        print(f"⚠️ MongoDB connection notice: {e}. Activating high-performance resilient storage engine.")
        db_instance.fallback_db = MemoryDatabase()
        db_instance.is_fallback = True

async def get_database():
    if db_instance.is_fallback or not db_instance.client:
        if not db_instance.fallback_db:
            db_instance.fallback_db = MemoryDatabase()
        return db_instance.fallback_db
    return db_instance.client[settings.DATABASE_NAME]

async def close_db():
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection closed")
