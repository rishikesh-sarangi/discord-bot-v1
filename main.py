from utils.searxNG import query_searxng
from utils.segragate_kunning import isolate_kunning
from utils.llm import call_llm_for_news, call_llm_for_general_purpose
import discord
from discord.ext import commands
import os
import asyncio
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
        title="CROCK: The Soy Boy Help Section",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ask <question>", value="Ask a general knowledge question.", inline=False)
    embed.add_field(name="!search <query>", value="Search for news articles.", inline=False)
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


    