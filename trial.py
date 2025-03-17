from utils.scrape import Scraper

# List of all modes
PLAYER_MODES = ["shooting", "passing", "passing_types", "gca", "defense", "possession", "playingtime", "misc"]
TEAM_MODES = [ "possession"]
PLAYER_IDENTIFIER = "min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1"
TEAM_IDENTIFIER = "stats_teams_possession_for"

SEASONS= ["2024-2025"]
DATA_DIR = "data"

for season in SEASONS:

    dataScraper = Scraper(player_modes=PLAYER_MODES, player_ID=PLAYER_IDENTIFIER, team_modes=TEAM_MODES, team_ID=TEAM_IDENTIFIER, season=season)

    dataScraper.save_to_csv(DATA_DIR)

# from utils.scrape import Scraper
# import os

# class outfieldScraper(Scraper):

#     def __init__(self, player_modes:list=["shooting", "passing", "passing_types", "gca", "defense", "possession", "playingtime", "misc"],\
#                  gk_modes:list=["keepers", "keepersadv"], team_modes= ["possession"], player_ID = "min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1", team_ID = "stats_teams_possession_for", season = "2024-2025"):
#         super().__init__(player_modes, gk_modes, team_modes, player_ID, team_ID, season)

#     def save_to_csv(self, DATA_DIR):

#         SeasonData = self.fetch_season_data(self.PLAYER_MODES, self.PLAYER_IDENTIFIER, self.TEAM_MODES, self.TEAM_IDENTIFIER, self.SEASON, gk=False)
#         fname = f"{self.SEASON}.csv"
#         SeasonData.to_csv(os.path.join(DATA_DIR,fname), index=False)
#         return SeasonData
    
# SEASONS= ["2017-2018","2018-2019","2019-2020","2020-2021","2021-2022","2022-2023","2023-2024"]  #  "2024-2025"]  #
# DATA_DIR = ""

# for season in SEASONS:

#     dataScraper = outfieldScraper(season=season)

#     dataScraper.save_to_csv(DATA_DIR)
