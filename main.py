from utils.ddg import query_ddg
from utils.llm import call_llm_with_context
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from utils.discord_ui import ImagePaginatorView

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
    processing_message = await ctx.send(f"🔎 Searching for news about: `{question}`...")

    try:
        response_data = await asyncio.to_thread(begin_procedure, question
        )

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
async def ask_img(ctx, *, question: str):
    processing_message = await ctx.send(f"🔎 Searching for news and images about: `{question}`...")

    try:
        response_data = await asyncio.to_thread(begin_procedure, question, True)

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
        
        image_urls = response_data.get("images", []) 
        
        if not image_urls:
            embed.set_footer(text=f"Query: {question}")
            await processing_message.edit(content="", embed=embed)
            return

        view = ImagePaginatorView(image_urls=image_urls, embed=embed, author=ctx.author)
        
        view.base_embed.set_image(url=view.image_urls[0])
        view.base_embed.set_footer(text=f"Image 1 of {len(view.image_urls)}")
        
        if len(view.image_urls) == 1:
            view.next_button.disabled = True

        message = await processing_message.edit(content="", embed=view.base_embed, view=view)
        view.message = message

    except Exception as e:
        await processing_message.edit(content=f"An unexpected error occurred: {e}") 


def begin_procedure(question: str, is_img: bool = False):

    # first query duck duck go
    search_results = query_ddg(question, img=is_img)

    if not search_results or not search_results['success']:
        return "Sorry, I couldn't find any recent news on that topic."

    # if we get results 
    context = search_results['message']

    # then query the llm
    response_from_llm = call_llm_with_context(context, question)

    return response_from_llm


if __name__ == "__main__":
    bot.run(TOKEN)

    