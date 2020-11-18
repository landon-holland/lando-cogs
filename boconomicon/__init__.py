from .boconomicon import Boconomicon

__red_end_user_data_statement__ = "This bot does not store any data or metadata about users."


async def setup(bot):
    cog = Boconomicon(bot)
    await cog.generate_cache()
    bot.add_cog(cog)
