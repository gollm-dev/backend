from pymongo import MongoClient
import motor.motor_asyncio
import config
#
# client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI)
# db = client.gollm
#
# sync_client = MongoClient(config.MONGO_URI)
# sync_db = sync_client.gollm
client = MongoClient(config.MONGO_URI)
db = client.gollm
