from collections import OrderedDict
from datetime import datetime
import json
import traceback
from typing import Tuple, List, Dict

from discord.ext.commands import (Cog, command, Context, Bot,
                                  MissingRequiredArgument, guild_only,
                                  BadArgument)
from discord import Member

DATABASE = 'database.json'


class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def _read_database(self) -> dict:
        while True:
            print("loop")
            try:
                with open(DATABASE, 'r') as f:
                    print("opening database")
                    return json.load(f)
            except FileNotFoundError:
                with open(DATABASE, 'w') as f2:
                    print("Creating database", DATABASE)
                    json.dump({"entries": []}, f2, indent=2)

    def _stats(self, database: dict) -> Tuple[dict, OrderedDict, OrderedDict]:
        entries: list = database['entries']

        kills = {}
        deaths = {}
        names = {}

        for entry in entries:
            killer = entry['uid']

            if killer not in kills:
                kills[killer] = 0
            if killer not in names:
                names[killer] = entry['name']

            for kill in entry['kills']:
                kills[killer] += 1

                victim = kill['victim']

                if victim not in names:
                    names[victim] = kill['name']

                if victim not in deaths:
                    deaths[victim] = 0
                deaths[victim] += 1

        sorted_kills = OrderedDict(
            {k: v for k, v in sorted(kills.items(), key=lambda item: item[1],
                                     reverse=True)})
        sorted_deaths = OrderedDict(
            {k: v for k, v in sorted(deaths.items(), key=lambda item: item[1],
                                     reverse=True)})

        print("names", names)
        print("kills", sorted_kills)
        print("deaths", sorted_deaths)

        return names, sorted_kills, sorted_deaths

    @guild_only()
    @command()
    async def log(self, ctx: Context, killer: Member, victim: Member,
                  *, description: str = ""):
        """
        Logs a single kill to the database

        <killer> and <victim> can either be: numeric ID, @mention, nickname in quotes, username or username#discriminator
        """

        """
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
        victim_id = victim.id
        print("killer name", killer_name, killer_id)
        print("victim name", victim_name, victim_id)

        database = self._read_database()

        entries = database['entries']
        killer_entry = next((
            entry
            for entry in entries
            if entry['uid'] == killer_id
        ), None)
        print("killer entry", killer_entry)
        if killer_entry is not None:
            entries.remove(killer_entry)
        else:
            killer_entry = {
                "uid": killer_id,
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

        print("db", database)

        with open(DATABASE, 'w') as f:
            json.dump(database, f, indent=2)

        await ctx.send("Logged: {} killed {}".format(killer_name, victim_name))

    def _create_message(self, option="kills") -> str:
        db = self._read_database()

        if len(db['entries']) == 0:
            return "No {}".format(option)

        names, kills, deaths = self._stats(db)

        if option == "kills":
            abbreviation = "TKs"
            dict_ = kills
        else:
            abbreviation = "TDs"
            dict_ = deaths

        i = 1
        message = "**Most team {}**\n".format(option)
        for uid, count in dict_.items():
            message += "`{}.` {} - {} {}\n".format(
                i, names[uid], count, abbreviation
            )
            i += 1

        return message

    @command()
    async def kills(self, ctx: Context):
        """
        Lists team kill counters
        """
        message = self._create_message("kills")
        await ctx.send(message)

    @command()
    async def deaths(self, ctx: Context):
        """
        Lists team death counters
        """
        message = self._create_message("deaths")
        await ctx.send(message)

    def _get_list(self, database) -> List[Dict[str, str]]:
        entries: list = database['entries']

        events: List[Dict[str, str]] = []

        for entry in entries:
            killer_name = entry['name']

            for kill in entry['kills']:
                events.append({
                    "killer": killer_name,
                    "victim": kill['name'],
                    "timestamp": kill['timestamp'],
                    "description": kill['description'],
                })

        sorted_events = sorted(events, key=lambda item: item['timestamp'])

        print("events", sorted_events)

        return sorted_events

    @command(name="list")
    async def list_(self, ctx: Context):
        """
        Shows a list of all logged data
        """
        db = self._read_database()

        if len(db['entries']) == 0:
            await ctx.send("No logged data")
            return

        events = self._get_list(db)

        message = "**All logged data**\n"
        for event in events:
            if len(event['description']) > 0:
                description = " with description: {}" \
                    .format(event['description'])
            else:
                description = ""
            message += "`{}`: **{}** killed **{}**{}\n".format(
                event['timestamp'],
                event['killer'],
                event['victim'],
                description
            )

        await ctx.send(message)

    @log.error
    @kills.error
    @deaths.error
    @list_.error
    async def error(self, ctx: Context, e: Exception):
        if isinstance(e, MissingRequiredArgument):
            await ctx.send("Missing required argument {}".format(e.param.name))
            await ctx.send_help(ctx.command)
        elif isinstance(e, BadArgument):
            await ctx.send("Invalid argument: {}. See: `!help {}`"
                           .format(e, ctx.command))
        else:
            await ctx.send("An error occured while executing command: "
                           "```{}```"
                           .format(traceback.format_exc()))
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Commands(bot))


if __name__ == "__main__":
    c = Commands(None)
    db = c._read_database()
    stats = c._stats(db)
    msg = c._create_message(option="kills")
    list_ = c._get_list(db)
