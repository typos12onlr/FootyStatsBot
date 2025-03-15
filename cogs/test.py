import discord 
from discord.ext import commands
from discord import app_commands, Interaction

class Test(commands.Cog):
    
    def __init__(self, bot):
        
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online")

    @app_commands.command(name="avatar", description="Send user avatar in embed (sends own avatar is no user selected)")
    async def avatar(self,interaction:Interaction, member:discord.Member=None):
        if member is None:
            member = interaction.user
        else:
            member=member
        
        avatar_embed = discord.Embed(title=f"{member.name}'s avatar", color=discord.Color.random())
        avatar_embed.set_image(url=member.avatar)
        avatar_embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)

        await interaction.response.send_message(embed=avatar_embed)

async def setup(bot):
    await bot.add_cog(Test(bot))