#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: github.com/imvast
@Date: 7/31/2023
"""

from .__session__ import SessionManager

from base64 import b64encode
from json import dumps
from tls_client import Session
from typing import Optional, Literal, List, Union, Tuple
from json import dumps
from .types.websocket import ReadyData
from requests import get
from re2 import search, findall
from asyncio import run, gather
from httpx import AsyncClient
from .types.device import AgentProperties, DiscordProperties, Agents


# def timeit(func): # debugging
#     def wrapper(*args, **kwargs):
#         start_time = time()
#         result = func(*args, **kwargs)
#         end_time = time()
#         execution_time = end_time - start_time
#         print(f"Function '{func.__name__}' took {execution_time:.6f} seconds to execute.")
#         return result
#     return wrapper


class HTTPClient:
    def __init__(self):
        self.session = Session(
            client_identifier="firefox_119", random_tls_extension_order=True
        )


class VeilCord:
    def __init__(
        self,
        session: Optional[Session] = HTTPClient().session,
        device_type: Literal["browser", "mobile", "app"] = "browser",
        user_agent: Optional[str] = None,
        device_version: Optional[str] = None,
        build_num: Optional[int] = None,
    ) -> None:
        self.session = HTTPClient().session if session is None else session
        self.currentBuildNUM = VeilCord.getBuildNum() if not build_num else build_num
        self.currentCapNum = VeilCord.getCapabilitiesNum()
        self.device_type = device_type
        
        if device_type == "browser":
            self.agent = Agents.Browser()
        elif device_type == "mobile":
            self.agent = Agents.Mobile()
        elif device_type == "app":
            self.agent = Agents.Desktop()
        else:
            raise ValueError(
                "An invalid device_type was provided. Acceptable values: ['browser', 'mobile', 'app']"
            )
            
        self.user_agent = self.agent.user_agent if user_agent is None else user_agent

        try:
            self.browser, self.bversion = AgentProperties.extract_browser(self.user_agent)
        except:
            self.browser = "Firefox"
            self.bversion = device_version if device_version else "119.0"

    # session mg

    def openSession(self, custom_rpc: dict = None) -> SessionManager:
        return SessionManager(
            self.user_agent,
            self.currentBuildNUM,
            self.device_type,
            self.currentCapNum,
            custom_rpc,
        )

    def getSession(
        self,
        token: str,
        session: SessionManager = None,
        keep_alive: bool = False,
        show_hb: bool = False,
    ) -> Tuple[ReadyData, Union[str, None]]:
        if session is None:
            session = SessionManager(
                self.user_agent,
                self.currentBuildNUM,
                self.device_type,
                self.currentCapNum,
            )
            if keep_alive:
                raise SyntaxError("Session cannot be null with keepAlive enabled.")
        ready_data, session_id = run(session.get_session(token, keep_alive, show_hb))
        return ready_data, session_id

    def closeSession(self, session):
        session.close_session()
        return True

    def generateXProp(
        self, browser_vers: Optional[str] = None, build_num: Optional[int] = None
    ):
        xsup_common = {
            "os": self.agent.device_type,
            "system_locale": "en-US",
            "browser_user_agent": self.user_agent,
            "browser_version": self.bversion,
            "browser": "",
            "device": "",
            "release_channel": "stable",
            "client_build_number": build_num if build_num else self.currentBuildNUM,
        }
        if self.device_type == "mobile":
            xsup = {
                "os": self.agent.device_type,
                "browser": "Discord Android",
                "device": "RMX2117L1",
                "system_locale": "en-US",
                "client_version": "177.21 - rn",
                "release_channel": "googleRelease",
                "device_vendor_id": "c3c29b3e-4e06-48ff-af49-ec05c504c63e",
                "os_version": "31",
                "client_build_number": 1750160087099,
            }
        elif self.device_type == "browser":
            xsup = {
                **xsup_common,
                "browser": self.browser,
                "os_version": "10",
            }
        elif self.device_type == "app":
            xsup = {
                **xsup_common,
                "browser": self.browser,
                "client_version": browser_vers if browser_vers else "1.0.9023",
                "os_version": "10.0.22621",
                "os_arch": "x64",
                "browser_version": "22.3.2",
                "native_build_number": 35236,
            }
        else:
            raise ValueError(
                "An invalid type for generateXProp() was provided. Acceptable values: ['browser', 'mobile', 'app']"
            )

        xsup["client_event_source"] = None
        xsup["referrer"] = ""
        xsup["referring_domain"] = ""
        xsup["referrer_current"] = ""
        xsup["referring_domain_current"] = ""

        return b64encode(dumps(dict(sorted(xsup.items())), separators=(",", ":")).encode()).decode()

    def getFingerprint(
        self,
        xsup: Optional[str] = None,
        withCookies: Optional[bool] = True,
        cookieType: Literal["json", "cookiejar"] = "cookiejar",
        custom_headers: dict = None,
    ) -> Union[str, List[str]]:
        if not xsup:
            xsup = self.generateXProp()
        if self.device_type == "mobile":
            headers = (
                {
                    "Host": "discord.com",
                    "X-Super-Properties": xsup,
                    "Accept-Language": "en-US",
                    "X-Discord-Locale": "en-US",
                    "X-Debug-Options": "bugReporterEnabled",
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/json",
                }
                if not custom_headers
                else custom_headers
            )
        elif self.device_type == "browser":
            headers = (
                {
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.5",
                    "connection": "keep-alive",
                    "host": "discord.com",
                    "referer": "https://discord.com/",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": self.user_agent,
                    "x-debug-options": "bugReporterEnabled",
                    "x-discord-locale": "en-US",
                    "x-super-properties": xsup,
                }
                if not custom_headers
                else custom_headers
            )
        elif self.device_type == "app":
            headers = (
                {
                    "authority": "discord.com",
                    "accept": "*/*",
                    "accept-language": "en-US",
                    "connection": "keep-alive",
                    "content-type": "application/json",
                    "origin": "https://discord.com",
                    "referer": "https://discord.com/",
                    "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": self.user_agent,
                    "x-debug-options": "bugReporterEnabled",
                    "x-discord-locale": "en-US",
                    "x-discord-timezone": "America/New_York",
                    "x-super-properties": xsup,
                }
                if not custom_headers
                else custom_headers
            )
        else:
            raise ValueError(
                "An invalid type for getFingerprint() was provided. Acceptable values: ['browser', 'mobile', 'app']"
            )
        response = self.session.get(
            "https://discord.com/api/v9/experiments", headers=headers
        )
        if withCookies:
            cookies = (
                response.cookies
                if cookieType == "cookiejar"
                else dumps(response.cookies.get_dict())
            )
            return response.json().get("fingerprint"), cookies
        return response.json().get("fingerprint")

    # non self #

    @staticmethod
    async def fetch_build_num(session, match):
        try:
            bn_file = f"https://discord.com{match}"
            response = await session.get(bn_file)
            bn_res = response.text
            if "buildNumber:" in bn_res:
                bn_index = bn_res.find("buildNumber:") + 13
                BUILD_NUM = int(bn_res[bn_index : bn_index + 6])
                return BUILD_NUM
        except:
            pass

    @staticmethod
    def getBuildNum() -> int:
        """
        Fetches the current discord build number. 
        - Currently takes about 1.2 seconds.

        Returns:
            int: The current build number
        """
        async def async_getBuildNum():
            try:
                async with AsyncClient() as session:
                    res = await session.get("https://discord.com/login")
                    res.raise_for_status()
                    matches = list(
                        reversed(findall(r'<script src="([^"]+)"[^>]*>', res.text))
                    )

                    tasks = [VeilCord.fetch_build_num(session, match) for match in matches]
                    results = await gather(*tasks)

                    for result in results:
                        if result is not None:
                            return result

                    return 245033
            except:
                return 245033
        return run(async_getBuildNum())

    @staticmethod
    def getCapabilitiesNum() -> int:
        return 16381
        try:
            cookie = {
                "OptanonConsent": "isIABGlobal=false&datestamp=Thu+Jul+27+2023+21%3A05%3A10+GMT-0400+(Eastern+Daylight+Time)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1",
            }

            resp_welcome = get("https://discord.com/welcome/", cookies=cookie)
            script_links = findall(r'<script[^>]+src="([^"]+)"', resp_welcome.text)
            last_script_link = script_links[-1]

            resp_script = get("https://discord.com" + last_script_link)
            script_content = resp_script.text

            cappattern = r"capabilities:(\d+)"
            match = search(cappattern, script_content)

            return int(match.group(1)) if match else 16381
        except:
            return 16381  # last known

    def extractCode(invite) -> Union[str, None]:
        """Extracts the invite code from a Discord invite link"""
        code_regex = r"(?:(?:http:\/\/|https:\/\/)?discord\.gg\/|discordapp\.com\/invite\/|discord\.com\/invite\/)?([a-zA-Z0-9-]+)"
        match = search(code_regex, invite)
        if match:
            try:
                return match.group(1)
            except:
                return match.group(0)
        else:
            return None
