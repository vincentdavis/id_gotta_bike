import os
from typing import Literal

import aiohttp
import logfire
from discord.ext import commands, tasks
from pydantic import ValidationError

from src.schema import DiscordGuildJoinUpdatePost, DiscordJoinUpdateResponse


async def guild_build_post_data(guild, status: Literal["JOIN", "UPDATE"]) -> DiscordGuildJoinUpdatePost | None:
    """Build data for guild join API request."""
    with logfire.span(f"Build Guild Post data, ID: {guild.id}"):
        try:
            # Get owner's name if possible
            owner_name = guild.owner.name if guild.owner else None

            # Get icon URL if exists
            icon_url = str(guild.icon.url) if guild.icon else None

            # Get categories names and ids
            categories = [
                {
                    "name": cat.name,
                    "id": cat.id,
                    "channels": [{"name": chan.name, "id": chan.id} for chan in cat.channels],
                }
                for cat in guild.categories
            ]
            channels = [{"name": chan.name, "id": chan.id} for chan in guild.channels]

            roles = [{"name": r.name, "id": r.id} for r in guild.roles]

            default_role_id = str(guild.default_role.id) if guild.default_role else None

            # Prepare server data using new model
            post_data = DiscordGuildJoinUpdatePost(
                status=status,
                guild_id=str(guild.id),
                guild_name=guild.name,
                owner_name=owner_name,
                owner_id=str(guild.owner_id),
                member_count=guild.member_count,
                categories=categories,
                channels=channels,
                roles=roles,
                jump_url=guild.jump_url,
                large=guild.large,
                icon_url=icon_url,
                default_role_id=default_role_id,
                guild_birthday=guild.created_at,
            )
            logfire.info(f"Guild join data prepared, Guild ID: {guild.id}")
            return post_data
        except TypeError as e:
            logfire.error(f"TypeError: Guild join data prep failed. TypeError, Guild ID: {guild.id}\n {e!s}")
            return None
        except ValidationError as e:
            logfire.error(f"ValidationError: Guild join data prep failed. ValidationError, Guild ID: {guild.id}\n{e!s}")
            print(e)
            return None
        except AttributeError as e:
            logfire.error(f"AttributeError: Guild join data prep failed. AttributeError, Guild ID: {guild.id}\n {e!s}")
            return None
        except Exception as e:
            logfire.error(f"Exception: Guild join data prep failed. Other Exception {e!s}")
            return None


async def guild_post_join_update(post_data: DiscordGuildJoinUpdatePost) -> bool:
    """Send guild join update to API.

    Args:
        post_data: The guild join/update data to send

    Returns:
        bool: True if successful, False otherwise

    """
    with logfire.span(f"Post Guild Join, Update, ID: {post_data.guild_id}"):
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    f"{os.getenv('API_URL')}/guild/join_update/",
                    json=post_data.model_dump(mode="json"),
                    headers={"X-API-Key": os.getenv("API_KEY")},
                )
                if response.status == 200:
                    logfire.info(f"Successfully registered server: {post_data.guild_name} ({post_data.guild_id})")
                    data = await response.json()
                    logfire.info(f"API Response, validating: {data}")
                    try:
                        DiscordJoinUpdateResponse.model_validate(data)
                    except ValidationError as e:
                        logfire.error(f"Failed to validate response from API: {e!s}")
                        return False
                    return True
                else:
                    error_text = await response.text()
                    logfire.error(f"Failed to register server. Status: {response.status}, Error: {error_text}")
                    return False

        except ValidationError as e:
            logfire.error(f"Failed to validate response from API: {e!s}")
            return False
        except aiohttp.ClientError as e:
            logfire.error(f"Network error while processing guild join: {e!s}")
            return False
        except Exception as e:
            logfire.error(f"Error processing guild join for {post_data.guild_name} ({post_data.guild_id}): {e!s}")
        return False


class GuildJoin(commands.Cog):
    """Cog to handle new guild joins."""

    def __init__(self, bot):
        self.bot = bot
        self.api_url = f"{os.getenv('API_URL')}/api_v1/discord/guild/joined/"

    @commands.Cog.listener()
    async def on_guild_join(self, guild) -> bool:
        """Handle new guild join and send data to API."""
        with logfire.span("SERVER: New guild join"):
            post_data = await guild_build_post_data(guild, status="JOIN")
            if post_data is None:
                return False
            else:
                return await guild_post_join_update(post_data)


@tasks.loop(hours=12)
async def pust_guild_update(bot: commands.Bot):
    """Push guild update to API."""
    with logfire.span("SERVER: Push guild update"):
        try:
            guilds = bot.guilds
            for guild in guilds:
                try:
                    post_data = await guild_build_post_data(guild, status="UPDATE")
                    if post_data is None:
                        logfire.error(f"Failed to build guild update data for guild: {guild.name} ({guild.id})")
                        continue
                    else:
                        await guild_post_join_update(post_data)
                except Exception as e:
                    logfire.error(f"Error processing a guild update: {e!s}")

        except Exception as e:
            logfire.error(f"Error processing ALL guild updates: {e!s}")
            return False
        return True


def setup(bot):
    pust_guild_update.start(bot)
    bot.add_cog(GuildJoin(bot))
