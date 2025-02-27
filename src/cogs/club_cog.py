import os
from datetime import datetime

import discord
import httpx
import logfire
from discord import ButtonStyle, Color, Embed, ui
from discord.ext import commands


class CubCog(commands.Cog):
    """Cyclist related cogs."""

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    # @discord.slash_command(name="my_clubs", description="Get a link to manage your club admin access")
    # async def my_clubs(self, ctx):
    #     """Get a link to manage your club admin access."""
    #     with logfire.span("Get club admin link"):
    #         headers = {"X-API-Key": os.getenv("API_KEY")}
    #         url = f"{os.getenv('API_URL')}/my_clubs/{ctx.author.id}"
    #
    #         try:
    #             async with httpx.AsyncClient() as client:
    #                 logfire.info(f"Getting club link for {ctx.author}:{ctx.author.id}")
    #                 logfire.info(f"Request: {url}")
    #                 response = await client.get(url, headers=headers)
    #
    #                 logfire.info(f"Response: {response.status_code}")
    #                 if response.status_code == 200:
    #                     data = response.json()
    #                     # Create embed message
    #                     embed = Embed(
    #                         title="My Clubs",
    #                         description="Click the button below to manage your clubs",
    #                         color=Color.blue(),
    #                     )
    #
    #                     # Add admin count field
    #                     admin_text = f"You are admin in {data['is_admin_count']} club{'s' if data['is_admin_count'] != 1 else ''}"
    #                     embed.add_field(name="Admin Status", value=admin_text, inline=False)
    #
    #                     membership_text = (
    #                         f"You are a member of {data['club_count']} club{'s' if data['club_count'] != 1 else ''}"
    #                     )
    #                     embed.add_field(name="Membership Status", value=membership_text, inline=False)
    #
    #                     # Add expiration field - API returns link that expires in 1 hour
    #                     logfire.info(f"Get expires at: {data['expires_at']}")
    #                     expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
    #                     embed.add_field(name="Link Expires", value=f"<t:{int(expires_at.timestamp())}:R>", inline=False)
    #
    #                     # Create button with the URL
    #                     logfire.info(f"Magic link: {data['magic_link']}")
    #                     view = ui.View()
    #                     view.add_item(ui.Button(label="Manage Clubs", url=data["magic_link"], style=ButtonStyle.link))
    #
    #                     await ctx.respond(embed=embed, view=view, ephemeral=True)
    #                 else:
    #                     error_data = response.json()
    #                     await ctx.respond(
    #                         f"❌ Error getting club admin link, Make sure you have registed with '/my_profile': {error_data.get('detail', 'Unknown error')}",
    #                         ephemeral=True,
    #                     )
    #         except Exception as e:
    #             logfire.error(f"Error in club_admin command: {e!s}")
    #             await ctx.respond(
    #                 "❌ An error occurred while getting your club admin link. Please try again later.",
    #                 ephemeral=True,
    #             )


def setup(bot):
    bot.add_cog(CubCog(bot))
