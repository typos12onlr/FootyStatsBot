from selenium import webdriver
import pandas as pd
import time
import numpy as np
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from unidecode import unidecode

# Automatically download and use the correct ChromeDriver version
service = Service(ChromeDriverManager().install())



class Scraper:

    """
    A web scraper class for extracting soccer statistics from fbref.com.

    This class demonstrates encapsulation by bundling data and methods that operate on that data within
    a single unit. It provides a controlled interface for data access through its public methods while
    keeping implementation details private.

    Attributes:
        PLAYER_MODES (list): Types of player statistics to scrape
        TEAM_MODES (list): Types of team statistics to scrape
        PLAYER_IDENTIFIER (str): HTML attribute for player statistics tables
        TEAM_IDENTIFIER (str): HTML attribute for team statistics tables
        SEASON (str): The season for which to scrape data

    Methods:
        fetch_season_data(player_modes, player_identifier, team_modes, team_identifier, season):
            Fetches and processes complete season data for both players and teams.
            
        fetch_player_data(modes, season, identifier, use_class):
            Retrieves player statistics for specified modes and combines them into a single DataFrame.
            
        fetch_team_data(modes, season, identifier, use_class):
            Retrieves team statistics for specified modes and returns processed DataFrame.
            
        _initialize_driver():
            Creates and configures a new Selenium WebDriver instance.
            
        _fetch_mode_data_selenium(driver, mode, season, identifier, use_class, players):
            Fetches data for a specific statistical mode using Selenium.
            
        _clean_master_df(master_df):
            Cleans raw data by removing unnecessary rows and normalizing text.
            
        _rename_cols(df):
            Standardizes column names across different statistical categories.
            
        _convert_type(df):
            Converts DataFrame columns to appropriate data types.
            
        _filter_90s(df):
            Filters players based on minimum 90-minute appearances.
            
        _convert_to_per90(df):
            Normalizes statistics to per-90-minute metrics.
            
        _add_poss_data(playerData, teamData):
            Merges possession statistics from team data into player statistics.
            
        _poss_adj(df, stats):
            Adjusts defensive statistics based on team possession data.
    """

    def __init__(self, player_modes:list=["shooting", "passing", "passing_types", "gca", "defense", "possession", "playingtime", "misc"],\
                 team_modes:list=[ "possession"], \
                 player_ID: str = "min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1",\
                 team_ID: str= "stats_teams_possession_for",\
                 season:str="2024-2025"):
        
        """
        Initialize the Scraper with configuration parameters.

        Args:
            player_modes: List of stat types to scrape for players
            team_modes: List of stat types to scrape for teams
            player_ID: HTML attribute identifier for player tables
            team_ID: HTML attribute identifier for team tables
            season: Season to scrape data for
        """

        self.PLAYER_MODES = player_modes
        self.TEAM_MODES = team_modes
        self.PLAYER_IDENTIFIER = player_ID
        self.TEAM_IDENTIFIER = team_ID
        self.SEASON = season

        def_stats=   [ ["Tkl","Tackles"],
            ["TklW","Tackles Won"],
            ["Def 3rd","Tackles in Defensive Third"],
            ["Mid 3rd","Tackles in Middle Third"],
            ["Att 3rd","Tackles in Attacking Third"],
            ["Tkl","Number of Dribblers Tackled"],
            ["Att","Number of Dribbles Challenged"],
        # ["Tkl%","Dribblers Tackled %"],
            ["Lost","Dribbled Past"],
            ["Blocks","Total Blocks"],
            ["Sh","Shots Blocked"],
            ["Pass","Passes Blocked"],
            ["Int","Interceptions"],
            ["Tkl+Int","Tackles + Interceptions"],
            ["Clr","Clearances"],
            ["Err","Errors"]]

        self.def_stats=[i[1] for i in def_stats]

    def save_to_csv(self):

        """
        Update seasonal data into csv file.

        Returns:
            DataFrame: Processed and cleaned season data
        """

        seasonData = self.fetch_season_data(self.PLAYER_MODES, self.PLAYER_IDENTIFIER, self.TEAM_MODES, self.TEAM_IDENTIFIER, self.SEASON)
        fname = f"{self.SEASON}.csv"
        seasonData.to_csv(fname, index=False)
        return seasonData
        
    def fetch_season_data(self, player_modes:list, player_identifier:str, team_modes:list, team_identifier:str, season:str="2024-2025"):

        """
        Fetch and process complete season data for both players and teams.

        Args:
            player_modes: List of player statistics types to fetch
            player_identifier: HTML identifier for player tables
            team_modes: List of team statistics types to fetch
            team_identifier: HTML identifier for team tables
            season: Season to fetch data for

        Returns:
            DataFrame: Processed and cleaned season data
        """

        playerData = self._fetch_player_data(player_modes, season="2023-2024", identifier=player_identifier, use_class=True)

        playerData= self._clean_master_df(playerData)
        playerData= self._renameCols(playerData)
        playerData= self._convertType(playerData)
        playerData= self._filter90s(playerData)
        playerData= self._convertToPer90(playerData)

        teamData= self._fetch_team_data(team_modes, season, team_identifier, use_class=False)

        playerData= self._addPossData(playerData,teamData)
        playerData= self._possAdj(playerData,self.def_stats)
        
        return playerData

    def _fetch_player_data(self, modes: list, season: str="2024-2025", identifier:str="min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1", use_class=True ):
        """
        Fetches and combines player statistics data for multiple statistical modes.

        This method retrieves player statistics for each specified mode (e.g., shooting, passing),
        combines them into a single DataFrame, and performs initial data cleaning.

        Args:
            modes (list): List of statistical modes to fetch. Valid options include:
                        ["shooting", "passing", "passing_types", "gca", "defense", 
                        "possession", "playingtime", "misc"]
            season (str, optional): Season to fetch data for in format "YYYY-YYYY". 
                                Defaults to "2024-2025".
            identifier (str, optional): HTML attribute of the table tag to locate in the source.
                                    Defaults to class name for standard fbref tables.
            use_class (bool, optional): If True, uses class attribute to find table; 
                                    if False, uses ID. Defaults to True.

        Returns:
            pandas.DataFrame: Combined DataFrame containing all requested player statistics.
                            Index represents players, columns represent different statistics.
                            First columns contain player metadata (name, team, etc.),
                            followed by statistics from each requested mode.

        Raises:
            ValueError: If any mode in modes list is invalid
            RuntimeError: If data fetching fails for all retries
        """
        
        
        all_dfs= self._fetch_all_modes_selenium(modes=modes, season=season, identifier=identifier, use_class=use_class, players=True)   


        master_df = pd.DataFrame()

        for i in range(len(all_dfs)):
            df= all_dfs[i]
            if i==0:
                new=[]
                for column in df.columns:
                    new.append(column[1])
                df.columns=new
                stats_to_drop=['Matches']
                df.drop(columns=stats_to_drop,axis=1,inplace=True)
                master_df=pd.concat([master_df,df],axis=1)
            else:
                new=[]
                for column in df.columns:
                    new.append(column[1])
                df.columns=new
                stats_to_drop=['Rk','Player','Nation','Pos', 'Squad', 'Comp', 'Age', 'Born', '90s','Matches']
                df.drop(columns=stats_to_drop, axis=1, inplace=True)

                master_df=pd.concat([master_df,df],axis=1)
            # print(f"{i+1}/{len(all_dfs)}")
            i+=1 

        return master_df   

    def _fetch_team_data(self, modes: list, season: str="2024-2025", identifier:str="stats_teams_possession_for", use_class=False):
        """
        Fetches and processes team statistics data for specified modes.

        This method retrieves team-level statistics, particularly focused on possession data,
        which is used later for adjusting player statistics.

        Args:
            modes (list): List of statistical modes to fetch. For teams, typically 
                        only includes ["possession"], but can support other modes.
            season (str, optional): Season to fetch data for in format "YYYY-YYYY". 
                                Defaults to "2024-2025".
            identifier (str, optional): HTML attribute of the table tag to locate in the source.
                                    Defaults to ID for team possession table.
            use_class (bool, optional): If True, uses class attribute to find table; 
                                    if False, uses ID. Defaults to False.

        Returns:
            pandas.DataFrame: Processed DataFrame containing team statistics.
                            Index represents teams, columns represent statistics.
                            Includes possession metrics used for player stat adjustments.

        Raises:
            RuntimeError: If data fetching fails for all retries
            ValueError: If required possession data columns are missing
        """
        
        team_poss_df = self._fetch_all_modes_selenium(modes=modes,season=season,identifier=identifier, use_class=use_class, players=False)
        
        newCols=[]
        for i in team_poss_df[0].columns:
            newCols.append(i[1])
            # print(i[0], "|", i[1])

        team_df = team_poss_df[0]
        team_df.columns = newCols

        team_df.iloc[:,4] = team_df.iloc[:,4].astype('float')

        return team_df

    @staticmethod
    def _initialize_driver():
        """Initialize a new Selenium WebDriver instance."""
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment to run in background
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        
        return webdriver.Chrome(options=chrome_options)

    def _fetch_mode_data_selenium(self, driver, mode, season="2024-2025", identifier="min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1", use_class=True, players=True):
      
        """
        Fetch data for a given mode using Selenium.

        - If fetching fails, returns None.
        
        Args:
            driver: Selenium WebDriver instance.
            mode: The mode of stats to fetch.
            season: The season (e.g., "2024-2025").
            identifier: String specifying the table's **class** or **ID**.
            use_class: If `True`, searches by class; otherwise, searches by ID.
            players: If `True`, fetches **player** stats; if `False`, fetches **team** stats.
        
        Returns:
            DataFrame with extracted data or None if failed.
        """
        if players:
            url = f"https://fbref.com/en/comps/Big5/{season}/{mode}/players/{season}-Big-5-European-Leagues-Stats"
        else:
            url = f"https://fbref.com/en/comps/Big5/{season}/{mode}/squads/{season}-Big-5-European-Leagues-Stats"
        
        try:
            driver.get(url)

            # Wait for the table to load
            if use_class:
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'table.{identifier.replace(" ", ".")}'))
                )
            else:
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, identifier))
                )

            # Extract HTML and parse table
            html_source = table.get_attribute("outerHTML")
            df = pd.read_html(html_source)[0]

            print(f"✅ Successfully fetched data for {mode} ({df.shape[0]} rows, {df.shape[1]} cols)")
            return df  # Return data if successful

        except Exception as e:
            print(f"⚠️ Failed to fetch {mode}: {e}")
            return None  # Return None if failed

    def _fetch_all_modes_selenium(self, modes, season="2024-2025", identifier="min_width sortable stats_table shade_zero long now_sortable sticky_table eq1 eq2 re2 le1", use_class=True, players=True):
        
        """
        Fetches data for all specified modes using Selenium with automated retry logic.

        This method implements a robust fetching strategy with:
        - Automatic retries for failed requests
        - WebDriver reinitialization between retry batches
        - Random delays between requests to avoid rate limiting
        - Maximum time limit for retries

        Args:
            modes (list): List of statistical modes to fetch
            season (str, optional): Season to fetch data for in format "YYYY-YYYY". 
                                Defaults to "2024-2025".
            identifier (str, optional): HTML attribute to locate tables.
                                    Defaults to standard fbref table class.
            use_class (bool, optional): If True, uses class attribute; if False, uses ID. 
                                    Defaults to True.
            players (bool, optional): If True, fetches player stats; if False, fetches team stats. 
                                    Defaults to True.

        Returns:
            list: List of pandas.DataFrames, one for each successfully fetched mode.
                Failed modes are not included in the output.

        Notes:
            - Uses exponential backoff strategy for retries
            - Maximum retry time is 15 minutes
            - Includes random delays (2-5 seconds) between requests
            - Reinitializes WebDriver between retry batches to avoid stale sessions

        Raises:
            RuntimeError: If retry time limit is exceeded with remaining failed modes
        """

        all_dfs = []  # Store successful DataFrames
        failed_modes = modes  # Track modes that failed
        start_time = time.time()  # Start timer

        while failed_modes and (time.time() - start_time) < 900:  # Retry until success or 15 minutes
            current_failed_modes = []  # Modes that fail in this round

            print("\n🔄 Reinitializing WebDriver...\n")
            driver = self._initialize_driver()  # Reinitialize the driver

            for mode in failed_modes:
                df = self._fetch_mode_data_selenium(driver, mode, season, identifier, use_class, players)

                if df is not None:
                    all_dfs.append(df)  # Store successful fetch
                else:
                    current_failed_modes.append(mode)  # Keep track of failures
                
                # Random delay (2-5 seconds) before the next request
                delay = random.uniform(2, 5)
                print(f"⏳ Waiting {delay:.2f} sec before next request...\n")
                time.sleep(delay)

            driver.quit()  # Close the driver after each round
            failed_modes = current_failed_modes  # Update failed modes for the next retry batch

            if failed_modes:
                print(f"🔄 Retrying failed modes: {failed_modes}\n")

        if failed_modes:
            print(f"❌ These modes failed after 15 minutes: {failed_modes}")

        return all_dfs  # Return all successful DataFrames
    
    def _renameCols(self,df):

        """Rename columns to more descriptive names."""
        
        rename_list=[["Rk","Rk"],
        ["Player","Player"],
        ["Nation","Nation"],
        ["Pos","Position"],
        ["Squad","Squad"],
        ["Comp","Competition"],
        ["Age","Age"],
        ["Born","Born"],
        ["90s","90s Played"],
        ["Gls","Goals"],
        ["Sh","Shots Total"],
        ["SoT","Shots on Target"],
        ["SoT%","Shots on Target %"],
        ["Sh/90","Shots per 90"],
        ["SoT/90","Shots on Target per 90"],
        ["G/Sh","Goals per Shot"],
        ["G/SoT","Goals per Shot on Target"],
        ["Dist","Avg Shot Distance"],
        ["FK","Free Kicks"],
        ["PK","Penatly Kicks"],
        ["PKatt","Penalty Kicks Attempted"],
        ["xG","Expected Goals"],
        ["npxG","Non Penalty Expected Goals"],
        ["npxG/Sh","Non Penalty Expected Goals per shot"],
        ["G-xG","Goals - Expected Goals"],
        ["np:G-xG","Non Penalty Goals - Expected Goals"],
        ["Cmp","Total Passes Completed"],
        ["Att","Total Passes Attempted"],
        ["Cmp%","Total Pass Completion %"],
        ["TotDist","Total Passing Distance"],
        ["PrgDist","Progressive Passing Distance"],
        ["Cmp","Short Passes Completed"],
        ["Att","Short Passes Attempted"],
        ["Cmp%","Short Pass Completion %"],
        ["Cmp","Medium Passes Completed"],
        ["Att","Medium Passes Attempted"],
        ["Cmp%","Medium Pass Completion %"],
        ["Cmp","Long Passes Completed"],
        ["Att","Long Passes Attempted"],
        ["Cmp%","Long Pass Completion %"],
        ["Ast","Assists"],
        ["xAG","Expected Assisted Goals"],
        ["xA","Expected Assists"],
        ["A-xAG","Assists - Expected Assisted Goals"],
        ["KP","Key Passes"],
        ["1/3","Passes into Final Third"],
        ["PPA","Passes into Penalty Area"],
        ["CrsPA","Crosses into Penalty Area"],
        ["PrgP","Progressive Passes"],
        ["Att","Total Passes Attempted"],
        ["Live","Live-Ball Passes"],
        ["Dead","Dead-Ball Passes"],
        ["FK","Passes from Free Kicks"],
        ["TB","Through Balls"],
        ["Sw","Switches"],
        ["Crs","Crosses"],
        ["TI","Throw Ins Taken"],
        ["CK","Corner Kicks"],
        ["In","Inswinging Corner Kicks"],
        ["Out","Outswinging Corner Kicks"],
        ["Str","Straight Corner Kicks"],
        ["Cmp","Total Passes Completed"],
        ["Off","Total Passes Offside"],
        ["Blocks","Total Passes Blocked"],
        ["SCA","Shot Creating Actions"],
        ["SCA90","Shot Creating Actions per 90"],
        ["PassLive","SCA Pass Live"],
        ["PassDead","SCA Pass Dead"],
        ["TO","SCA Take Ons"],
        ["Sh","SCA Shot"],
        ["Fld","SCA Fouls Drawn"],
        ["Def","SCA Defensive Actions"],
        ["GCA","Goal Creating Actions"],
        ["GCA90","Goal Creating Actions per 90"],
        ["PassLive","GCA Pass Live"],
        ["PassDead","GCA Pass Dead"],
        ["TO","GCA Take Ons"],
        ["Sh","GCA Shot"],
        ["Fld","GCA Fouls Drawn"],
        ["Def","GCA Defensive Actions"],
        ["Tkl","Tackles"],
        ["TklW","Tackles Won"],
        ["Def 3rd","Tackles in Defensive Third"],
        ["Mid 3rd","Tackles in Middle Third"],
        ["Att 3rd","Tackles in Attacking Third"],
        ["Tkl","Number of Dribblers Tackled"],
        ["Att","Number of Dribbles Challenged"],
        ["Tkl%","Dribblers Tackled %"],
        ["Lost","Dribbled Past"],
        ["Blocks","Total Blocks"],
        ["Sh","Shots Blocked"],
        ["Pass","Passes Blocked"],
        ["Int","Interceptions"],
        ["Tkl+Int","Tackles + Interceptions"],
        ["Clr","Clearances"],
        ["Err","Errors"],
        ["Touches","Touches"],
        ["Def Pen","Touches in Defensive Penalty"],
        ["Def 3rd","Touches in Defensive Third"],
        ["Mid 3rd","Touches in Middle Third"],
        ["Att 3rd","Touches in Attacking Third"],
        ["Att Pen","Touches in Attacking Penalty Area"],
        ["Live","Live Ball Touches"],
        ["Att","Take Ons Attempted"],
        ["Succ","Successful Take Ons"],
        ["Succ%","Successful Take on %"],
        ["Tkld","Times Tackled"],
        ["Tkld%","Tackled %"],
        ["Carries","Number of Carries"],
        ["TotDist","Total Carrying Distance"],
        ["PrgDist","Progressive Carrying Distance"],
        ["PrgC","Progressive Carries"],
        ["1/3","Carries into Final Third"],
        ["CPA","Carries into Penalty Area"],
        ["Mis","Miscontrols"],
        ["Dis","Dispossessed"],
        ["Rec","Passes Received"],
        ["PrgR","Progressive Passes Received"],
        ["MP","Matches Played"],
        ["Min","Minutes Played"],
        ["Mn/MP","Minutes per Match"],
        ["Min%","Total Minutes Played %"],
        ["Starts","Starts"],
        ["Mn/Start","Minutes per Start"],
        ["Compl","Complete Matches Played"],
        ["Subs","Subbed On"],
        ["Mn/Sub","Minutes per Sub"],
        ["unSub","Subbed Off"],
        ["PPM","PPM"],
        ["onG","onG"],
        ["onGA","onGA"],
        ["+/-","Goals +/-"],
        ["+/-90","Goals +/- per 90"],
        ["On-Off","On-Off"],
        ["onxG","onxG"],
        ["onxGA","onxGA"],
        ["xG+/-","xG+/-"],
        ["xG+/-90","xG+/-90"],
        ["On-Off","On-Off"],
        ["CrdY","Yellow Cards"],
        ["CrdR","Red Cards"],
        ["2CrdY","Second Yellows"],
        ["Fls","Fouls Committed"],
        ["Fld","Fouls Drawn"],
        ["Off","Offside"],
        ["Crs","Crs"],
        ["Int","Int"],
        ["TklW","Tackles Won"],
        ["PKwon","Penalty Kicks Won"],
        ["PKcon","Penalty Kicks Converted"],
        ["OG","Own Goals"],
        ["Recov","Loose Balls Recovered"],
        ["Won","Aerials Won"],
        ["Lost","Aerials Lost"],
        ["Won%","Aerials Won %"]]

        newCols=[i[1] for i in rename_list]


        df.columns=newCols

        return df

    def _clean_master_df(self, master_df):
        """Clean and process the master dataframe."""
        master_df.dropna(subset=['Player'], inplace=True)

        rows,cols=master_df.shape
        for i in range(25,rows,26):
            master_df.drop(index=i,inplace=True)
        master_df['Player'] = master_df['Player'].apply(unidecode)
        master_df['Squad'] = master_df['Squad'].apply(unidecode)

        return master_df

    def _convertType(self, df):
        """Convert column types to appropriate data types."""
        df.fillna(0,inplace=True)
        rows,cols=df.shape
        for i in range(8,cols):
            df.iloc[:,i] = pd.to_numeric(df.iloc[:,i], errors='coerce')
            df.iloc[:,i]=df.iloc[:,i].astype('float')

        return df

    def _filter90s(self, df):
        """Filter players based on 90-minute appearances."""
        df_new = df[df['90s Played'] > 0]
        return df_new

    def _convertToPer90(self, df):
        """Convert statistics to per-90-minute metrics."""
        columns=df.columns
        cols=df.shape[1]
        for i in range(9,cols):
            if columns[i][-1]!="%":
                df.iloc[:, i] = df.iloc[:, i].div(df['90s Played'], axis=0)
        return df

    def _addPossData(self, playerData, teamData):
        """Add possession data to player statistics."""
        teamData['Squad'] = teamData['Squad'].apply(unidecode)
        possData=teamData[['Squad','Poss']]
        playerData = playerData.merge(possData, on='Squad', how='left')

        return playerData

    def _possAdj(self, df, stats):
        """Adjust statistics based on possession data."""
        def sigmoid(x):
            return 2/( 1+np.exp(-0.1*(x-50)))
        df["Poss"]=df["Poss"].apply(lambda x: sigmoid(x))
        for i in stats:
            rows=df.shape[0]
            #print(i)
            for j in range(rows):
                factor=df.loc[j,"Poss"]
                df.loc[j,i]=df.loc[j,i]*factor

        return df


