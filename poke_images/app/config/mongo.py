from pymongo import MongoClient,ASCENDING
from pymongo.collection import Collection



from app.config.settings import api_settings


__all__ = ("client")

client = MongoClient(api_settings.MONGO_URI)
logs: Collection = client[api_settings.MONGO_DATABASE][api_settings.MONGO_LOG_COLLECION]
pokemons: Collection = client[api_settings.MONGO_DATABASE][api_settings.MONGO_POKEMON_COLLECTION]