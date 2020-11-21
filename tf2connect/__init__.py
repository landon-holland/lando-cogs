from .tf2connect import TF2Connect

__red_end_user_data_statement__ = "This bot does not store any data or metadata about users."


def setup(bot):
    bot.add_cog(TF2Connect())
