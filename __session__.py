from websocket import WebSocket, WebSocketConnectionClosedException
from json import dumps, loads
from terminut import printf as print
from asyncio import sleep, create_task
from re import search
from .types.websocket import ReadyData, D_Data


class SessionManager:
    def __init__(
        self,
        user_agent,
        build_num,
        device_type,
        capabilities_num,
        cst_presence: dict = None,
    ):
        self.session_id = None
        self.session_task = None
        self.session_on = False
        self.socket_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive, Upgrade",
            "Host": "gateway.discord.gg",
            "Origin": "https://discord.com",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate",
            "User-Agent": user_agent,
        }
        self.ws = WebSocket()

        self.user_agent = user_agent
        self.build_num = build_num
        self.device_type = device_type
        self.capabilities_num = capabilities_num
        self.custom_presence = cst_presence
        browser_patterns = {
            "Discord Client": r"discord/([\d.]+)",
            "Chrome": r"Chrome/([\d.]+)",
            "Firefox": r"Firefox/([\d.]+)",
            "Edge": r"Edge/([\d.]+)",
            "Safari": r"Safari/([\d.]+)",
            "Opera": r"OPR/([\d.]+)|Opera/([\d.]+)",
        }

        for browser, pattern in browser_patterns.items():
            match = search(pattern, user_agent)
            if match:
                self.browser = browser
                self.bversion = match.group(1)

    async def _wsconn(self, token) -> [ReadyData, str]:
        self.ws.connect(
            "wss://gateway.discord.gg/?encoding=json&v=9", header=self.socket_headers
        )
        message = {
            "op": 2,
            "d": {
                "token": token,
                "capabilities": self.capabilities_num,
                "properties": {
                    "os": "Windows",
                    "browser_user_agent": self.user_agent,
                    "device": "",
                    "system_locale": "en-US",
                    "release_channel": "stable",
                    "client_build_number": self.build_num,
                    "client_event_source": None,
                },
                "presence": {
                    "status": "online",
                    "since": 0,
                    "activities": [],
                    "afk": False,
                }
                if not self.custom_presence
                else self.custom_presence,
                "compress": False,
                "client_state": {
                    "guild_versions": {},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1,
                    "user_settings_version": -1,
                    "private_channels_version": "0",
                    "api_code_version": 0,
                },
            },
        }

        if self.device_type == "browser":
            message["d"]["properties"]["browser"] = str(self.browser)
            message["d"]["properties"]["browser_version"] = str(self.bversion)
            message["d"]["properties"]["os_version"] = "10"
            message["d"]["properties"]["referrer"] = ("",)
            message["d"]["properties"]["referring_domain"] = ("",)
            message["d"]["properties"]["referrer_current"] = ("",)
            message["d"]["properties"]["referring_domain_current"] = ("",)
        elif self.device_type == "app":
            message["d"]["properties"]["browser"] = "Discord Client"
            message["d"]["properties"]["browser_version"] = "22.3.2"
            message["d"]["properties"]["client_version"] = "1.0.9015"
            message["d"]["properties"]["os_version"] = "10.0.22621"
            message["d"]["properties"]["os_arch"] = "x64"
            message["d"]["properties"]["native_build_number"] = 32266
        # elif self.device_type == "mobile":
        #     message["d"]["properties"] = {
        #         "os": "iOS",
        #         "browser": "Discord iOS",
        #         "device": "iPhone14,5",
        #         "system_locale": "en-US",
        #         "client_version": "202.0",
        #         "release_channel": "stable",
        #         "device_vendor_id": "",
        #         "browser_user_agent": "",
        #         "browser_version": "",
        #         "os_version": "17.0",
        #         "client_build_number": 51852,
        #         "client_event_source": None,
        #         "design_id": 0
        #     }

        else:
            raise ValueError(
                "An invalid device_type was provided for getSession() | Acceptable values: ['browser', 'app']"
            )

        self.ws.send(dumps(message))
        self.ws.send(
            dumps(
                {
                    "op": 4,
                    "d": {
                        "guild_id": None,
                        "channel_id": None,
                        "self_mute": False,
                        "self_deaf": False,
                        "self_video": False,
                        "flags": 2,
                    },
                }
            )
        )
        READY_DATA = "unfetched"
        for _ in range(5):
            try:
                result = loads(self.ws.recv())
            except WebSocketConnectionClosedException as e:
                return "invalid token", "invalid token"
            except:
                continue
            
            if result.get("op") == 9:
                print("Invalid token provided.")
                self.ws.close()
                return None, "Invalid token"
                
            if result.get("t") == "READY":
                READY_DATA = ReadyData(
                    t=result.get("t"),
                    s=result.get("s"),
                    op=result.get("op"),
                    d=D_Data(**result.get("d")),
                )
            if "heartbeat_interval" in dumps(result):
                self.rpBeat = result["d"].get("heartbeat_interval")
            if "session_id" in dumps(result):
                self.session_id = result["d"].get("session_id")
                break
        return READY_DATA, self.session_id

    async def keepSessionAlive(self, showHB):
        while self.session_on:
            try:
                self.ws.send(dumps({"op": 1, "d": 10}))
                if showHB:
                    print(f"(*) Sent HB. | Next: {self.rpBeat/1000}s")
                await sleep(self.rpBeat / 1000)
            except Exception as e:
                print(f"(!) Error sending HB: {e}")
                break

    async def get_session(
        self, token: str, keep_alive: bool = False, show_hb: bool = False
    ) -> [ReadyData, str]:
        try:
            ready_data, session_id = await self._wsconn(token)
            if keep_alive:
                # print("[WARN] KeepAlive is experimental.", showTimestamp=False)
                self.session_on = True
                self.session_task = create_task(self.keepSessionAlive(show_hb))
                return ready_data, session_id
            else:
                return ready_data, session_id
        except KeyboardInterrupt:
            if self.session_on:
                self.session_on = False  # Stop the keep-alive loop
                await self.session_task  # Wait for the task to complete
            return

    def get_active_ws(self):
        return self.ws
        

    def close_session(self):
        self.session_on = False
        if self.session_task is None:
            return print("(!) Cannot close an unopened session.")
        self.session_task.cancel()
