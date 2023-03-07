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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = response.choices[0].text.strip()
    return message

# Define bot commands
@bot.command()
async def chat(ctx, *, message):
    prompt = f"User: {message}\nAI:"
    response = openai_chat(prompt)
    await ctx.send(response)

# Run the bot
bot.run(TOKEN)