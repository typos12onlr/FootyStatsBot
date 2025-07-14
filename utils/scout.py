import numpy as np 
import pandas as pd 

from utils.constants import *
import discord

def scoutPlayer(playerInfo, percentile_df, n=10, max_age=100):
    '''
    args: 
        playerInfo (dictionary) : dictionary containing player information (name, team, league, radartype, data)
        percentile_df (pandas dataframe) : dataframe of eligible players 
        max_age (int) : Maximum age of eligible players

    returns:
        similarPlayers (list) : list of "n" most similar players
    '''
    # Extract player's data
    player_data = playerInfo["data"]  # Shape (1, features)

    # Select only percentile-based features
    percentile_cols = [col for col in percentile_df.columns if col.endswith("_Percentile")]

    # Normalize percentiles to range [0,1]
    player_vector = player_data[percentile_cols].values / 100  # Shape (1, selected_features)

    # Extract the numerical age from "Age" column
    # Ensure Age is treated correctly regardless of dtype
    if percentile_df["Age"].dtype == object:
        percentile_df["Age"] = percentile_df["Age"].apply(lambda x: int(x.split("-")[0]) if isinstance(x, str) else x)

    # Filter players within the specified age range
    filtered_df = percentile_df[(percentile_df["Age"] <= max_age)]

    # If no players remain after filtering, return an empty list
    if filtered_df.empty:
        return []

    # Get the filtered players' percentile data
    all_players_vectors = filtered_df[percentile_cols].values / 100  # Shape (m_filtered, selected_features)

    # Compute cosine similarity manually using numpy
    dot_product = np.dot(all_players_vectors, player_vector.T).flatten()  # (m_filtered,)
    player_norm = np.linalg.norm(player_vector)  # Scalar
    all_players_norms = np.linalg.norm(all_players_vectors, axis=1)  # (m_filtered,)

    # Avoid division by zero
    similarities = dot_product / (all_players_norms * player_norm + 1e-9)

    # Add similarity scores to the filtered DataFrame
    filtered_df = filtered_df.copy()  # Avoid modifying the original DataFrame
    filtered_df["Similarity"] = similarities

    # Sort by similarity in descending order, exclude the player itself
    similar_players = filtered_df.sort_values(by="Similarity", ascending=False)
    similar_players = similar_players[similar_players["Player"] != playerInfo["name"]]

    # Select top N rows
    top_n = similar_players.head(n)

    # Format as "Player (Age)"
    return [f"{row['Player']} ({int(row['Age'])})" for _, row in top_n.iterrows()]



async def get_similar_players(interaction: discord.Interaction, playerMenu, **kwargs):

    playerInfo = playerMenu.playersData[1]
    percentile_df = playerMenu.df.copy()
    n_similar = kwargs["n_similar"]
    max_age = kwargs["max_age"]
    similarPlayers = scoutPlayer(playerInfo, percentile_df, n = n_similar, max_age= max_age)

    await interaction.followup.send(f"Here's your response {interaction.user.mention}\nSimilar players to {playerInfo['name']} ({str(playerInfo['age'])}) ({playerInfo['season']}) are: {', '.join(similarPlayers)}", ephemeral = False)
    