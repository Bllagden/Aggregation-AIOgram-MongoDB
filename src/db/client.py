from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient

from settings import MongoSettings, get_settings

_mongodb_settings = get_settings(MongoSettings)

client: AgnosticClient = AsyncIOMotorClient(_mongodb_settings.uri)
db: AgnosticDatabase = client.sampleDB
collection: AgnosticCollection = db.sample_collection
