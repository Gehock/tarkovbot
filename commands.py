from datetime import datetime
import json
import traceback

from discord.ext.commands import (Cog, command, Context, Bot,
                                  MissingRequiredArgument)
from discord import Member

DATABASE = 'database.json'


class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def log(self, ctx: Context, killer: Member, victim: Member,
                  *, description: str = ""):
        """
        Logs a single kill to the database.

        Database format:
        {
            "entries": [
                {
                    "uid": 150625032656125952,
                    "name": "Gehock",
                    "kills": [
                        {
                            "victim": 387348620841582594,
                            "name": "Gahock",
                            "timestamp": "2020-03-16T03:21",
                            "description": "Misclick"
                        }
                    ]
                }
            ]
        }
        """

        killer_name = killer.nick if killer.nick is not None else killer.name
        victim_name = victim.nick if victim.nick is not None else victim.name
        killer_id = killer.id

        while True:
            print("loop")
            try:
                with open(DATABASE, 'r') as f:
                    print("opening database")
                    database = json.load(f)
                    break
                    print("open successful")
            except FileNotFoundError as e:
                with open(DATABASE, 'w') as f2:
                    print("Creating database", DATABASE)
                    json.dump({"entries": []}, f2, indent=2)
        print("loop done")

        await ctx.send("```{}```".format(json.dumps(database, indent=2)))

        entries = database['entries']
        killer_entry = next((
            entry
            for entry in entries
            if entry['uid'] == killer_id
        ))
        if killer_entry is not None:
            entries.remove(killer_entry)
        else:
            killer_entry = {
                "uid": killer_entry,
                "name": killer_name,
                "kills": []
            }

        victim_entry = {
            "victim": victim.id,
            "name": victim_name,
            "timestamp": datetime.now().isoformat(timespec='minutes'),
            "description": description
        }

        killer_entry['kills'].append(victim_entry)
        database['entries'].append(killer_entry)

        print(database)

        with open(DATABASE, 'w') as f:
            json.dump(database, f, indent=2)

        await ctx.send("Logged: {} killed {}".format(killer_name, victim_name))

    @command()
    async def kills(self, ctx: Context):
        await ctx.send("No kills")

    @command()
    async def deaths(self, ctx: Context):
        await ctx.send("No deaths")

    @log.error
    @kills.error
    @deaths.error
    async def error(self, ctx: Context, e: Exception):
        if isinstance(e, MissingRequiredArgument):
            await ctx.send("Missing required argument {}".format(e.param.name))
            await ctx.send_help(ctx.command)
        else:
            await ctx.send("An error occured while executing command: "
                           "```{}```"
                           .format(traceback.format_exc()))
            traceback.print_exc()

def setup(bot):
    bot.add_cog(Commands(bot))
