import asyncio
import random
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
import psycopg2
from config1 import host, user, password, db_name
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Токен бота Telegram
TOKEN = "5895594295:AAHB02rH2thdVUSlp7ufrXV_tC6Mtuefhkk"

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# PostgreSQL connection details
DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PASSWORD = 'any'
DB_NAME = 'postgres'


commands_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
commands_keyboard.add(KeyboardButton('/game <<random game>>'), KeyboardButton('/randomgames'), KeyboardButton('/joke'))

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_keyboard.add(KeyboardButton('/start'))

# Function to fetch game data from the database
async def get_game_info(game_name):
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    query = "SELECT name, url, cost,  description, minimum_requirements, recommended_requirements FROM game WHERE name ILIKE $1"
    result = await conn.fetchrow(query, game_name)
    await conn.close()
    return result


# Handler for the /game command
@dp.message_handler(Command(commands=['game']))
async def handle_game_command(message: types.Message):
    # Get the game name from the command arguments
    game_name = message.get_args()

    if not game_name:
        await message.reply("Please specify the game name after the /game command.")
        return
    try:
        # Get the game information from the database
        game_info = await get_game_info(game_name)

        if game_info:
            name = game_info['name']
            description = game_info['description']
            minimum_requirements = game_info['minimum_requirements']
            recommended_requirements = game_info['recommended_requirements']
            cost = game_info['cost']
            url = game_info['url']
            # Send the game information to the user
            await message.reply(
                f"Game Name: {name}\n"
                f"Link: {url}\n"
                f"Price: {cost}\n"
                f"Description: {description}\n"
                f"Minimum_requirements: {minimum_requirements}\n"
                f"Recommended_requirements: {recommended_requirements}\n"
            )
        else:
            await message.reply("Game with the specified name was not found.")
    except Exception as e:
        await message.reply("An error occurred while fetching game information.")
        print(e)

# Handler for the /randomgames command
@dp.message_handler(Command(commands=['randomgames']))
async def handle_random_games_command(message: types.Message):
    try:
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        query = "SELECT name, url, cost, description, minimum_requirements, recommended_requirements FROM game ORDER BY random() LIMIT 5"
        result = await conn.fetch(query)
        await conn.close()
        if result:
            response = "Random Games:\n\n"
            for game in result:
                name = game['name']
                cost = game['cost']
                url = game['url']
                response += f"Game Name: {name}\nLink: {url}\nPrice: {cost}\n\n"

            # Send the random game information to the user
            await message.reply(response)
        else:
            await message.reply("No games found.")
    except Exception as e:
        await message.reply("An error occurred while fetching random games.")
        print(e)


async def handle_start_command(message: types.Message):
    response = "Welcome to the Game Bot!\n"
    response += "Use */game <game_name>\* to search for a specific game.\n"
    response += "Use */randomgames\* to get information about 5 random games.\n"
    response += "Use */joke*\ to get a random joke.\n"
    await message.reply(response, reply_markup=commands_keyboard)



@dp.message_handler(commands=['help'])
async def handle_start_help_command(message: types.Message):
    response = "Welcome to the Timplate.ru!\n"
    response += "Use /game <game_name> to search for a specific game.\n"
    response += "Use /randomgames to get information about 5 random games.\n"
    response += "Introduction:\n Welcome to the Game Bot! This bot provides information about computer games, and also knows how to pick up random jokes for your entertainment. In this guide, we will tell you how to use the bot's functionality and get interesting information about games.\n"
    response += "1. Launching the bot: To use Bot, find it in Telegram by username or via a link t.me/CostREABot. After you open a chat with a bot, you can start interacting with it.\n"
    response += "2. Bot commands: The bot supports the following commands:\n"
    response += "/start or /help: Get a welcome message and a list of available commands.\n"
    response += "/game <game_name>: Get information about a specific game by specifying its name. For example, /game Cyberpunk 2077.\n"
    response += "/randomgames: Get information about 5 random games.\n"
    response += "/joke: Get a random joke from a bot.\n"
    response += "3. Game search:\n"
    response += "To get information about a specific game, use the command /game <game_name>. For example, if you want to know about the game Cyberpunk 2077, enter /game Cyberpunk 2077. The bot will give you information about the game, such as the name, link to it, cost, as well as its description and recommended and minimum system requirements.\n"
    response += "4. Getting random games:\n"
    response += "Using the /randomgames command, you can get information about 5 random games. Just enter this command and the bot will provide you with information about randomly selected games.\n"
    response += "5. Getting a random joke:\n"
    response += "If you need to cheer yourself up, use the /joke command, and the bot will provide a random joke from the list of available ones.\n"
    await message.reply(response)


@dp.message_handler(commands=['start'])
async def handle_start_command(message: types.Message):
    response = "Welcome to the Game Bot!\n"
    response += "Use /game <game_name> to search for a specific game.\n"
    response += "Use /randomgames to get information about 5 random games.\n"
    response += "Use /joke to get a random joke.\n"
    await message.reply(response, reply_markup=commands_keyboard)



# List of jokes
jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "Why don't eggs tell jokes? Because they might crack up!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "How do you catch a squirrel? Climb a tree and act like a nut!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What do you call a fish wearing a crown? King of the sea!",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "What do you call a bear with no teeth? A gummy bear!"
]


# Handler for the /joke command
@dp.message_handler(Command(commands=['joke']))
async def handle_joke_command(message: types.Message):
    joke = random.choice(jokes)
    await message.reply(joke)


@dp.message_handler()
async def handle_unknown_command(message: types.Message):
    response = "Unknown command.\n"
    response += "Available commands:\n"
    response += "- /start or /help\n"
    response += "- /game <game_name>\n"
    response += "- /randomgames\n"
    response += "- /joke\n"
    await message.reply(response, reply_markup=commands_keyboard)


# Run the bot
if __name__ == '__main__':
    asyncio.run(dp.start_polling())
