from typing import Optional
from tls_client import Session


class Joiner:
    def __init__(self) -> None:
        pass

    def joinGuild():
        ...


class DM:
    def __init__(self) -> None:
        pass

    def openDM():
        ...

    def sendDM():
        ...


class Friend:
    def __init__(self, client: Session) -> None:
        self.common_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Authorization": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "discord.com",
            "Origin": "https://discord.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-GB",
            "X-Discord-Timezone": "America/Chicago",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wKChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEyMC4wKSkpIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUzMDQ3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9",
        }
        self.client = client

    def send_friend_by_id(self, user_id: str, mutual_guild_id: str):
        # {"op": 14, "d": {"guild_id": mutual_guild_id, "members": [user_id]}}

        headers = {
            **self.common_headers,
            "Referer": f"https://discord.com/channels/{mutual_guild_id}",
            "X-Context-Properties": "eyJsb2NhdGlvbiI6IlVzZXIgUHJvZmlsZSJ9",  # {"location":"User Profile"}
        }
        url = f"https://discord.com/api/v9/users/@me/relationships/{user_id}"
        return self.client.put(url, headers=headers, json={})

    def send_friend_by_username(self, username: str, discrim: Optional[str] = None):
        headers = {
            **self.common_headers,
            "Referer": "https://discord.com/channels/@me",
            "X-Context-Properties": "eyJsb2NhdGlvbiI6IkFkZCBGcmllbmQifQ==",  # {"location":"Add Friend"}
        }
        url = "https://discord.com/api/v9/users/@me/relationships"
        payload = {"username": username, "discriminator": discrim}
        return self.client.post(url, headers=headers, json=payload)


class UDCord(Friend, DM, Joiner):
    def __init__(self) -> None:
        super().__init__()
