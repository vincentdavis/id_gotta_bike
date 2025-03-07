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

    @bot.slash_command(name="about")
    async def about(ctx):
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
        website_link = "https://app.gotta.bike"
        invite_link = "https://discord.gg/vY3XXwdnmt"
        dev_help = "https://app.gotta.bike/development/development_help/"
        github_link = "https://github.com/id-gotta-bike/discord-gotta-bike"
        install_link = "https://discord.com/oauth2/authorize?client_id=1317880120173924434"

        await ctx.response.send_message(
            f"Hello, {name}, this is the Gotta.Bike Bot!\n"
            f"Your running at Guild: id, {ctx.guild.name}: {ctx.guild.id}\n"
            f"----\n"
            f"Website: <{website_link}>\n"
            f"GOTTA.BIKE Discord Server: <{invite_link}>\n"
            f"Bot Install link: <{install_link}>\n"
            f"----\n"
            f"Contributions, feedback, suggestions and beta testers are welcome\n"
            f"If you would like to help, here is how: <{dev_help}>\n"
            f"If you want to contribute, please visit the project on GitHub:\n"
            f"<{github_link}>\n"
            f"Contact me, Vincent Davis, at <{dm_link}>\n"
            f"----\n"
            f"Diagnostics"
            f"Logging {os.getenv('LOGFIRE_ENVIRONMENT')} environment\n"
            f"API server test response: {api_server_responded}\n"
            f" server_version: {data.get('server_version', 'N/A')}\n"
            f" Other: {data.get('other', 'N/A')}",
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
