import os
import discord
import openai
import aiosqlite
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up Discord bot client
bot = commands.Bot(command_prefix="$", intents=intents)
messages = [
    {"role": "system", "content": "You are a helpful assistant that works through Discord."}
]

async def create_db():
    async with aiosqlite.connect("api_keys.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS api_keys (user_id INTEGER PRIMARY KEY, api_key TEXT)"
        )
        await db.commit()
@bot.event
async def on_ready():
    print(f"{bot.user} is connected to Discord and ready to receive events.")
    await create_db()

# Define a function to retrieve the user's API key
async def get_user_api_key(user_id):
    async with aiosqlite.connect("api_keys.db") as db:
        cursor = await db.execute("SELECT api_key FROM api_keys WHERE user_id=?", (user_id,))
        api_key = await cursor.fetchone()
        return api_key[0] if api_key else None


# Define a function to set/update the user's API key
@bot.command()
async def setapikey(ctx, *, api_key):
    user_id = ctx.author.id
    async with aiosqlite.connect("api_keys.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO api_keys (user_id, api_key) VALUES (?, ?)",
            (user_id, api_key),
        )
        await db.commit()
    await ctx.send("API key set successfully!")


async def openai_chat(user_id, prompt):
    api_key = await get_user_api_key(user_id)
    if api_key is None:
        return "you need to set your OpenAI API key first. Use the $setup command for more information"
    openai.api_key = api_key
    message=prompt
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})
    return reply

@bot.command()
async def chat(ctx, *, prompt):
    user_id = ctx.author.id
    async with ctx.typing():
        reply = await openai_chat(user_id, prompt)
    await ctx.send(reply)

@bot.command()
async def setup(ctx):
    api_key = await get_user_api_key(ctx.author.id)
    if api_key is None:
        await ctx.author.send("Please send your OpenAI API key in this format: $setapikey YOUR_API_KEY")
        await ctx.send("Check your messages to finish setting up your API key! :)")
    else:
        await ctx.send("You already have an API key setup. If you wish to update your key, send the bot a direct message with $setkey followed by your API key")

@chat.error
async def chat_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Oops! You need a message after the chat command.')

# Run the bot
bot.run(TOKEN)



#current idea: yeah lets move to node.js lol https://github.com/CappeDiem/Discord.js-bot-template