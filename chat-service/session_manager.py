from typing import Dict, List
from db.db import DataBase

db = DataBase()


class SessionManager:

    user_client_map: Dict[str, str] = {}

    async def get_user_id(self, username: str) -> str:

        if username in self.user_client_map:
            return self.user_client_map[username]
        user_id = await db.get_user_by_name(username)
        print(f"userid frm db is {user_id}")
        if not user_id:
            user_id = await db.create_users(
                username=username, email=f"{username}@test.com"
            )
            print(f"newly created user id {user_id}")
        self.user_client_map[username] = user_id
        return user_id

    # def get_user(self, user: str) -> List[str]:
    #    user = user.lower()
    #    all_users = [key for key in self.user_client_map]
    #    matches = difflib.get_close_matches(user, all_users, n=10, cutoff=0.5)
    #    return matches

    def get_user(self, user: str) -> List[str]:
        user = user.lower()
        return [
            u for u in self.user_client_map if user in u.lower() and u.lower() != user
        ][:10]

    async def search_users(self, query: str) -> List[str]:
        results = await db.search_users_by_name(query)
        users = [r["username"] for r in results]
        return users
