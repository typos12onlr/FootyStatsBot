import numpy as np 
import pandas as pd 

from utils.constants import *
import discord

def scoutPlayer(playerInfo, percentile_df, n=10):
    '''
    args: 
        playerInfo (dictionary) : dictionary containing player information (name, team, league, radartype, data)
        percentile_df (pandas dataframe) : dataframe of eligible players 

    returns:
        similarPlayers (list) : list of "n" most similar players
    '''
    # Extract player's data
    player_data = playerInfo["data"]  # Shape (1, features)
    
    # Select only percentile-based features
    percentile_cols = [col for col in percentile_df.columns if col.endswith("_Percentile")]

    # Normalize percentiles to range [0,1]
    player_vector = player_data[percentile_cols].values / 100  # Shape (1, selected_features)
    all_players_vectors = percentile_df[percentile_cols].values / 100  # Shape (m, selected_features)

    # Compute cosine similarity manually using numpy
    dot_product = np.dot(all_players_vectors, player_vector.T).flatten()  # (m,)
    player_norm = np.linalg.norm(player_vector)  # Scalar
    all_players_norms = np.linalg.norm(all_players_vectors, axis=1)  # (m,)

    # Avoid division by zero
    similarities = dot_product / (all_players_norms * player_norm + 1e-9)

    # Create a DataFrame with similarity scores
    percentile_df["Similarity"] = similarities

    # Sort by similarity in descending order, exclude the player itself
    similar_players = percentile_df.sort_values(by="Similarity", ascending=False)

    # Exclude the given player from the list
    similar_players = similar_players[similar_players["Player"] != playerInfo["name"]]

    # Return the top n player names
    return similar_players["Player"].head(n).tolist()


async def get_similar_players(interaction: discord.Interaction, playerMenu):

    playerInfo = playerMenu.playersData[1]
    percentile_df = playerMenu.df

    similarPlayers = scoutPlayer(playerInfo, percentile_df)

    await interaction.followup.send(f"Similar players to {playerInfo['name']} are: {', '.join(similarPlayers)}")
    