from .avalon import Avalon

__red_end_user_data_statement__ = "This bot does not store any data or metadata about users."


async def setup(bot):
    bot.add_cog(Avalon())
