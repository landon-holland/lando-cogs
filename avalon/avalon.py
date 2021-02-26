from redbot.core import commands, checks
import discord
import random


class Avalon(commands.Cog):
    """Avalon"""

    def __init__(self, bot):
        self.bot = bot
        self.players = []
        self.ready_players = []
        self.min_players = 2
        self.max_players = 10
        self.player_roles = {}
        self.quest_num = 1
        self.game_status = 0  # 0: No Game. 1: Intermission. 2: In game
        self.roles = {
            2: {"Loyal Servant of Arthur": 1, "Merlin": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 0},
            5: {"Loyal Servant of Arthur": 1, "Merlin": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 0},
            6: {"Loyal Servant of Arthur": 2, "Merlin": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 0},
            7: {"Loyal Servant of Arthur": 2, "Merlin": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 1},
            8: {"Loyal Servant of Arthur": 3, "Merlin": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 1},
            9: {"Loyal Servant of Arthur": 4, "Merlin": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 1},
            10: {"Loyal Servant of Arthur": 4, "Merlin": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 2}
        }

    def make_embed(self, title, color, name, value):
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name=name,
                        value=value,
                        inline=False)

        return embed

    async def check_pm(self, message):
        # Checks if we're talking in PM, and if not - outputs an error
        if isinstance(message.channel, discord.abc.PrivateChannel):
            # PM
            return True
        else:
            # Not in PM
            await message.channel.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'This command must be used in PMs.'))
            return False

    def displayname(self, member: discord.Member):
        # A helper function to return the member's display name
        nick = name = None
        try:
            nick = member.nick
        except AttributeError:
            pass
        try:
            name = member.name
        except AttributeError:
            pass
        if nick:
            return nick
        if name:
            return name
        return None

    def clear_variables(self):
        self.players = []
        self.ready_players = []
        self.player_roles = {}
        self.quest_num = 1
        self.game_status = 0

    # Guild commands
    @commands.group()
    async def avalon(self, ctx):
        """Main Avalon command"""
        pass

    @avalon.command()
    @commands.guild_only()
    async def start(self, ctx):
        """Start game of Avalon"""
        if self.game_status != 0:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'Game already in progress'))
            return

        self.clear_variables()
        self.players = [ctx.author]
        self.game_status = 1
        
        await ctx.send(embed=self.make_embed('Avalon', 0x77dd77, 'Starting...', 'Starting game of Avalon in PMs...'))
        await ctx.author.send("{0} has joined the game.".format(self.displayname(ctx.author)))

    @avalon.command()
    @commands.guild_only()
    async def join(self, ctx):
        """Join existing game of Avalon"""
        if len(self.players) > self.max_players:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'Already 10 players in game.'))
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'You must start a game first.'))
            return
        elif self.game_status == 2:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'Game is already in progress.'))
            return
        if ctx.author in self.players:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'You are already in the game.'))
            return

        self.players.append(ctx.author)
        for player in self.players:
            await player.send("{0} has joined the game.".format(self.displayname(ctx.author)))
        await ctx.send(embed=self.make_embed('Avalon', 0x77dd77, 'Joined', 'You have joined the game. Check PMs!'))

    @avalon.command()
    @commands.guild_only()
    @checks.mod()
    async def stop(self, ctx):
        """Stop game of Avalon"""
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'No game in progress.'))
            return
        self.game_status = 0
        await ctx.send(embed=self.make_embed('Avalon', 0x77dd77, 'Stopped', 'Current game of Avalon stopped.'))
        for player in self.players:
            await player.send(embed=self.make_embed('Avalon', 0x77dd77, 'Stopped', 'This game has been cancelled.')

    # PM commands
    @avalon.command()
    async def leave(self, ctx):
        """Leave game of Avalon during intermission"""
        if not await self.check_pm(ctx.message):
            return
        if ctx.author not in self.players:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'You are not in a game..'))
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'No game in progress.'))
            return
        elif self.game_status == 2:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'You can not leave an in progress game.'))
            return
        self.players.remove(ctx.author)
        await ctx.send(embed=self.make_embed('Avalon', 0x77dd77, 'Avalon', 'You have successfully left the game.'))

    @avalon.command()
    async def ready(self, ctx):
        """Ready up for Avalon game"""
        if not await self.check_pm(ctx.message):
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'There is no active game. Start a game by running `[p]avalon start`.'))
            return
        if ctx.author.id in self.ready_players:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'You are already ready.'))
            return
        self.ready_players.append(ctx.author)
        await ctx.send(embed=self.make_embed('Avalon', 0x77dd77, 'Readied', 'You have readied up!'))
        for player in self.players:
            if player != ctx.author:
                await player.send("{0} has readied up!".format(self.displayname(ctx.author)))

        if set(self.ready_players) == set(self.players):
            if len(self.players) < self.min_players:
                for player in self.players:
                    await player.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'You must have 5 players to start the game.'))
            else:
                self.assign_roles()
                #self.bot.loop.create_task(self.game_loop())

    @avalon.command()
    async def unready(self, ctx):
        """Unready for Avalon game"""
        if not await self.check_pm(ctx.message):
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'There is no active game. Start a game by running `[p]avalon start`.'))
            return
        if ctx.author.id not in self.ready_players:
            await ctx.send(embed=self.make_embed('Avalon', 0xff4055, 'Error', 'You aren\'t ready.'))
            return
        self.ready_players.remove(ctx.author)
        await ctx.send(embed=self.make_embed('Avalon', 0x77dd77, 'Unreadied', 'You have unreadied.'))

    async def game_loop(self):
        while True:
            break
    
    def assign_roles(self):
        roles_for_this_game = []
        for role, number in self.roles[len(self.players)].items():
            for n in range(number):
                roles_for_this_game.append(role)

        for player in self.players:
            self.player_roles.update({player:roles_for_this_game.pop(random.randrange(len(roles_for_this_game)))})
        
        print(self.player_roles)
