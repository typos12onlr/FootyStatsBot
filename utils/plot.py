import matplotlib
import matplotlib.pyplot as plt 
import matplotlib.gridspec as gridspec

import numpy as np 
from highlight_text import fig_text
import gc
from io import BytesIO
import os
import pandas as pd
from PIL import Image

from discord import Interaction
import discord

from utils.constants import RADAR_TYPES, radarToPos, FORWARD_COLS, WINGER_COLS, MIDFIELDER_COLS, DEFENDER_COLS, GOALKEEPER_COLS, radarTypeToCols, NEGATIVE_COLS

DATA_ROOT = "data"
CREDITS = "FC Discordelona"

COLOR1 = '#d67171' #f59eab
COLOR2 = '#8787e3'
COLORS = [COLOR1, COLOR2]

BGCOLOR = '#222222'

ALPHA_1 = 0.9
ALPHA_2 = 0.8
ALPHAS = [ALPHA_1, ALPHA_2]

TEXT_COLOR = '#f6f6f6'
HIGHLIGHT_COLOR = 'w'
EMP_COLOR = '#FFED02'

FONT = 'DejaVu Sans'



FBREF_LOGO = Image.open("static\\fb-logo.png")
SB_LOGO = Image.open("static\\Opta_Logo_Primary_01-1-1024x346.png")
FCD_QR = Image.open("static\\ExampleQRCode.png")   

def plot_player_radar(playerDataDict, cols):
    
    player1_info = playerDataDict[1]
    player2_info = playerDataDict[2]

    print(player2_info)

    p1_90s = float(player1_info['data']['90s Played'])
    p1 = f"{player1_info['name']} | {player1_info['team']} | 90's - {p1_90s:2}"
    if player2_info['name'] != None:
        p2_90s = float(player2_info['data']['90s Played'])
        p2 = f"{player2_info['name']} | {player2_info['team']} | 90's - {p2_90s:2}"
    else:
        p2 = ''

    radarType = player1_info['radarType']

    if cols is None:
        cols = radarTypeToCols[player1_info['radarType']]
    percentile_cols = [f'{col}_Percentile' for col in cols]

    p1_data = player1_info['data']
    p2_data = player2_info['data']
    p1_pvals = [100*p1_data[col].item() for col in percentile_cols]
    p1_vals = [p1_data[col].item() for col in cols]
    if(p2 == ''):
        p2_pvals = [0.0 for _ in range(len(p1_pvals))]
        p2_vals = [0.0 for _ in range(len(p1_vals))]
    else:
        p2_pvals = [100*p2_data[col].item() for col in percentile_cols]
        p2_vals = [p2_data[col].item() for col in cols]

    arr1 = np.asarray(p1_pvals)
    arr2 = np.asarray(p2_pvals)

    N = len(p1_vals)
    bottom = 0.0
    theta, width = np.linspace(0.0, 2 * np.pi, N, endpoint=False, retstep=True)

    fig = plt.figure(figsize=(16, 9), dpi=100)
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.5, 1])  # Allocate more space to radar plot
    ax = plt.subplot(gs[0], polar=True)  # Radar plot takes more space
    ax2 = plt.subplot(gs[1])
    # ax = plt.subplot(121, polar=True)
    fig.set_facecolor(BGCOLOR)
    ax.patch.set_facecolor(BGCOLOR)
    ax.set_rorigin(-20)


    bars = ax.bar(
        theta, height=arr1,
        width=width,
        bottom=bottom,
        color=COLOR1, edgecolor=HIGHLIGHT_COLOR, zorder=1,
        alpha=ALPHA_1,
        linewidth=0.5
    )
    bars2 = ax.bar(
        theta, arr2,
        width=width,
        bottom=bottom,
        color=COLOR2, zorder=1,
        alpha=ALPHA_2,
        edgecolor=HIGHLIGHT_COLOR, linewidth=0.5
    )

    ax.set_rticks(np.arange(0.0, 120.0, 20.0))
    ax.set_thetagrids((theta+width/2) * 180 / np.pi)
    # ax.set_rlabel_position(-100)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.grid(zorder=10.0, color=HIGHLIGHT_COLOR, linestyle='--', linewidth=0.5)
    ax.spines['polar'].set_visible(False)

    ticks = [str(i+1) for i in range(len(cols))]
    ax.set_xticklabels([])
    rotations = np.rad2deg(theta)

    for x, bar, rotation, label in zip(theta, bars, rotations, cols):
        lab = ax.text(x, 105, label, ha='center', va='center', color=TEXT_COLOR,
                        rotation=-rotation if rotation <= 90 or rotation >= 270 else 180 - rotation, 
                        rotation_mode='anchor', fontsize=6,
                        fontfamily=FONT)

    ax.spines["polar"].set_color(HIGHLIGHT_COLOR)
    ax.spines["polar"].set_linewidth(2)
    ax.set_yticklabels([])

    # ax2 = plt.subplot(122)
    ax2.patch.set_facecolor(BGCOLOR)
    ax2.axis('off')

    ax2.text(0.12, 1.02, 'Stat (Percentile in bracket)', fontsize=15, color=TEXT_COLOR,
                fontfamily=FONT)
    for i in range(len(cols)+1):
            ax2.text(0, 1.0-0.06*i, '|', fontsize=35, color=TEXT_COLOR, fontfamily=FONT)

    for i in range(32):
            ax2.text(0+0.04*i, 1, '_', fontsize=10, color=TEXT_COLOR, fontfamily=FONT)

    for i in range(len(cols)):
            ax2.text(0.05, 0.95-0.06*i, str(i+1)+' :  '+ cols[i], fontsize=10, color=TEXT_COLOR, fontfamily=FONT)
        
    for i in range(len(cols)+1):
            ax2.text(0.75, 1.0-0.06*i, '|', fontsize=35, color=TEXT_COLOR, fontfamily=FONT)

    ax2.text(0.8, 1.02, 'Player 1', fontsize=15, color=COLOR1, fontfamily=FONT)

    for i in range(len(cols)+1):
            ax2.text(1.005, 1.0-0.06*i, '|', fontsize=35, color=TEXT_COLOR, fontfamily=FONT)

    ax2.text(1.05, 1.02, 'Player 2', fontsize=15, color=COLOR2, fontfamily=FONT)

    for i in range(len(cols)):
        ax2.text(0.8, 0.95-0.06*i, 
            str(round(p1_vals[i], 2))+'  ('+str(round(p1_pvals[i], 2))+ ')', 
            fontsize=10, color=TEXT_COLOR, fontfamily=FONT)
        if(p2 != ''):
            ax2.text(1.05, 0.95-0.06*i, str(round(p2_vals[i], 2))+'  ('+str(round(p2_pvals[i], 2)) + ')', 
                fontsize=10, color=TEXT_COLOR, fontfamily=FONT)

    season = player1_info['season']
    text1 = f"{radarType}"
    text2 = f"({season} season)"

    long_title = False
    if len(text1) > len(text2):
        long_title = True
    print(long_title)
    fig_text(s=text1 + ('\n' if long_title else ' ') + text2, x=0.1, y=1.02,
                fontsize=15 if long_title else 20, color=EMP_COLOR, fontfamily=FONT, textalign='center')

    highlight_textprops = [{"color": COLOR1}, {"color": COLOR2}]
    fig_text(s=f"<{p1}>"+'\n'+f"<{p2}>", x=0.1, y=0.95 if long_title else 0.98,
                highlight_textprops=highlight_textprops,
                fontsize=12, color=TEXT_COLOR, fontfamily=FONT)

    ax2.text(-0.63, 1.12, '\n\n' + 'Design idea :  Tom Worville / The Athletic/ Football Slices'
                +'\n\n'+'Code base :  Soumyajit Bose (@Soumyaj15209314)', 
                fontsize=10, color=TEXT_COLOR, fontfamily=FONT)

    fig_text(x = 0.40, y = 0.95,
            s=f'Presented to you by : <{CREDITS}>',
            fontsize=15, color=TEXT_COLOR, fontfamily=FONT,
            highlight_textprops=[{"color": EMP_COLOR, "weight": "regular", "fontsize": 15}])
        
    ax3 = fig.add_axes([0.7, 0.95, 0.08, 0.08])
    ax3.axis('off')
    ax3.imshow(FBREF_LOGO)
    ax4 = fig.add_axes([0.80, 0.95, 0.08, 0.08])
    ax4.axis('off')
    ax4.imshow(SB_LOGO)
    ax5 = fig.add_axes([0.9, 0.92, 0.08, 0.12])
    ax5.axis('off')
    ax5.imshow(FCD_QR)

    # fig.tight_layout()

    # plt.show()
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    p1_name = playerDataDict[1]['name']
    p2_name = playerDataDict[2]['name'] if playerDataDict[2]['name'] != None else 'None'
    filename = p1_name + "_vs_" + p2_name + ".png"
    image = Image.open(buffer)
    image.save(filename, format='PNG')
    buffer.seek(0)
    fig.clear()    
    
    gc.collect()
    
    return buffer


async def get_player_radar(interaction: Interaction, playerMenu):
    """

    """
    playersDict = playerMenu.playersData
    stat_cols = playerMenu.cols
    buffer = plot_player_radar(playersDict, stat_cols)
    print("plotting done")
    p1_name = playersDict[1]['name']
    p2_name = playersDict[2]['name'] if playersDict[2]['name'] != None else 'None'
    season = playersDict[1]['season']
    await interaction.followup.send(file=discord.File(buffer, filename=f'radar_{p1_name}_{p2_name}_{season}.png'))
    
# async def get_player_radar(interaction: Interaction, playersDict , stat_cols):
#     """

#     """
    
#     buffer = plot_player_radar(playersDict, stat_cols)
#     print("plotting done")
#     p1_name = playersDict[1]['name']
#     p2_name = playersDict[2]['name'] if playersDict[2]['name'] != None else 'None'
#     season = playersDict[1]['season']
#     await interaction.followup.send(file=discord.File(buffer, filename=f'radar_{p1_name}_{p2_name}_{season}.png'))


