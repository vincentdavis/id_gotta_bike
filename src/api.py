import os
import urllib

import httpx
import logfire

from src.schema import CyclistLookUp, DiscordMagicLinkResponse, LocalGetMagicLinkResponse


def format_handicaps(zr_record) -> str:
    """Format handicaps into a multiline string."""
    logfire.info("format_handicaps")
    profile = zr_record.get("handicaps", {}).get("profile", None)
    if profile is None:
        logfire.info("No handicap record")
        return "No handicap record"
    lines = [
        f"Flat: {profile.get('flat', 0):.2f}",
        f"Rolling: {profile.get('rolling', 0):.2f}",
        f"Hilly: {profile.get('hilly', 0):.2f}",
        f"Mountainous: {profile.get('mountainous', 0):.2f}",
    ]
    logfire.info(f"Handicaps: {lines}")
    return "\n".join(lines)


def format_phenotype(zr_record) -> str:
    """Format phenotype scores into a multiline string."""
    logfire.info("format_phenotype")
    scores = zr_record.get("phenotype", {}).get("scores", None)
    if scores is None:
        return "No phenotype"
    lines = [
        f"Type: {zr_record.get('phenotype_value', '_')}: {zr_record.get('phenotype_bias', '_')} ",
        f"Sprinter: {scores.get('sprinter', 0):.1f}",
        f"Puncheur: {scores.get('puncheur', 0):.1f}",
        f"Pursuiter: {scores.get('pursuiter', 0):.1f}",
        f"Climber: {scores.get('climber', 0):.1f}",
        f"Time Trial: {scores.get('tt', 0):.1f}",
    ]
    return "\n".join(lines)


async def get_magic_link(
    api: str,
    discord_id: str | int,
    discord_name: str,
    guild_id: str | int,
    guild_name: str,
    guild_admin: bool,
    guild_roles: list[str | int] | None = None,
) -> LocalGetMagicLinkResponse:
    """Get magic link for a user discord bot user."""
    with logfire.span("API: Get MagicLink"):
        encoded_roles = urllib.parse.quote(str(guild_roles))

        logfire.info(
            f"Building MagicLink for:\n{api}, {discord_id}, {discord_name}, {guild_id}, {guild_name}, {guild_admin}\n"
        )
        logfire.info(f"Member Roles: {guild_roles}")
        try:
            headers = {"X-API-Key": os.getenv("API_KEY")}
            guild_parms = f"?discord_name={urllib.parse.quote(discord_name)}&guild_id={guild_id}&guild_name={urllib.parse.quote(guild_name)}&guild_admin={guild_admin}&guild_roles={encoded_roles if encoded_roles else ''}"
            match api:
                case "my_profile":
                    url = f"{os.getenv('API_URL')}/my_profile_link/{discord_id}{guild_parms}"
                case "cyclists_reg_status":
                    url = (f"{os.getenv('API_URL')}/cyclists/registration_status",)
                case _:
                    raise ValueError(f"Unknown API type: {api}")

            async with httpx.AsyncClient() as client:
                logfire.info(f"Getting magic link for :{discord_id}")
                logfire.info(f"Request url: {url}")
                response = await client.get(url, headers=headers)
                logfire.info(f"Response status_code: {response.status_code}, {response.text}")
                if response.status_code == 200:
                    discord_magic_link: DiscordMagicLinkResponse = DiscordMagicLinkResponse.model_validate(
                        response.json()
                    )
                    logfire.info(f"Magic link: {discord_magic_link}")
                    data = LocalGetMagicLinkResponse(
                        status_code=response.status_code,
                        status_message=response.text,
                        api=api,
                        discord_id=discord_id,
                        guild_id=guild_id,
                        guild_name=guild_name,
                        url=discord_magic_link.url,
                        expires_at=discord_magic_link.expires_at,
                        uuid=discord_magic_link.uuid,
                    )
                    logfire.info(f"Magic link: {data}")
                    return data
                else:
                    logfire.error(f"Response status_code: {response.status_code}, {response.status_message}")
                    data = LocalGetMagicLinkResponse(
                        status_code=response.status_code,
                        status_message=response.text,
                        api=api,
                        discord_id=discord_id,
                        guild_id=guild_id,
                        guild_name=guild_name,
                        url=None,
                        expires_at=None,
                        uuid=None,
                    )
                    logfire.error(f"Error getting magic link, {data}")
                    return data
        except Exception as e:
            logfire.error(
                "Unknown error building magic link with params:\n"
                f"{api}, {discord_id}, {guild_id}, {guild_name}\n"
                f"Error: {e!s}"
            )
            LocalGetMagicLinkResponse(
                status_code=500,
                status_message="Unknown error building magic link with params:",
                api=api,
                discord_id=discord_id,
                guild_id=guild_id,
                guild_name=guild_name,
                url=None,
                expires_at=None,
                uuid=None,
            )
            return data


async def lookup_cyclist(discord_id: str) -> CyclistLookUp:
    """Look up cyclist information using the API.

    Args:
        discord_id: Discord ID of the user to look up

    Returns:
        tuple: (success, result)
            - success: Boolean indicating if the lookup was successful
            - result: Dict containing cyclist data if successful, error message if not

    """
    with logfire.span("lookup_cyclist_api"):
        async with httpx.AsyncClient() as client:
            from discord import ValidationError

            try:
                response = await client.get(
                    f"{os.getenv('API_URL')}/cyclists",
                    params={"discord_id": discord_id},
                    timeout=10.0,
                )

                logfire.info(f"Response: {response.status_code}")

                if response.status_code == 200:
                    logfire.info("Found cyclist information")
                    data = response.json()
                    # for i in data["cyclist"].items():
                    #     logfire.info(f"item: {i}")
                    data["status_code"] = 200
                    data["status_message"] = "OK"
                    logfire.info(f"Cyclist data: {data.keys()}")

                else:  # TODO, should have better plan for different error codes.
                    logfire.error(f"Status code not 200: {response.status_code}, {response}")
                    try:
                        error_detail = response.json().get("detail", "Unknown error 1")
                    except Exception as e:
                        logfire.error(f"Error parsing response: {e!s}")
                        error_detail = "Unknown error 2"
                    data = {
                        "status_code": response.status_code,
                        "status_message": error_detail,
                        "cyclist": None,
                        "zracing": None,
                    }
                logfire.info("Validate the data")
                v_data = CyclistLookUp.model_validate(data)
                return v_data

            except ValidationError as e:
                logfire.error(f"ValidationError: {e!s}")
                data = {
                    "status_code": response.status_code,
                    "status_message": "Invalid input",
                    "cyclist": None,
                    "zracing": None,
                }
            except httpx.ConnectTimeout:
                logfire.error("API request timed out")
                data = {
                    "status_code": response.status_code,
                    "status_message": "Request timed out while looking up the cyclist.",
                    "cyclist": None,
                    "zracing": None,
                }
                return CyclistLookUp.model_validate(data)
            except httpx.HTTPStatusError as e:
                logfire.error(f"API error: Status {e.response.status_code}, Response: {e.response.text}")
                data = {
                    "status_code": response.status_code,
                    "status_message": "An error occurred while looking up the cyclist.",
                    "cyclist": None,
                    "zracing": None,
                }
                return CyclistLookUp.model_validate(data)
            except httpx.RequestError as e:
                logfire.error(f"Request failed: {e!s}")
                data = {
                    "status_code": response.status_code,
                    "status_message": "An error occurred while connecting to the registration service.",
                    "cyclist": None,
                    "zracing": None,
                }
                return CyclistLookUp.model_validate(data)
            except Exception as e:
                logfire.error(f"Unexpected error while looking up cyclist: {e!s}")
                data = {
                    "status_code": response.status_code,
                    "status_message": "Unexpected error while looking up cyclist",
                    "cyclist": None,
                    "zracing": None,
                }
                logfire.error(f"Error: {data}")
                return CyclistLookUp.model_validate(data)
