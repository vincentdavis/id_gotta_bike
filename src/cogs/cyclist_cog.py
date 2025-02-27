import discord
import httpx
import logfire
from discord import ButtonStyle, Color, Embed, ui
from discord.ext import commands, tasks

from src.api import format_handicaps, format_phenotype, get_magic_link, lookup_cyclist


class CyclistCog(commands.Cog):
    """Cyclist related cogs."""

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    # @discord.slash_command()  # we can also add application commands
    # async def cyclist_goodbye(self, ctx):
    #     """Say goodbye to the bot. Just for fun."""
    #     await ctx.respond("Goodbye!")

    @commands.Cog.listener()  # we can add event listeners to our cog
    async def on_member_join(self, member):
        """Triggered When a member joins the server.

        - you must enable the proper intents
        - to access this event.
        - See the Popular-Topics/Intents page for more info
        """
        # TODO, look up the club setting and return with more info
        with logfire.span("CyclistCog.on_member_join"):
            logfire.info(f"{member} joined the server!")
            await member.send("Welcome to the server!")

    @tasks.loop(minutes=1)
    async def very_useful_task(self):
        """Very useful task just for testing purposes."""
        logfire.info("Doing very useful stuff...")
        print("doing very useful stuff.")

    @discord.slash_command()
    async def cyclist_lookup(self, ctx, user: discord.Member):
        """Look up a user in the registration database."""
        with logfire.span("CyclistCog.cyclist_lookup"):
            logfire.info(f"Looking up user: {user}")
            data = await lookup_cyclist(discord_id=str(user.id))
            if data.status_code != 200:
                logfire.error(f"success message: {data.status_code}, {data.status_message}")
                await ctx.response.send_message(data.status_message, ephemeral=True)
            else:
                try:
                    embed = discord.Embed(
                        title="Profile",
                        color=discord.Color.blue(),
                        timestamp=discord.utils.utcnow(),  # Add timestamp to embed
                    )
                    embed.add_field(name="Discord", value=user.mention, inline=True)

                    cyclist = data.cyclist.model_dump()
                    # Add all cyclist fields to the embed, excluding any null values
                    # TODO: Seems like the name is not returned because it is a property maybe
                    fields = [
                        "name",
                        "zwift",
                        "zwiftpower",
                        "strava",
                    ]
                    # Add all cyclist fields to the embed, excluding any null values
                    logfire.info("Start adding fields to embed:")
                    for field in fields:
                        # Format the field name to be more readable
                        logfire.info(f"Field: {field}:{cyclist.get(field, 'failed to get field')}")
                        field_name = field.replace("_", " ").title()
                        embed.add_field(name=field_name, value=f"{cyclist.get(field, '_')}", inline=True)

                    #  Add zwift verified status
                    zwift_verified_status = cyclist.get("ids", {}).get("zwift_verified", None)
                    if zwift_verified_status is not None:
                        logfire.info(f"Add zwift verified status: {cyclist.get('ids')}")
                        embed.add_field(name="Zwift Verified", value=cyclist["zwift_verified"], inline=True)
                    else:
                        embed.add_field(name="Zwift Status", value="Not Verified", inline=True)
                    logfire.info("Finished adding Cyclist fields to embed")

                    # Add ZR record
                    if data.zracing is not None:
                        zr_record = data.zracing.model_dump()
                        logfire.info("Add ZR record")
                        try:
                            zr_record["Handicaps"] = format_handicaps(zr_record)
                            zr_record["Phenotype"] = format_phenotype(zr_record)

                            zr_fields = [
                                "zpCategory",
                                "zpFTP",
                                "CP",
                                "AWC",
                                "compoundScore",
                                "powerRating",
                                "Handicaps",
                                "Phenotype",
                            ]

                            # Embed the fields
                            logfire.info(f"Add ZR record: {zr_record}")
                            for field in zr_fields:
                                embed.add_field(name=field.title(), value=zr_record.get(field), inline=True)
                        except Exception as e:
                            logfire.info(f"zr_rocord might be none: {zr_record}")
                            logfire.error(f"Error formatting ZR record: {e!s}")
                            # embed.add_field(name="ZR Record", value="Error formatting ZR record", inline=True)

                    logfire.info("Add roles to embed")
                    embed.add_field(
                        name="Roles", value=str([r.name for r in user.roles if r is not None]), inline=False
                    )
                    await ctx.response.send_message(embed=embed, ephemeral=True)
                except Exception as e:
                    logfire.error(f"Unexpected error while looking up cyclist: {e!s}")
                    await ctx.response.send_message(
                        "An unexpected error occurred while looking up the cyclist.", ephemeral=True
                    )

    @discord.slash_command(name="my_profile", description="Get a link to manage your cyclist profile")
    async def my_profile(self, ctx: discord.ApplicationContext):
        """Get a link to manage your cyclist profile."""
        with logfire.span("CyclistCog: my_profile"):
            logfire
            logfire.info(f"Getting profile link for {ctx.author}:{ctx.author.id}")
            try:
                data = await get_magic_link(
                    api="my_profile",
                    discord_id=ctx.author.id,
                    discord_name=ctx.author.name,
                    guild_id=ctx.guild.id,
                    guild_name=ctx.guild.name,
                    guild_admin=ctx.author.guild_permissions.administrator,
                    guild_roles=[r.name for r in ctx.author.roles],
                )
                if data.status_code != 200:
                    logfire.error(
                        f"Error getting profile link: CODE:my_profile_1: {data.status_message}: status_code:{data.status_code}"
                    )
                    await ctx.respond(
                        f"❌ Error getting profile link: CODE:my_profile_1: {data.status_message}: status_code:{data.status_code}",
                        ephemeral=True,
                    )
                else:
                    logfire.info(f"Link expires at: {data.expires_at}")
                    embed = Embed(
                        title="My Profile",
                        description="Click the button below to create or edit your profile",
                        color=Color.blue(),
                    )
                    embed.add_field(
                        name="Link Expires", value=f"<t:{int(data.expires_at.timestamp())}:R>", inline=False
                    )
                    # Create button with the URL
                    view = ui.View()
                    view.add_item(ui.Button(label="Manage Profile", url=data.url, style=ButtonStyle.link))
                    await ctx.respond(embed=embed, view=view, ephemeral=True)
                    logfire.info(f"Sent profile link to {ctx.author}")
            except httpx.RequestError as e:
                logfire.error(f"Request failed: CODE:my_profile_2 {e!s}")
                await ctx.respond(
                    f"❌ An error occurred while contacting the API: CODE:my_profile_2 {e!s}", ephemeral=True
                )
            except Exception as e:
                logfire.error(f"Unexpected error while getting profile link: CODE:my_profile_3 {e!s}")
                await ctx.respond("❌ An Unknown error occurred: CODE:my_profile_3", ephemeral=True)


def setup(bot):
    """Pycord calls to setup the cog."""
    bot.add_cog(CyclistCog(bot))  # add the cog to the bot
