from .quotes import Quotes

__red_end_user_data_statement__ = "This bot does not store any data or metadata about users."


async def setup(bot):
    cog = Quotes(bot)
    await cog.generate_cache()
    bot.add_cog(cog)
