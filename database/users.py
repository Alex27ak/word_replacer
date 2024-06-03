from motor.motor_asyncio import AsyncIOMotorClient


class UserDatabase:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db["users"]

    async def create_user(self, user_id):
        return await self.col.insert_one(
            {
                "_id": user_id,
                "banned": False,
            }
        )

    async def get_user(self, user_id):
        return await self.col.find_one({"_id": user_id})

    async def get_all_users(self):
        return await self.col.find({}).to_list(length=None)

    async def update_user(self, user_id, data, tag="set"):
        await self.col.update_one({"_id": user_id}, {f"${tag}": data})

    async def delete_user(self, user_id):
        await self.col.delete_one({"_id": user_id})

    async def is_user_exist(self, user_id):
        return bool(await self.col.find_one({"_id": user_id}))

    async def filter_users(self, query):
        return await self.col.find(query).to_list(length=None)
