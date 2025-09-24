from utils.searxNG import query_searxng
from utils.segragate_kunning import isolate_kunning
from utils.llm import call_llm_for_news, call_llm_for_general_purpose
import discord
from discord.ext import commands, tasks
import os
import asyncio
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    send_cron_message.start()


@tasks.loop(hours=5)
async def send_cron_message():
    channel_id = int(os.getenv('CRON_CHANNEL_ID'))
    channel = bot.get_channel(channel_id)

    quotes =  [
    "Nothing ever happens.",
    "I just want to be left alone.",
    "Life is pain.",
    "Why do I even try?",
    "This is fine.",
    "Everything is meaningless.",
    "I can't deal with this.",
    "Nobody understands me.",
    "Why bother?",
    "It's all over anyway."
    ]

    random_quote = random.choice(quotes)

    if channel:
        await channel.send(random_quote)

@bot.command()
async def roll(ctx, dice: str = "1d6"):
    try:
        amount, sides = map(int, dice.lower().split('d'))
        rolls = [random.randint(1, sides) for _ in range(amount)]
        await ctx.send(f"🎲 You rolled: {rolls} → Total: {sum(rolls)}")
    except Exception:
        await ctx.send("Usage: !roll <amount>d<sides> e.g., !roll 2d8")

@bot.command()
async def mock(ctx, member: commands.MemberConverter):
    """Mock a user in classic soyjack style."""
    soyjack_insults = [
        "Nothing ever happens in your brain, {name}.",
        "I can't believe {name} thinks they're smart.",
        "Why do you even try, {name}? It's cute.",
        "{name}, your life is pain and despair.",
        "Everything is meaningless to you, {name}.",
        "Nobody understands you, {name}, and they never will.",
        "It's all over anyway, {name}.",
        "Your opinions are like expired memes, {name}.",
        "{name}, the cringe is strong with you.",
        "Imagine thinking you’re important, {name}."
    ]

    insult = random.choice(soyjack_insults).format(name=member.display_name)
    await ctx.send(insult)


@bot.command()
async def ask(ctx, *, question: str):
    if(isolate_kunning(ctx)):
         await ctx.send("SYBAU LMAO DUMBASS MONKEY")
         return
    
    if ctx.message.reference and ctx.message.reference.resolved:
        original_message = ctx.message.reference.resolved.content
        full_question = f"{original_message} \n {question}"
    else:
        full_question = question

    processing_message = await ctx.send(f"🧠 Thinking...")

    try:
        response_data = await asyncio.to_thread(call_llm_for_general_purpose, full_question)

        if isinstance(response_data, str):
            await processing_message.edit(content=response_data)
            return
            
        await processing_message.edit(content=response_data.get("answer", "No answer found."))

    except Exception as e:
        await processing_message.edit(content=f"An unexpected error occurred: {e}")


@bot.command()
async def search(ctx, *, question: str):
    if(isolate_kunning(ctx)):
         await ctx.send("SYBAU LMAO DUMBASS MONKEY")
         return
    
    if ctx.message.reference and ctx.message.reference.resolved:
        original_message = ctx.message.reference.resolved.content
        full_question = f"{original_message} \n {question}"
    else:
        full_question = question

    processing_message = await ctx.send(f"🔎 Searching for news about: `{question}`...")

    try:
        response_data = await asyncio.to_thread(begin_procedure, full_question)

        if isinstance(response_data, str):
            await processing_message.edit(content=response_data)
            return
            
        embed = discord.Embed(
            title="News Summary",
            description=response_data.get("answer", "No answer found."),
            color=discord.Color.blue()
        )
        
        sources_text = []
        for i, link in enumerate(response_data.get("sources", []), 1):
             sources_text.append(f"[[{i}]]({link})")

        if sources_text:
            embed.add_field(name="Sources", value=" ".join(sources_text), inline=False)
        
        embed.set_footer(text=f"Query: {question}")

        await processing_message.edit(content="", embed=embed)

    except Exception as e:
        await processing_message.edit(content=f"An unexpected error occurred: {e}")


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Blitzcrank - the Great Steam Golem",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )

    embed.add_field(name="!ask <question>", value="Ask a general knowledge question to the AI.", inline=False)
    embed.add_field(name="!search <query>", value="Search the web and fact-check results.", inline=False)
    embed.add_field(name="!roll <XdY>", value="Roll dice. Example: `!roll 2d6` rolls two 6-sided dice.", inline=False)
    embed.add_field(name="!mock @user1 [@user2 ...]", value="Mock one or multiple users in classic soyjack style.", inline=False)
    embed.add_field(name="!help", value="Shows this help message.", inline=False)

    embed.set_footer(text="You can also mention the bot instead of using the '!' prefix.")
    
    await ctx.send(embed=embed)


def begin_procedure(question: str):

    # first query search engine
    search_results = query_searxng(question)

    if not search_results or not search_results['success']:
        return "Sorry, I couldn't find any recent news on that topic."

    # if we get results
    context = search_results['message']



    # then query the llm
    response_from_llm = call_llm_for_news(context, question)

    return response_from_llm


if __name__ == "__main__":
    bot.run(TOKEN)


    