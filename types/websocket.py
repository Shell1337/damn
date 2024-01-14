from dataclasses import dataclass, fields, field
from typing import Optional


@dataclass
class ClientInfo:
    version: int
    os: str
    client: str


@dataclass
class UserData:
    verified: bool
    username: str
    purchased_flags: int
    pronouns: str
    premium_type: int
    premium: bool
    phone: str
    nsfw_allowed: bool
    mobile: bool
    mfa_enabled: bool
    id: str
    has_bounced_email: bool
    global_name: str
    flags: int
    email: str
    discriminator: str
    desktop: bool
    bio: str
    banner_color: str
    banner: str
    avatar_decoration_data: str
    avatar: str
    accent_color: str


@dataclass
class SessionData:
    status: str
    session_id: str
    client_info: ClientInfo
    activities: list


@dataclass
class UserGuildSettings:
    version: int
    partial: bool
    entries: list


@dataclass
class Tutorial:
    indicators_suppressed: bool
    indicators_confirmed: list


@dataclass
class ReadState:
    version: int
    partial: bool
    entries: list


@dataclass
class NotificationSettings:
    flags: int


@dataclass
class D_Data:
    v: int
    users: list
    user_guild_settings: UserGuildSettings
    user: UserData
    tutorial: Tutorial
    sessions: list
    session_type: str
    session_id: str
    resume_gateway_url: str
    relationships: list
    read_state: ReadState
    private_channels: list
    notification_settings: NotificationSettings
    merged_members: list
    guilds: list
    guild_join_requests: list
    guild_experiments: list
    geo_ordered_rtc_regions: list
    friend_suggestion_count: int
    experiments: list
    current_location: list
    country_code: str
    consents: dict
    connected_accounts: list
    auth_session_id_hash: str
    auth: dict
    api_code_version: int
    analytics_token: str
    _trace: list

    user_settings_proto: Optional[str] = None
    required_action: Optional[str] = None


@dataclass
class ReadyData:
    t: str
    s: int
    op: int
    d: D_Data
