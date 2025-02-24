radarToPos = {
    'Forwards': ['FW','FW,MF','MF,FW','FW,DF'],
    'Attacking Mids/Winger/Wingbacks': ['MF,FW','FW,MF','FW,DF','DF,FW'],
    'Central/Defensive/Wide Mids': ['MF,FW', 'MF','MF,DF'],
    'Centerbacks/Fullbacks/Wingbacks': ['DF','DF,FW','DF,MF'],
    'Goalkeepers': ['GK']
}

RADAR_TYPES = radarToPos.keys()

FORWARD_COLS = [
    "Shots Total",
    "Goals",
    "Non Penalty Expected Goals",
    "Expected Assists",
    "Passes Into Penalty Area",
    "Passes Into Final Third",
    "Shot Creating Actions",
    "Goal Creating Actions",
    "Successful Take Ons",
    "Successful Take On %",
    "Carries Into Penalty Area",
    "Progressive Passes Received",
    "Aerials Won",
    "Aerials Won %",
    "Dispossessed"
]

WINGER_COLS=[
    "Shots Total",
    "Goals",
    "Non Penalty Expected Goals",
    "Expected Assists",
    "Key Passes",
    "Passes Into Penalty Area",
    "Passes Into Final Third",
    "Shot Creating Actions",
    "Goal Creating Actions",
    "Successful Take Ons",
    "Successful Take On %",
    "Progressive Carrying Distance",
    "Progressive Carries",
    "Fouls Drawn",
    "Dispossessed"
]

MIDFIELDER_COLS=[
    "Progressive Passes",
    "Passes Into Final Third",
    "Passes Into Penalty Area",
    "Expected Assists",
    "Shot Creating Actions",
    "Goal Creating Actions",
    "Number Of Carries",
    "Successful Take Ons",
    "Successful Take On %",
    "Tackles Won",
    "Interceptions",
    "Dribblers Tackled %",
    "Aerials Won %",
    "Dispossessed",
    "Miscontrols"
]

DEFENDER_COLS=[
    "Passes Into Final Third",
    "Progressive Passes",
    "Progressive Carries",
    "Carries Into Final Third",
    "Expected Assists",
    "Successful Take Ons",
    "Successful Take on %",
    "Tackles Won",
    "Dribblers Tackled %",
    "Interceptions",
    "Dribbled Past",
    "Aerials Won",
    "Aerials Won %",
    "Dispossessed",
    "Miscontrols"
]

GOALKEEPER_COLS=[
    "Shots In Target Against",
    "PSxG Per SoT",
    "Save %",
    "PSxG Saved",
    "PK Against",
    "Pass Launch %",
    "Launched Passes Completed",
    "Avg Pass Length",
    "Def Outside Pen Area",
    "Avg Def Act Distance",
    "GK Launch %",
]

NEGATIVE_COLS = [
    "Dribbled Past",
    "Aerials Lost",
    "Dispossessed",
    "Miscontrols",
    "Yellow Cards",
    "Red Cards",
    "Second Yellows",
    "Fouls Committed",
    "Own Goals",
    "Offside",
    "Goals Against",
    "Shots On Target Against",
    "Losses",
    "PK Against",
    "PK Goals Against",
    "Free Kick Goals Against",
    "Corner Kick Goals Against",
    "PSxG Faced"
]

radarTypeToCols = {"Forwards": FORWARD_COLS,
                   "Attacking Mids/Winger/Wingbacks": WINGER_COLS,
                   "Central/Defensive/Wide Mids":MIDFIELDER_COLS,
                   "Centerbacks/Fullbacks/Wingbacks":DEFENDER_COLS,
                   "Goalkeepers": GOALKEEPER_COLS}

