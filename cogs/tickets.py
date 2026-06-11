import discord
from discord.ext import commands
from discord import app_commands


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Ticket",
        style=discord.ButtonStyle.green,
        emoji="🎫"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild

        existing = discord.utils.get(
            guild.channels,
            name=f"ticket-{interaction.user.name.lower()}"
        )

        if existing:
            await interaction.response.send_message(
                "You already have an open ticket.",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="Support Ticket",
            description="A staff member will assist you shortly.",
            color=discord.Color.green()
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"Ticket created: {channel.mention}",
            ephemeral=True
        )


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.red,
        emoji="🔒"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "Closing ticket...",
            ephemeral=True
        )

        await interaction.channel.delete()


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ticketpanel",
        description="Send the ticket panel."
    )
    async def ticket_panel(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="Support Center",
            description="Click the button below to create a support ticket.",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=TicketView()
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
