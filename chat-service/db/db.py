from db.db_connection import database
from db.models import users, chats, messages
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert
import uuid


class DataBase:
    async def create_users(self, username: str, email: str = "") -> str:
        user_id = str(uuid.uuid4())
        query = """
            INSERT INTO users (id, username, email)
            VALUES (:id, :username, :email)
        """
        print(f"query is {query}")
        result = await database.execute(
            query, values={"id": user_id, "username": username, "email": email}
        )
        print(f"user insert result is {result}")
        return user_id

    async def get_user_by_name(self, name: str):
        query = "SELECT username FROM users WHERE lower(username) = lower(:name)"
        return await database.fetch_one(query, values={"name": name})

    async def get_or_create_chat(self, sender_id: str, receiver_id: str) -> int:
        a, b = sorted([sender_id, receiver_id])

        # PostgreSQL-specific: use ON CONFLICT DO NOTHING + RETURNING
        insert_query = (
            pg_insert(chats)
            .values(sender=a, receiver=b)
            .on_conflict_do_nothing(index_elements=["sender", "receiver"])
            .returning(chats.c.id)
        )

        chat_id = await database.fetch_val(insert_query)

        if chat_id:
            return chat_id

        # If insert did nothing (because row existed), fetch existing chat ID
        select_query = select(chats.c.id).where(
            and_(chats.c.sender == a, chats.c.receiver == b)
        )
        existing_id = await database.fetch_val(select_query)
        return existing_id

    async def save_message(self, chat_id: int, text: str) -> int:
        query = messages.insert().values(chat_id=chat_id, text=text)
        return await database.execute(query)

    async def get_chat_messages(self, chat_id: int, limit: int = 50):
        query = """
            SELECT
                id,
                chat_id,
                sender_id,
                text,
                TO_CHAR(time AT TIME ZONE 'UTC' AT TIME ZONE 'US/Pacific', 'YYYY-MM-DD HH24:MI:SS') AS formatted_time
            FROM messages
            WHERE chat_id = :chat_id
            ORDER BY time DESC
            LIMIT :limit
        """
        return await database.fetch_all(
            query, values={"chat_id": chat_id, "limit": limit}
        )

    async def search_users_by_name(self, query: str, limit: int = 10):
        sql = """
            SELECT id, username
            FROM users
            WHERE username ILIKE :pattern
            ORDER BY username
            LIMIT :limit
        """
        values = {"pattern": f"%{query}%", "limit": limit}
        results = await database.fetch_all(query=sql, values=values)
        return results
