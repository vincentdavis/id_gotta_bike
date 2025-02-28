# Response model
import re
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, field_validator


class DiscordGuildJoinUpdatePost(BaseModel):
    """POST data model to the /guild/join_update/ API endpoint.

    Copied from the api server
    """

    status: Literal["JOIN", "UPDATE"]  # to track is this is an update or new server join, just for logging
    guild_id: str = Field(..., min_length=17, max_length=19, description="Discord server snowflake ID (17-19 digits)")
    guild_name: str | None = Field(None, max_length=255)
    owner_name: str | None = Field(None, max_length=255)
    owner_id: str | None = Field(None, min_length=17, max_length=19)
    member_count: int | None = None
    categories: list[Any] = Field(default_factory=list)
    channels: list[Any] = Field(default_factory=list)
    roles: list[Any] = Field(default_factory=list)
    jump_url: AnyUrl | None = None
    large: bool = False
    icon_url: AnyUrl | None = None
    default_role_id: str | None = Field(None, min_length=17, max_length=19)
    guild_birthday: datetime | None = None

    @field_validator("guild_id", "owner_id", "default_role_id")
    def validate_discord_id(cls, v):
        """Validate Discord ID numbers."""
        if v is not None and not re.match(r"^\d{17,19}$", v):
            raise ValueError("Discord ID must be a string of 17-19 digits")
        return v

    class Config:  # noqa: D106
        json_encoders = {datetime: lambda v: v.isoformat()}  # noqa: RUF012
        json_schema_extra = {  # noqa: RUF012
            "example": {
                "guild_id": "123456789012345678",
                "guild_name": "My Discord Server",
                "owner_name": "Server Owner",
                "owner_id": "123456789012345678",
                "member_count": 100,
                "categories": [],
                "channels": [],
                "roles": [],
                "jump_url": "https://discord.com/channels/123456789012345678",
                "large": False,
                "icon_url": "https://cdn.discordapp.com/icons/123456789012345678/abcdef.png",
                "default_role_id": "123456789012345678",
                "guild_birthday": "2024-01-01T00:00:00Z",
            }
        }


class DiscordJoinUpdateResponse(BaseModel):
    """Copied from API server."""

    status: bool
    guild_created: bool
    club_created: bool


class DiscordMagicLinkResponse(BaseModel):
    """Copied from api server."""

    uuid: UUID | None = None
    expires_at: datetime
    url: str


class LocalGetMagicLinkResponse(BaseModel):
    """get_magic_link method."""

    status_code: int
    status_message: str
    api: str
    discord_id: str | int
    guild_id: str | int
    guild_name: str
    url: str | None
    expires_at: datetime | None
    uuid: UUID | None


class Cyclist(BaseModel):
    first_name: str
    last_name: str
    usac_id: int | None = None
    uci_id: int | None = None
    zwift_id: int
    strava_id: int | None = None
    discord_id: int
    ids: dict | None = None
    created: datetime
    modified: datetime

    class Config:
        extra = "allow"


class ZRacing(BaseModel):
    uuid: UUID
    riderId: int
    name: str
    gender: str
    country: str
    height: float
    weight: float
    zpCategory: str
    zpFTP: int
    power: dict
    race: dict
    handicaps: dict
    phenotype: dict
    created: datetime
    modified: datetime

    class Config:
        extra = "allow"


class LookUpAthlete(BaseModel):  # noqa: D101
    status_code: int
    status_message: str
    athlete: Cyclist | None = None
    zracing: ZRacing | None = None

    class Config:  # noqa: D106
        extra = "allow"


class AthleteResponseDiscord(BaseModel):  # noqa: D101
    uuid: UUID
    first_name: str
    last_name: str
    usac_id: int | None = None
    uci_id: int | None = None
    zwift_id: int | None = None
    strava_id: int | None = None
    discord_id: str | None = None
    ids: dict | None = None
    created: datetime
    changed: datetime

    class Config:
        extra = "allow"


# Create Pydantic models for request validation
class CyclistCreate(BaseModel):
    first_name: str
    last_name: str
    birth_year: int
    usac_id: int | None = None
    uci_id: int | None = None
    zwift_id: int | None = None
    strava_id: int | None = None
    discord_id: str
    ids: dict | None = {}


class CyclistUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    usac_id: int | None = None
    uci_id: int | None = None
    zwift_id: int | None = None
    strava_id: int | None = None
    discord_id: str
    ids: dict | None = None


class DiscordServerJoin(BaseModel):
    server_id: str
    server_name: str
    owner_id: str
    member_count: int
    server_created_at: datetime
    installed_by: str | None = None


# Response model
class DiscordServerResponse(BaseModel):
    uuid: UUID
    server_id: str
    server_name: str
    owner_id: str
    member_count: int
    server_created_at: datetime
    is_installed: bool
    installed_date: datetime
    installed_by: str | None = None
    created: datetime
    changed: datetime

    class MagicLink(BaseModel):
        uuid: UUID
        token: str
