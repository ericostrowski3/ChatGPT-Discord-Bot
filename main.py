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

# Set up OpenAI chat function
def openai_chat(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that works through Discord."}
    ]
    message=prompt
    messages.append({"role": "user", "content": message})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages

    )
    reply = response["choices"][0]["message"]["content"]
    messages.append({"Role": "assistant", "content": reply})
    return reply
    print(messages)

# Define bot commands
@bot.command()
async def chat(ctx, *, prompt):
    
    reply = openai_chat(prompt)
    await ctx.send(reply)


# Run the bot
bot.run(TOKEN)

