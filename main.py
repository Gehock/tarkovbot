from secret import TOKEN
from tarkovbot import Tarkovbot


if __name__ == "__main__":
    print("creating bot")
    bot = Tarkovbot(command_prefix='!')
    print("running bot")
    bot.run(TOKEN)
