import discord
from discord import app_commands
from discord.ext import commands

from utils.dataHandler import DataHandler
from utils.constants import RADAR_TYPES, radarTypeToCols, radarToPos
from utils.plot import get_player_radar


import traceback

class PlotSelect(discord.ui.Select):
    """ Dropdown menu for player selection in the Plot Menu """

    def __init__(self, menu: "PlotMenu", options, handler_index):
        super().__init__(placeholder="Choose an option", options=options)
        self.menu = menu
        self.handler_index = handler_index

    async def callback(self, interaction: discord.Interaction):
        """ Handles dropdown selection and progresses the selection process """

        selected_value = self.values[0]
        print(f"Selected Value: {selected_value}")
        # Determine the appropriate handler
        handler_index = self.handler_index 
        handlers = self.menu.handlers[handler_index:]

        while self.menu.currentPlayer <= self.menu.n_players:
            for handler in handlers:
                print(f"Value passed to: {handler.__name__}")
                response = handler(selected_value)
                print(response)
                
                # Check if there's a next handler before printing
                if handler_index + 1 < len(self.menu.handlers):
                    print("Next Handler", self.menu.handlers[handler_index + 1].__name__)
                
                # If the handler is _player_handler, return league options for the next player
                if handler == self.menu._player_handler and self.menu.currentPlayer < self.menu.n_players:
                    
                    print("Last Handler detected")
                    self.menu.currentPlayer += 1  # Move to next player selection
                    next_handler_index = 2  # Reset handler index for the new player (start from league handler)
                    
                    # Fetch new league options based on selected season
                    leagues = self.menu.df["Competition"].unique()
                    league_options = [discord.SelectOption(label=l, value=l) for l in leagues]

                    new_select = PlotSelect(self.menu, league_options, next_handler_index)
                    self.menu.clear_items()
                    self.menu.add_item(new_select)
                    await interaction.response.edit_message(view=self.menu)
                    return
                
                if isinstance(response, str):  # Error message
                    await interaction.response.send_message(response, ephemeral=False)
                    return

                if isinstance(response, list):  # Update dropdown with new options
                    new_select = PlotSelect(self.menu, response, handler_index + 1)
                    self.menu.clear_items()
                    self.menu.add_item(new_select)
                    await interaction.response.edit_message(view=self.menu)
                    return

                
            
            # Move to the next player after processing
            print("Moving to next player")
            self.menu.currentPlayer += 1
            print(self.menu.currentPlayer)

        print("all players selected")            
        # # All players selected, delete the interaction message
        # await interaction.message.delete()

        print("final step now")
        # Extract final selections
        try:
            season = self.menu.playersData[1]["season"]
            player1 = self.menu.playersData[1]["name"]
            player2 = self.menu.playersData[2]["name"]
        except Exception as e:
            print(f"Error occurred: {e}")

        # Edit the original message instead of deleting it

        print("sending final message")
        print(self.menu.playersData[1]["data"])
        try:
            await interaction.response.defer()  # Prevents timeout
            # await interaction.edit_original_response(
            #     content=(
            #         f"**Selection Complete!**\n"
            #         f"Season: **{season}**\n"
            #         f"Player 1: **{player1}**\n"
            #         f"Player 2: **{player2}**"
            #     ),
            #     view=None  # ✅ Removes dropdown UI
            # )

            await interaction.edit_original_response(content="Generating radar plot...", view=None)

            # Call the radar function
            await get_player_radar(interaction, self.menu.playersData, self.menu.cols)

        except Exception as e:
            print(f"Error occurred: {e}")
            traceback.print_exc()


class PlotMenu(discord.ui.View):
    """ View managing dropdown selections """

    def __init__(self, bot, datahandler, n_players, interaction,cols=None):
        super().__init__()
        self.bot = bot
        self.datahandler = datahandler
        self.n_players = n_players
        self.interaction = interaction
        self.df = None
        self.cols = cols

        # Player data structure
        self.playersData = {
            1: {"season": None, "radarType": None, "league": None, "team": None, "name": None, "data": None},
            2: {"season": None, "radarType": None, "league": None, "team": None, "name": None, "data": None}
        }
        self.currentPlayer = 1

        # Handler functions
        self.handlers = (
            self._season_handler,
            self._radar_type_handler,
            self._league_handler,
            self._team_handler,
            self._player_handler
        )

        # Start with season selection
        self.add_item(PlotSelect(self, [discord.SelectOption(label=s, value=s) for s in self.datahandler.SEASONS], handler_index=0))

    def _season_handler(self, season):
        if season not in self.datahandler.SEASONS:
            return "Invalid Season"

        for playerNum in range(1, self.n_players + 1):
            self.playersData[playerNum]["season"] = season

        return [discord.SelectOption(label=rt, value=rt) for rt in RADAR_TYPES]

    def _radar_type_handler(self, radarType):
        print(f"Radar Type Selected: {radarType}")  # Debugging
        if radarType not in RADAR_TYPES:
            return "Invalid Radar Type"

        if self.cols is None:
            self.cols = radarTypeToCols[radarType]

        posn = radarToPos[radarType]
        print(type(posn))
        for playerNum in range(1, self.n_players + 1):
            self.playersData[playerNum]["radarType"] = radarType

        print(f"Fetching data for season: {self.playersData[1]['season']} with position: {posn}")
        try:
            if radarType == "Goalkeepers":
                self.df = self.datahandler.get_data(season=self.playersData[1]["season"], gk=True)
                print("GK Data", self.df.shape)
            else:
                self.df = self.datahandler.get_data(season=self.playersData[1]["season"])

            print(f"Data fetched, computing percentiles...", self.df.shape)

            # Filter data: Select only rows where Position is in posn and "90s Played" >= 5.0
            self.df = self.df[(self.df["Position"].isin(posn)) & (self.df["90s Played"] >= 5.0)]

            self.df = self.df[['Player', 'Squad', 'Competition', '90s Played'] + self.cols]

            # self.df = self.df[['Player', 'Squad', 'Competition', '90s Played'] + self.cols]
            print("columns reduced")

            self.df = self.datahandler.compute_percentiles(self.df, self.cols)
        except Exception as e:
            print(f"Error occurred: {e}")
            print(self.df.columns[:20])
        
        leagues = self.df["Competition"].unique()
        print(f"Leagues available: {leagues}")

        return [discord.SelectOption(label=l, value=l) for l in leagues]


    def _league_handler(self, league):

        if league not in self.df["Competition"].unique():
            return "Invalid League"

        
        self.playersData[self.currentPlayer]["league"] = league

        filteredData = self.df[self.df["Competition"] == league]
        self.playersData[self.currentPlayer]["data"] = filteredData

        teams = filteredData["Squad"].unique()

        return [discord.SelectOption(label=t, value=t) for t in teams]

    def _team_handler(self, team):
        if team not in self.df["Squad"].unique():
            return "Invalid Team"

        self.playersData[self.currentPlayer]["team"] = team
        pdata = self.playersData[self.currentPlayer]["data"]
        pdata = pdata[pdata["Squad"] == team]

        self.playersData[self.currentPlayer]["data"] = pdata  

        return [discord.SelectOption(label=p, value=p) for p in pdata["Player"].unique()]

    def _player_handler(self, player):
        if player not in self.df["Player"].unique():
            return "Invalid Player"

        self.playersData[self.currentPlayer]["name"] = player
        pdata = self.playersData[self.currentPlayer]["data"]
        self.playersData[self.currentPlayer]["data"] = pdata[pdata["Player"] == player]

        return None  # No more dropdowns after player selection

class Stat(commands.Cog):
    """ Discord Cog for Player Selection """

    def __init__(self, bot):
        self.bot = bot
        # self.datahandler = DataHandler  # Use the initialized DataHandler

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} is online")

    @app_commands.command(name="plot", description="Start player selection for radar chart")
    async def plot(self, interaction: discord.Interaction, n_players: int):
        """ Slash command to start selection """
        if n_players not in [1, 2]:
            await interaction.response.send_message("Only 1 or 2 players are supported.", ephemeral=False)
            return

        view = PlotMenu(self.bot, DataHandler, n_players, interaction)
        await interaction.response.send_message("Select an option:", view=view, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Stat(bot))
