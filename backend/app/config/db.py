import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

logger = logging.getLogger("trust_sell.db")

class Database:
    client: AsyncIOMotorClient = None
    db = None
    is_connected: bool = False

    async def connect_to_database(self):
        """Initialize connection to MongoDB Atlas or local MongoDB."""
        self.is_connected = False
        self.db = None
        try:
            logger.info("Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            self.db = self.client[settings.DATABASE_NAME]

            # Simple ping command to verify the connection is alive
            await self.db.command("ping")
            self.is_connected = True
            logger.info(f"Successfully connected to MongoDB database: {settings.DATABASE_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            if self.client:
                self.client.close()
                self.client = None
            self.db = None

            if settings.ENV == "development":
                try:
                    from mongomock_motor import AsyncMongoMockClient

                    logger.warning(
                        "Using in-memory MongoDB mock for local development. "
                        "Install MongoDB for persistent data."
                    )
                    self.client = AsyncMongoMockClient()
                    self.db = self.client[settings.DATABASE_NAME]
                    await self.db.command("ping")
                    self.is_connected = True
                    return
                except Exception as mock_error:
                    logger.error(f"In-memory database fallback failed: {mock_error}")

            raise e

    async def close_database_connection(self):
        """Close connection to MongoDB."""
        if self.client:
            self.client.close()
            self.client = None
        self.db = None
        self.is_connected = False
        logger.info("MongoDB connection closed.")

# Instantiate database manager
db_manager = Database()

def get_db():
    """Dependency provider for retrieving the raw database connection."""
    return db_manager.db

def get_collection(name: str):
    """Helper to get a database collection quickly."""
    if not db_manager.is_connected or db_manager.db is None:
        raise RuntimeError(
            "Database is offline. Start MongoDB (localhost:27017) or set MONGODB_URL in backend/.env"
        )
    return db_manager.db[name]
