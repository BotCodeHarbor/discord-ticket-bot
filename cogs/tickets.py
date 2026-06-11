import discord
from discord.ext import commands
from discord import app_commands


SUPPORT_ROLE_NAME = "Support"


class DeleteTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Delete Ticket",
        emoji="🗑️",
        style=discord.ButtonStyle.danger
    )
    async def delete_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        support_role = discord.utils.get(
            interaction.guild.roles,
            name=SUPPORT_ROLE_NAME
        )

        if support_role not in interaction.user.roles:
            await interaction.response.send_message(
                "Only Support staff can delete tickets.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Deleting ticket...",
            ephemeral=True
        )

        await interaction.channel.delete()


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.red
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        support_role = discord.utils.get(
            interaction.guild.roles,
            name=SUPPORT_ROLE_NAME
        )

        if support_role not in interaction.user.roles:
            await interaction.response.send_message(
                "Only Support staff can close tickets.",
                ephemeral=True
            )
            return

        channel = interaction.channel

        ticket_owner = None

        for member in channel.members:
            if member.bot:
                continue

            if support_role in member.roles:
                continue

            ticket_owner = member
            break

        if ticket_owner:
            await channel.set_permissions(
                ticket_owner,
                overwrite=None
            )

        try:
            await channel.edit(
                name=f"closed-{channel.name}"
            )
        except Exception:
            pass

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=(
                f"Closed by {interaction.user.mention}\n\n"
                "The ticket has been closed.\n"
                "A Support member may delete it when appropriate."
            ),
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            view=DeleteTicketView()
        )


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.green
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild

        support_role = discord.utils.get(
            guild.roles,
            name=SUPPORT_ROLE_NAME
        )

        existing = discord.utils.get(
            guild.channels,
            name=f"ticket-{interaction.user.id}"
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
                send_messages=True,
                read_message_history=True
            )
        }

        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True
            )

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.id}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Support Ticket",
            description=(
                f"Welcome {interaction.user.mention}!\n\n"
                "Please describe your issue in detail and "
                "a Support member will assist you."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Created By",
            value=interaction.user.mention,
            inline=False
        )

        embed.set_footer(
            text="BotCodeHarbor Ticket System"
        )

        await channel.send(
            content=(
                interaction.user.mention
                if not support_role
                else f"{interaction.user.mention} {support_role.mention}"
            ),
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"Ticket created: {channel.mention}",
            ephemeral=True
        )


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
            title="🎫 Support Center",
            description=(
                "Need help?\n\n"
                "Click the button below to create a private ticket."
            ),
            color=discord.Color.green()
        )

        embed.add_field(
            name="How It Works",
            value=(
                "• Create a ticket\n"
                "• Speak with Support\n"
                "• Support closes the ticket\n"
                "• Ticket can then be deleted"
            ),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            view=TicketView()
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
