# Importing the necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Reading the data from the CSV file
data = pd.read_csv('randomdata123.csv')

# 1. a summary of the most important stats: goals, xG , shots, etc.
# Count the number of 'Goal' outcomes in the 'shot_outcome' column
goals_by_team = data[data['shot_outcome'] == 'Goal'].groupby('team').size()

# Calculate the total shots for each team by filtering out rows where 'shot_outcome' is not NaN
# and then counting the occurrences for each team
total_shots_by_team = data[data['type'] == 'Shot'].groupby('team').size()

# Calculate the total expected goals (xG) for each team
total_xg_by_team = data.groupby('team')['shot_statsbomb_xg'].sum()

# 2. One of the most recognized metrics is possession share between teams
# Calculate the total possession for each team
total_possession_by_team = data.groupby('possession_team')["duration"].sum()
# percentage possession
total_possession_by_team = round(total_possession_by_team / total_possession_by_team.sum() * 100, 2)

# display the cumulative xG progression
data['timestamp'] = pd.to_datetime(data['timestamp'], format='%H:%M:%S.%f')
data.sort_values('timestamp', inplace=True)

# Calculate cumulative xG for each shot
data['cumulative_xg'] = data.groupby('team')['shot_statsbomb_xg'].cumsum()

# Resample the data into 1-minute bins and take the max of the cumulative xG in that bin for each team
# We pivot the table first to ensure 'team' remains a column after resampling
team_cumulative_xg = data.pivot_table(index='timestamp', columns='team', values='cumulative_xg').resample('1T').max().fillna(method='ffill')

# Extract minutes from the timestamp to use as x-axis values
team_cumulative_xg.index = team_cumulative_xg.index.map(lambda x: x.minute)

fig, ax = plt.subplots()

# Iterate through the columns (teams) in team_cumulative_xg and plot
for team in team_cumulative_xg.columns:
    ax.plot(team_cumulative_xg.index, team_cumulative_xg[team], label=team)

ax.set_xlabel('Time (min)')
ax.set_ylabel('Cumulative xG')
ax.set_title('Cumulative xG Progression for Both Teams')
ax.legend()
ax.grid(True)
plt.tight_layout()

# Filter for shot events
shot_events_new = data[data['type'] == 'Shot'].copy()

# Ensure the 'shot_statsbomb_xg' column is numeric
shot_events_new['shot_statsbomb_xg'] = pd.to_numeric(shot_events_new['shot_statsbomb_xg'], errors='coerce')

# Aggregate xG by player
player_xg_contribution_new = shot_events_new.groupby('player')['shot_statsbomb_xg'].sum().reset_index()

# Sort by xG contribution
player_xg_contribution_sorted_new = player_xg_contribution_new.sort_values(by='shot_statsbomb_xg', ascending=False)
fig, ax = plt.subplots()

# Plotting player xG contribution as a bar chart with adjusted size and font size
ax.barh(player_xg_contribution_sorted_new['player'], player_xg_contribution_sorted_new['shot_statsbomb_xg'], color='skyblue')
ax.set_xlabel('Total xG Contribution')
ax.set_ylabel('Player')
ax.set_title('Player Contribution to xG')
ax.invert_yaxis()
plt.tight_layout()

# Adjusting the other charts to include values on the bars
fig, axs = plt.subplots(2, 2)

# Goals by team with values on bars
bars_goals = axs[0, 0].bar(goals_by_team.index, goals_by_team.values, color='skyblue')
axs[0, 0].set_title('Goals by Team')
axs[0, 0].set_ylabel('Goals')
axs[0, 0].set_xlabel('Team')
axs[0, 0].tick_params(axis='x')
for bar in bars_goals:
    height = bar.get_height()
    axs[0, 0].annotate('{}'.format(height),
                       xy=(bar.get_x() + bar.get_width() / 2, height / 2),
                       textcoords="offset points",
                       ha='center', va='bottom')

# Total shots by team with values on bars
bars_shots = axs[0, 1].bar(total_shots_by_team.index, total_shots_by_team.values, color='lightgreen')
axs[0, 1].set_title('Total Shots by Team')
axs[0, 1].set_ylabel('Total Shots')
axs[0, 1].set_xlabel('Team')
axs[0, 1].tick_params(axis='x')
for bar in bars_shots:
    height = bar.get_height()
    axs[0, 1].annotate('{}'.format(height),
                       xy=(bar.get_x() + bar.get_width() / 2, height/2),
                       textcoords="offset points",
                       ha='center', va='bottom')

# Total expected goals (xG) by team with values on bars (if data available)
if not total_xg_by_team.empty:
    bars_xg = axs[1, 0].bar(total_xg_by_team.index, total_xg_by_team.values, color='salmon')
    axs[1, 0].set_title('Total Expected Goals (xG) by Team')
    axs[1, 0].set_ylabel('Total xG')
    axs[1, 0].set_xlabel('Team')
    axs[1, 0].tick_params(axis='x')
    axs[1, 0].size = 10
    for bar in bars_xg:
        height = bar.get_height()
        axs[1, 0].annotate('{:.2f}'.format(height),
                           xy=(bar.get_x() + bar.get_width() / 2, height / 2),
                           textcoords="offset points",
                           ha='center', va='bottom')
else:
    axs[1, 0].text(0.5, 0.5, 'xG data not available', ha='center', va='center', fontsize=12)

# The possession share chart is a pie chart and does not require value annotations
if not total_possession_by_team.empty:
    axs[1, 1].pie(total_possession_by_team, labels=total_possession_by_team.index, autopct='%1.1f%%', startangle=140)
    axs[1, 1].set_title('Possession Share by Team')
else:
    axs[1, 1].text(0.5, 0.5, 'Possession data not available', ha='center', va='center', fontsize=12)


plt.tight_layout()
plt.show()