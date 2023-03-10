import os
import discord
import openai
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv('OPENAI_KEY')
# Set up Discord bot client
bot = commands.Bot(command_prefix="$", intents=intents)
#define messages globally for context to work
messages = [
    {"role": "system", "content": "You are a helpful assistant that works through Discord."}
]

# Set up OpenAI chat function
def openai_chat(prompt):
    message=prompt
    messages.append({"role": "user", "content": message})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages

    )
    reply = response["choices"][0]["message"]["content"]
    messages.append({"Role": "assistant", "content": reply})
    return reply


# Define chat command
@bot.command()
async def chat(ctx, *, prompt):
    reply = openai_chat(prompt)
    await ctx.send(reply)
#Define reset command 
@bot.command()
async def reset(ctx):
    global messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant that works through Discord."}
    ]
    await ctx.send("Message history cleared!")
#handle error if $chat is send without a prompt
@chat.error
async def chat_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Oops! You need a message after the chat command.')


# Run the bot
bot.run(TOKEN)

