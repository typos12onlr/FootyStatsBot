from scrape import Scraper

# List of all modes
PLAYER_MODES = ["shooting", "passing", "passing_types", "gca", "defense", "possession", "playingtime", "misc"]
TEAM_MODES = [ "possession"]
PLAYER_IDENTIFIER = "min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1"
TEAM_IDENTIFIER = "stats_teams_possession_for"
SEASONS= ["2017-2018", "2018-2019","2019-2020","2020-2021","2021-2022"]

for season in SEASONS:

    dataScraper = Scraper(player_modes=PLAYER_MODES, player_ID=PLAYER_IDENTIFIER, team_modes=TEAM_MODES, team_ID=TEAM_IDENTIFIER, season=season)

    dataScraper.save_to_csv()