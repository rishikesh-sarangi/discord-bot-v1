import discord
class ImagePaginatorView(discord.ui.View):
    def __init__(self, *, image_urls: list, embed: discord.Embed, author: discord.User):
        super().__init__(timeout=300) 
        
        self.image_urls = image_urls
        self.base_embed = embed
        self.author = author   
        
        self.current_page = 0
        self.message = None 

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You can't control this menu.", ephemeral=True)
            return False
        return True

    async def update_message(self, interaction: discord.Interaction):
        self.base_embed.set_image(url=self.image_urls[self.current_page])
        self.base_embed.set_footer(text=f"Image {self.current_page + 1} of {len(self.image_urls)}")
        
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.image_urls) - 1

        await interaction.response.edit_message(embed=self.base_embed, view=self)

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.image_urls) - 1:
            self.current_page += 1
            await self.update_message(interaction)
            
    async def on_timeout(self):
        if self.message:
            original_embed = self.message.embeds[0]
            await self.message.edit(embed=original_embed, view=None)