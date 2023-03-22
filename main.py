import os
import discord
import openai
import aiosqlite
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up Discord bot client
bot = commands.Bot(command_prefix="$", intents=intents)
messages = [
    {"role": "system", "content": "You are a helpful assistant that works through Discord."}
]

async def create_table():
    async with aiosqlite.connect("api_keys.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS api_keys (user_id INTEGER PRIMARY KEY, api_key TEXT)")
        await db.commit()

async def set_user_api_key(user_id, api_key):
    async with aiosqlite.connect("api_keys.db") as db:
        await db.execute("INSERT OR REPLACE INTO api_keys (user_id, api_key) VALUES (?, ?)", (user_id, api_key))
        await db.commit()

async def get_user_api_key(user_id):
    async with aiosqlite.connect("api_keys.db") as db:
        cursor = await db.execute("SELECT api_key FROM api_keys WHERE user_id=?", (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else None

async def openai_chat(prompt, api_key):
    message=prompt
    messages.append({"role": "user", "content": message})

    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    reply = response["choices"][0]["message"]["content"]
    return reply

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await create_table()

@bot.command()
async def setkey(ctx, api_key):
    await set_user_api_key(ctx.author.id, api_key)
    await ctx.author.send("Your OpenAI API key has been set!")

@bot.command()
async def chat(ctx, *, prompt):
    api_key = await get_user_api_key(ctx.author.id)
    
    if api_key is None:
        await ctx.send("Please set your OpenAI API key first using the `$setup command")
        return

    reply = await openai_chat(prompt, api_key)
    await ctx.send(reply)

@bot.command()
async def setup(ctx):
    api_key = await get_user_api_key(ctx.author.id)
    if api_key is None:
        await ctx.author.send("Please send your OpenAI API key in this format: $setkey YOUR_API_KEY")
        await ctx.send("Check your messages to finish setting up your API key! :)")
    else:
        await ctx.send("You already have an API key setup. If you wish to update your key, send the bot a direct message with $setkey followed by your API key")

@chat.error
async def chat_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Oops! You need a message after the chat command.')

# Run the bot
bot.run(TOKEN)



#current idea: in chat command, see if api_key is already defined. If its not, tell user. If it is, do nothing. It would then be declared globally. would not need to set it every single time in the openai_chat function