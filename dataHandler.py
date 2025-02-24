import os
import pandas as pd 
import numpy as np

from constants import *
from singleton import *
from scrape import *

class DataHandler(metaclass=Singleton):


    SEASONS = ["2017-2018", "2018-2019","2019-2020","2020-2021","2021-2022","2022-2023","2023-2024","2024-2025"]
    CURRENT_SEASON = SEASONS[-1]

    def __init__(self, DATA_ROOT:str):

        self.root = DATA_ROOT
        self.data={}
        self.gk_data={}

        for season in self.SEASONS:

            data_path = os.path.join(self.root, f"{season}.csv")
            gk_data_path = os.path.join(self.root, f"gk{season}.csv")

            data_df = self._readData(data_path)
            gk_data_df = self._readData(gk_data_path)

            self.data[season] = data_df
            self.gk_data[season] = gk_data_df


    def _readData(self, path):

        try:
            df = pd.read_csv(path)
        except Exception as e:
            print(f"Error Occurred in {path}: {e}")
            df = None

        return df

    def get_data(self, season:str, gk:bool=False):

        if season not in self.SEASONS:
                raise ValueError(
                    f"No season data named {season}"
                    f"Select from {self.SEASONS}"
                )

        if(gk):
            return self.gk_data[season].copy()

        else:
            return self.data[season].copy()

    @staticmethod
    def compute_percentiles(df, cols):
        """
        Computes percentiles for given columns, inverting for negative impact metrics.
        
        Args:
        - df (pd.DataFrame): The player dataset.
        - cols (list): Columns to compute percentiles for.
        - negative_cols (set): Columns where higher values are worse.

        Returns:
        - pd.DataFrame: DataFrame with percentile columns added.
        """
        for col in cols:
            percentile_col = f"{col}_Percentile"
            
            if col in NEGATIVE_COLS:
                df[percentile_col] = 1.0 - df[col].rank(pct=True)  # Invert percentiles
            else:
                df[percentile_col] = df[col].rank(pct=True)  # Standard percentiling

        return df

    def scrape(self):

        player_modes = ["shooting", "passing", "passing_types", "gca", "defense", "possession", "playingtime", "misc"]
        team_modes = [ "possession"]
        player_ID = "min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1"
        team_ID = "stats_teams_possession_for"

        dataScraper = Scraper(player_modes=player_modes, player_ID=player_ID, 
                            team_modes=team_modes, team_ID=team_ID, season=self.CURRENT_SEASON)
        try:
            dfs = dataScraper.save_to_csv(self.root)
            data_df, gk_data_df = dfs[0], dfs[1]
            
            if data_df is not None and gk_data_df is not None:
                self.data[self.CURRENT_SEASON] = data_df
                self.gk_data[self.CURRENT_SEASON] = gk_data_df
            else:
                print("Scraping failed. Data not updated.")
        
        except Exception as e:
            print(f"Error in scraping: {e}")

        pass