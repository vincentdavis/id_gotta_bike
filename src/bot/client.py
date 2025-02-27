"""Primary Client class that runs the bot"""

import os

import discord as pycord
import httpx
import logfire


def init_bot():
    """Initialize the bot."""
    # with logfire.span("STARTING BOT"):
    logfire.info("Load pycord intents")
    try:
        intents = pycord.Intents.default()
        intents.members = True
        logfire.info("members + Intents loaded successfully!")

    except Exception as e:
        logfire.error(f"Failed to load pycord intents: {e}")
        logfire.info("Defaulting to all intents")
        intents = pycord.Intents.default()

    logfire.info(f"Intents: {intents}")

    logfire.info("Initialize bot")
    bot = pycord.Bot(command_prefix="!", intents=intents)
    logfire.info("Run bot")

    @bot.event
    async def on_ready():
        """Sync commands."""
        try:
            logfire.info("Syncing commands with Discord...")
            await bot.sync_commands()
            logfire.info("Commands synced successfully!")
        except Exception as e:
            logfire.error(f"Failed to sync commands: {e}")
        logfire.info("Bot is now ready!")

    @bot.slash_command()
    async def id_gotta_bike_info(ctx):
        """Information about the  ID Discord Gotta Bike bot. and app.gotta.bike."""
        with logfire.span("id_gotta_bike_info"):
            logfire.info(f"Guild ID: {ctx.guild.id}")
            logfire.info(f"Guild Name: {ctx.guild.name}")
            logfire.info(f"API_URL: {os.getenv('API_URL')}")
            logfire.info(f"API_KEY: {os.getenv('API_KEY')[:3]}")
            logfire.info(f"LOGFIRE_TOKEN: {os.getenv('LOGFIRE_TOKEN', 'BLANK')[:3]}")
            logfire.info(f"LOGFIRE_ENVIRONMENT: {os.getenv('LOGFIRE_ENVIRONMENT')}")
            logfire.info(f"DISCORD_BOT_TOKEN: {os.getenv('DISCORD_BOT_TOKEN')[:3]}")

            # Test the connection to the API server
            try:
                api_test_url = f"{os.getenv('API_URL')}/api_test"
                logfire.info(f"Testing API connection: {api_test_url}")
                async with httpx.AsyncClient() as client:
                    response = await client.get(api_test_url)
                    response.raise_for_status()
                    data = response.json()
                    logfire.info(
                        f"API Test Successful!\n"
                        f"source_ip: {data.get('source_ip', 'failed')}\n"
                        f" server_version: {data.get('server_version', 'failed')}\n"
                        f" Other: {data.get('other', 'failed')}"
                    )
                    api_server_responded = "PASSED" if data.get("source_ip", "failed") != "failed" else "FAILED"
            except httpx.HTTPError as http_err:
                logfire.error(f"HTTP error while connecting to API: {http_err}")
                api_server_responded = "HTTP error while connecting to API"
            except Exception as e:
                logfire.error(f"Unexpected error during API testing: {e}")
                api_server_responded = "Unexpected API error during testing"

        name = ctx.author.name
        dm_link = "https://discord.com/users/588793677317537811"

        await ctx.response.send_message(
            f"Hello, {name}, This is the ID_Discrod_Gotta_Bike Bot!\n"
            f"The source code is available at https://github.com/id-gotta-bike/discord-gotta-bike\n"
            f"Your running this on {ctx.guild.name}: {ctx.guild.id} Guild/Server\n"
            f"This the {os.getenv('LOGFIRE_ENVIRONMENT')} environment\n"
            f"If you have question, issues... DM me, Vincent Davis at {dm_link}\n"
            f"API server test response: {api_server_responded}\n",
            ephemeral=True,
        )

    # bot.load_extension("src.cogs.club_cog")
    bot.load_extension("src.cogs.cyclist_cog")
    bot.load_extension("src.cogs.server_cog")

    logfire.info("Get: DISCORD_BOT_TOKEN")

    if not os.getenv("DISCORD_BOT_TOKEN"):
        logfire.error("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
        raise ValueError("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
    logfire.info("Bot started: if your here it has stopped")


# if __name__ == "__main__":
#     print(pycord.__version__)
#     TOKEN = os.getenv("DISCORD_BOT_TOKEN")
#     if not TOKEN:
#         raise ValueError("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file."
