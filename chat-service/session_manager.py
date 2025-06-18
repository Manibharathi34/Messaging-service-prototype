from typing import Dict
import uuid
from typing import List
import difflib


class SessionManager:
    def __init__(self):
        self.user_client_map: Dict[str, str] = {}

    def get_user_client_id(self, user_id: str) -> str:
        if user_id not in self.user_client_map:
            self.user_client_map[user_id] = str(uuid.uuid4())
        return self.user_client_map[user_id]

    def get_user(self, user: str) -> List[str]:
        user = user.lower()
        all_users = [key for key in self.user_client_map]
        print(f"user={user} and all={all_users}")
        try:
            matches = difflib.get_close_matches(user, all_users, n=10, cutoff=0.5)
        except Exception as e:
            print(f"error is {e}")
        return matches
