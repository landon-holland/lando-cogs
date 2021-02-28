from redbot.core import commands, checks
import discord
import random


class Avalon(commands.Cog):
    """Avalon"""

    def __init__(self, bot):
        self.bot = bot
        self.players = []
        self.ready_players = []
        self.min_players = 5
        self.max_players = 10
        self.player_roles = {}
        self.quest_num = 1
        self.game_status = 0  # 0: No Game. 1: Intermission. 2: In game
        self.checkTime = 300
        self.roles = {
            5: {"Loyal Servant of Arthur": 1, "Merlin": 1, "Percival": 1, "Morgana": 1, "Mordred": 1, "Assassin": 0, "Minion of Mordred": 0},
            6: {"Loyal Servant of Arthur": 2, "Merlin": 1, "Percival": 1, "Morgana": 1, "Mordred": 1, "Assassin": 0, "Minion of Mordred": 0},
            7: {"Loyal Servant of Arthur": 2, "Merlin": 1, "Percival": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 0},
            8: {"Loyal Servant of Arthur": 3, "Merlin": 1, "Percival": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 0},
            9: {"Loyal Servant of Arthur": 4, "Merlin": 1, "Percival": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 0},
            10: {"Loyal Servant of Arthur": 4, "Merlin": 1, "Percival": 1, "Morgana": 1, "Mordred": 1, "Assassin": 1, "Minion of Mordred": 1}
        }
        self.good = ["Loyal Servant of Arthur", "Merlin", "Percival"]
        self.evil = ["Morgana", "Mordred", "Assassin", "Minion of Mordred"]

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
            await message.channel.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "This command must be used in PMs."))
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
    async def guide(self, ctx):
        message = """```asciidoc
= **AVALON** =
[Setup]
There are two sides: the Loyal Servants of Arthur (good) and the Evil Minions of Mordred (evil).
Each side has some special players which are covered in the [Roles] section.
All members of the evil side know who each other are.
Members of the good side do not know who is on either side.

[Gameplay]
The game consists of up to five rounds. Each round has a team building phase and a quest phase.
If three rounds succeed, then the good side wins. If three rounds fail, then the evil side wins.

= Team Building Phase =
One person will be assigned as a team leader. The person chosen to be team leader is assigned in a set order.
After discussion from everyone, the team leader will choose a team to go on the quest. (The size of the team depends on the round.)
The team leader or team members are not always on the good side, so appropriate discussion is necessary for who is on the team.
Once the team leader has chosen all of the team members, a vote is initiated.
(The team leader can put themself on the team.)

All players will vote on whether or not they accept or reject the team that the team leader has built.
If half or more than half of the players vote to reject, then a new team leader is chosen and the process starts over.
If a majority of players vote to accept, then the quest phase of gameplay begins with the assigned team.
(If a vote is rejected five times in one round, the evil side wins.)

= Quest Phase =
Now that a team has been selected. Each team member will individually and privately select whether to succeed or fail the quest.
The quest succeeds if all team members select to succeed the quest.
The quest will fail if one or more team members select to fail quest.
(If the game is played with more than seven players, then on the fourth round you need to team members to select to fail the quest in order to fail the quest.)
```"""
        await ctx.author.send(message)
        message = """```asciidoc
[Roles]
= Loyal Servants of Arthur =
Merlin: Can see all members of the evil side (except for Mordred).
Percival: Can see who Morgana and Percival are. Percival doesn't know who is who.

= Evil Minions of Mordred =
Mordred: Is invisible to Merlin.
Morgana: Pretends to be Merlin in order to throw Percival off.
Assassin: The assigned person to choose who they think Merlin is if the good side wins.

[Post-Game]
If the good side wins, there is a chance for the evil side to take the win.
If the evil side either votes who Merlin is, or the Assassin chooses who Merlin is, then the evil side wins.
```"""
        await ctx.send(embed=self.make_embed("Avalon", 0x77dd77, "Guide", "Sending guide to PMs..."))
        await ctx.author.send(message)

    @avalon.command()
    @commands.guild_only()
    async def start(self, ctx):
        """Start game of Avalon"""
        if self.game_status != 0:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "Game already in progress."))
            return

        self.clear_variables()
        self.players = [ctx.author]
        self.game_status = 1
        
        await ctx.send(embed=self.make_embed("Avalon", 0x77dd77, "Starting...", "Starting game of Avalon in PMs..."))
        await ctx.author.send("{0} has joined the game.".format(self.displayname(ctx.author)))

    @avalon.command()
    @commands.guild_only()
    async def join(self, ctx):
        """Join existing game of Avalon"""
        if len(self.players) > self.max_players:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "Already 10 players in game."))
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You must start a game first."))
            return
        elif self.game_status == 2:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "Game is already in progress."))
            return
        if ctx.author in self.players:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You are already in the game."))
            return

        self.players.append(ctx.author)
        for player in self.players:
            await player.send("{0} has joined the game. ({1}/10)".format(self.displayname(ctx.author), len(self.players)))
        await ctx.send(embed=self.make_embed("Avalon", 0x77dd77, "Joined", "You have joined the game. Check PMs!"))

    @avalon.command()
    @commands.guild_only()
    @checks.mod()
    async def stop(self, ctx):
        """Stop game of Avalon"""
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "No game in progress."))
            return
        self.game_status = 0
        await ctx.send(embed=self.make_embed("Avalon", 0x77dd77, "Stopped", "Current game of Avalon stopped."))
        for player in self.players:
            await player.send(embed=self.make_embed("Avalon", 0x77dd77, "Stopped", "This game has been cancelled."))

    # PM commands
    @avalon.command()
    async def leave(self, ctx):
        """Leave game of Avalon during intermission"""
        if not await self.check_pm(ctx.message):
            return
        if ctx.author not in self.players:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You are not in a game.."))
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "No game in progress."))
            return
        elif self.game_status == 2:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You can not leave an in progress game."))
            return
        self.players.remove(ctx.author)
        await ctx.send(embed=self.make_embed("Avalon", 0x77dd77, "Avalon", "You have successfully left the game."))

    @avalon.command()
    async def ready(self, ctx):
        """Ready up for Avalon game"""
        if not await self.check_pm(ctx.message):
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "There is no active game. Start a game by running `[p]avalon start`."))
            return
        if ctx.author.id in self.ready_players:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You are already ready."))
            return
        self.ready_players.append(ctx.author)
        for player in self.players:
            await player.send("{0} has readied up! ({1}/{2})".format(self.displayname(ctx.author), len(self.ready_players), len(self.players)))

        if set(self.ready_players) == set(self.players):
            if len(self.players) < self.min_players:
                for player in self.players:
                    await player.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You must have 5 players to start the game."))
            else:
                self.game_status = 2
                await self.assign_roles()
                #self.bot.loop.create_task(self.game_loop())

    @avalon.command()
    async def unready(self, ctx):
        """Unready for Avalon game"""
        if not await self.check_pm(ctx.message):
            return
        if self.game_status == 0:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "There is no active game. Start a game by running `[p]avalon start`."))
            return
        if ctx.author.id not in self.ready_players:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You aren't ready."))
            return
        self.ready_players.remove(ctx.author)
        await ctx.send(embed=self.make_embed("Avalon", 0x77dd77, "Unreadied", "You have unreadied."))
    
    @avalon.command()
    async def players(self, ctx):
        """List all players in current Avalon game"""
        if not await self.check_pm(ctx.message):
            return
        if ctx.author not in self.players:
            await ctx.send(embed=self.make_embed("Avalon", 0xff4055, "Error", "You aren't in a game."))
            return
        self.sendPlayerOrder()

    async def game_loop(self):
        while True:
            break
    
    async def assign_roles(self):
        roles_for_this_game = []
        role_thumbnails = {"Loyal Servant of Arthur": "http://gamekicker.herokuapp.com/assets/loyal-5b2decd4aa309e12020b50b3950ab440.jpeg",
          "Merlin": "https://www.ultraboardgames.com/avalon/gfx/merlin.jpg",
          "Percival": "https://www.ultraboardgames.com/avalon/gfx/percival.jpg",
          "Morgana": "https://www.ultraboardgames.com/avalon/gfx/morgana.jpg",
          "Mordred": "https://www.ultraboardgames.com/avalon/gfx/mordred.jpg",
          "Assassin": "https://www.ultraboardgames.com/avalon/gfx/assassin.jpg",
          "Minion of Mordred": "http://gamekicker.herokuapp.com/assets/minion-553e9b70b2aea7fbfd37e20e68aab878.jpeg"}

        random.shuffle(self.players)

        for role, number in self.roles[len(self.players)].items():
            for n in range(number):
                roles_for_this_game.append(role)

        for player in self.players:
            self.player_roles.update({player:roles_for_this_game.pop(random.randrange(len(roles_for_this_game)))})
        
        evil_players = []
        for player, role in self.player_roles.items():
            if role in self.evil:
                evil_players.append(player)

        for player, role in self.player_roles.items():
            message = ""
            embed_role = ""
            embed_color = 0x77dd77
            embed_desc = ""
            embed_thumbnail = ""
            if role in self.evil:
                embed_role = "Minion of Mordred"
                embed_color = 0xff4055
                embed_desc = "You are a Minion of Mordred"
                message += "The other players on your team are:\n"
                for p in evil_players:
                    if p != player
                        message += self.displayname(p) + "\n"
            
            if role in self.good:
                embed_role = "Loyal Servant of Arthur"
                embed_desc = "You are a Loyal Servant of Arthur"

            if role == "Merlin":
                message += "The Minions of Mordred (excluding Mordred) are:\n"
                for p in evil_players:
                    if self.player_roles[p] != "Mordred":
                        message += self.displayname(p) + "\n"
            
            if role == "Percival":
                message += "Merlin and Morgana are (you don't know who is who):\n"
                for p in self.players:
                   if self.player_roles[p] == "Merlin" or self.player_roles[p] == "Morgana":
                        message += self.displayname(p) + "\n"
            
            if role != "Loyal Servant of Arthur" and role != "Minion of Mordred":
                embed_desc = "You are {0}!\nUse `[p]avalon guide {0}` to find a guide about your role.".format(role)
                embed_thumbnail = role_thumbnails[role]
            
            embed = self.make_embed("Avalon", embed_color, embed_desc, embed_role)
            embed.set_thumbnail(url=embed_thumbnail)
            await player.send(embed=embed)
            if message != "":
                await player.send(message)

        await self.sendPlayerOrder()
    
    async def sendPlayerOrder(self):
        message = "The order of players is:\n"
        for count, p in enumerate(self.players):
            message += str(count + 1) + ". " + self.displayname(p) + "\n"

        for player in self.players:
            await player.send(message)
            