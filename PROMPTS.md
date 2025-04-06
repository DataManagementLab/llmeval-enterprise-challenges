# Prompt Templates and Example Prompts

## Headline Experiment & The Data Challenge

### Headline Experiment & Exp. 1 - 3: Enterprise vs. public tables & Textual vs. numerical data & Table width and sparsity

Prompt template:

```
prompt_chat_template:
  - role: "user"
    content: |-
      Predict the column types of the following tables. 
      Use only column types this list: {{all_column_types}}
      Provide just the column types as a JSON list without any introduction or explanation.
  - "{{examples}}"
  - role: "user"
    content: "{{table}}"

example_chat_template:
  - role: "user"
    content: "{{table}}"
  - role: "assistant"
    content: "{{column_types}}"
```

Example prompt (with table and column names):

```
"messages": [
    {
        "role": "user",
        "content": "Predict the column types of the following tables. \nUse only column types this list: [\"address\", \"baseball.experience_years\", \"baseball.manager.all_star_games_managed\", \"baseball.manager.championship_wins\", \"baseball.manager.ejections\", \"baseball.manager.games_managed\", \"baseball.manager.games_over_.5\", \"baseball.manager.name\", \"baseball.manager.playoff_appearances\", \"baseball.manager.playoff_total_losses\", \"baseball.manager.playoff_total_wins\", \"baseball.manager.playoff_win_loss_percentage\", \"baseball.manager.teams_avg_finish\", \"baseball.manager.teams_best_finish\", \"baseball.manager.teams_worst_finish\", \"baseball.manager.total_championship_wins\", \"baseball.manager.total_losses\", \"baseball.manager.total_ties\", \"baseball.manager.total_wins\", \"baseball.manager.win_loss_percentage\", \"baseball.player.age\", \"baseball.player.batting_side\", \"baseball.player.height\", \"baseball.player.name\", \"baseball.player.position\", \"baseball.player.throwing_hand\", \"baseball.player.weight\", \"baseball.player.wins_above_replacement\", \"baseball.team.at_bats\", \"baseball.team.average_age\", \"baseball.team.balks\", \"baseball.team.bases_on_balls\", \"baseball.team.batters_faced\", \"baseball.team.bb9\", \"baseball.team.cauught_stealing\", \"baseball.team.complete_game\", \"baseball.team.doubles\", \"baseball.team.earned_runs\", \"baseball.team.era\", \"baseball.team.era+\", \"baseball.team.fip\", \"baseball.team.games_behind\", \"baseball.team.games_finished\", \"baseball.team.games_over_.5\", \"baseball.team.games_played\", \"baseball.team.games_started\", \"baseball.team.grounded_double_plays\", \"baseball.team.h9\", \"baseball.team.hit_by_pitch\", \"baseball.team.hits\", \"baseball.team.home_runs\", \"baseball.team.hr9\", \"baseball.team.innings_pitched\", \"baseball.team.intentional_bases_on_balls\", \"baseball.team.losses\", \"baseball.team.name\", \"baseball.team.number_of_hall_of_famers\", \"baseball.team.number_of_players\", \"baseball.team.obp\", \"baseball.team.ops\", \"baseball.team.ops+\", \"baseball.team.plate_appearances\", \"baseball.team.playoffs_participations\", \"baseball.team.runners_left_on_base\", \"baseball.team.runs\", \"baseball.team.runs_allowed_per_game\", \"baseball.team.runs_batted_in\", \"baseball.team.runs_scored_per_game\", \"baseball.team.sacrifice_flies\", \"baseball.team.sacrifice_hits\", \"baseball.team.saves\", \"baseball.team.shutouts\", \"baseball.team.shutouts_by_team\", \"baseball.team.slg\", \"baseball.team.so/w\", \"baseball.team.so9\", \"baseball.team.stolen_bases\", \"baseball.team.strikeouts\", \"baseball.team.total_at_bats\", \"baseball.team.total_ba\", \"baseball.team.total_bases\", \"baseball.team.total_championship_wins\", \"baseball.team.total_division_wins\", \"baseball.team.total_games_played\", \"baseball.team.total_hits\", \"baseball.team.total_home_runs\", \"baseball.team.total_losses\", \"baseball.team.total_number_of_players\", \"baseball.team.total_runs\", \"baseball.team.total_runs_allowed\", \"baseball.team.total_wins\", \"baseball.team.triples\", \"baseball.team.whip\", \"baseball.team.wild_pitches\", \"baseball.team.win_loss_percentage\", \"baseball.team.wins\", \"basketball.coach.franchise_games_coached\", \"basketball.coach.franchise_losses\", \"basketball.coach.franchise_sesaons\", \"basketball.coach.franchise_wins\", \"basketball.coach.name\", \"basketball.coach.playoff_franchise_games_coached\", \"basketball.coach.playoff_franchise_losses\", \"basketball.coach.playoff_franchise_wins\", \"basketball.coach.playoff_total_games_coached\", \"basketball.coach.playoff_total_losses\", \"basketball.coach.playoff_total_wins\", \"basketball.coach.playoffs_games_coached\", \"basketball.coach.playoffs_losses\", \"basketball.coach.playoffs_wins\", \"basketball.coach.season_games_coached\", \"basketball.coach.season_losses\", \"basketball.coach.season_wins\", \"basketball.coach.total_games_coached\", \"basketball.coach.total_losses\", \"basketball.coach.total_seasons\", \"basketball.coach.total_wins\", \"basketball.coach.total_wins_percentage\", \"basketball.player.2-point_field_goals_attempts_per_game\", \"basketball.player.2-point_field_goals_per_game\", \"basketball.player.2-point_field_goals_percentage\", \"basketball.player.3-point_field_goals_attempts_per_game\", \"basketball.player.3-point_field_goals_per_game\", \"basketball.player.3-point_field_goals_percentage\", \"basketball.player.age\", \"basketball.player.assists_per_game\", \"basketball.player.blocks_per_game\", \"basketball.player.defensive_rebounds_per_game\", \"basketball.player.effective_field_goals_percentage\", \"basketball.player.field_goals_attempts_per_game\", \"basketball.player.field_goals_per_game\", \"basketball.player.field_goals_percentage\", \"basketball.player.fouls_per_game\", \"basketball.player.free_throws_per_game\", \"basketball.player.free_throws_percentage\", \"basketball.player.games_played\", \"basketball.player.games_started\", \"basketball.player.minutes_per_game\", \"basketball.player.name\", \"basketball.player.offensive_rebounds_per_game\", \"basketball.player.points_per_game\", \"basketball.player.position\", \"basketball.player.rebounds_per_game\", \"basketball.player.steals_per_game\", \"basketball.player.three_throw_attempts_per_game\", \"basketball.player.turnovers_per_game\", \"basketball.team.2-point_field_goals_attempts_per_game\", \"basketball.team.2-point_field_goals_per_game\", \"basketball.team.2-point_field_goals_percentage\", \"basketball.team.3-point_field_goals_attempts_per_game\", \"basketball.team.3-point_field_goals_per_game\", \"basketball.team.3-point_field_goals_percentage\", \"basketball.team.assists_per_game\", \"basketball.team.blocks_per_game\", \"basketball.team.defensive_rebounds_per_game\", \"basketball.team.field_goals_attempts_per_game\", \"basketball.team.field_goals_per_game\", \"basketball.team.field_goals_percentage\", \"basketball.team.fouls_per_game\", \"basketball.team.free_throws_per_game\", \"basketball.team.free_throws_percentage\", \"basketball.team.games_behind\", \"basketball.team.games_played\", \"basketball.team.losses\", \"basketball.team.minutes_per_game\", \"basketball.team.name\", \"basketball.team.offensive_rebounds_per_game\", \"basketball.team.points_opponent_per_game\", \"basketball.team.points_per_game\", \"basketball.team.rebounds_per_game\", \"basketball.team.simple_rating_system\", \"basketball.team.steals_per_game\", \"basketball.team.three_throw_attempts_per_game\", \"basketball.team.turnovers_per_game\", \"basketball.team.win_loss_percentage\", \"basketball.team.wins\", \"birthdate\", \"city\", \"country\", \"football.coach.name\", \"football.player.adj_net_yards_per_pass_attempt\", \"football.player.adj_yards_per_pass_attempt\", \"football.player.age\", \"football.player.catch_percentage\", \"football.player.comebacks_led\", \"football.player.first_down_passings\", \"football.player.first_down_receiving\", \"football.player.first_down_rushing\", \"football.player.fumbles\", \"football.player.fumbles_forced\", \"football.player.fumbles_recovered\", \"football.player.fumbles_recovered_touchdowns\", \"football.player.fumbles_recovered_yards\", \"football.player.game_winning_drives\", \"football.player.games_played\", \"football.player.games_started\", \"football.player.gets_sacked\", \"football.player.gets_sacked_percentage\", \"football.player.interception_percentage\", \"football.player.interception_touchdowns\", \"football.player.interception_yards\", \"football.player.interception_yards_longest\", \"football.player.interceptions\", \"football.player.interceptions_thrown\", \"football.player.longest_pass_yards\", \"football.player.longest_reception\", \"football.player.longest_rush_yards\", \"football.player.name\", \"football.player.net_yards_per_pass_attempt\", \"football.player.pass_targets\", \"football.player.passes_attempted\", \"football.player.passes_completed\", \"football.player.passes_completed_percentage\", \"football.player.passes_defended\", \"football.player.passing_touchdowns\", \"football.player.passing_touchdowns_percentage\", \"football.player.passing_yards\", \"football.player.passing_yards_per_game\", \"football.player.position\", \"football.player.qb_rating\", \"football.player.qb_rating_old\", \"football.player.qb_record\", \"football.player.receiving_touchdowns\", \"football.player.receiving_yards\", \"football.player.receiving_yards_per_game\", \"football.player.receiving_yards_per_reception\", \"football.player.receiving_yards_per_target\", \"football.player.reception_per_game\", \"football.player.receptions\", \"football.player.rushing_attempted\", \"football.player.rushing_attempted_per_game\", \"football.player.rushing_touchdowns\", \"football.player.rushing_yards\", \"football.player.rushing_yards_per_game\", \"football.player.sacks\", \"football.player.scrimmage_touchdowns\", \"football.player.scrimmage_yards\", \"football.player.scrimmage_yards_per_touch\", \"football.player.tackles_assists\", \"football.player.tackles_combined\", \"football.player.tackles_for_loss\", \"football.player.tackles_qb_hits\", \"football.player.tackles_safeties\", \"football.player.tackles_solo\", \"football.player.touches\", \"football.player.yards_lost_due_to_sack\", \"football.player.yards_per_pass_attempt\", \"football.player.yards_per_pass_completion\", \"football.player.yards_per_rush_attempt\", \"football.stadium.games_played\", \"football.stadium.name\", \"football.team.championship_wins\", \"football.team.conference_championship_wins\", \"football.team.defensive_srs\", \"football.team.division_championship_wins\", \"football.team.expected_points_by_defense\", \"football.team.first_down\", \"football.team.first_down_passings\", \"football.team.first_down_penalties\", \"football.team.first_down_rushing\", \"football.team.fumbles_lost\", \"football.team.games_played\", \"football.team.interceptions_thrown\", \"football.team.losses\", \"football.team.margin_of_victory\", \"football.team.name\", \"football.team.net_yards_per_pass_attempt\", \"football.team.offensive_plays\", \"football.team.offensive_srs\", \"football.team.passes_attempted\", \"football.team.passes_completed\", \"football.team.passing_touchdowns\", \"football.team.passing_yards\", \"football.team.penalties\", \"football.team.penalty_yards\", \"football.team.playoffs_participations\", \"football.team.playoffs_total_losses\", \"football.team.playoffs_total_wins\", \"football.team.playoffs_win_loss_percentage\", \"football.team.points_diff\", \"football.team.points_opponent\", \"football.team.points_scored\", \"football.team.rushing_attempted\", \"football.team.rushing_touchdowns\", \"football.team.rushing_yards\", \"football.team.scoring_drives_percentage\", \"football.team.simple_rating_system\", \"football.team.strength_of_schedule\", \"football.team.super_bowl_wins\", \"football.team.takeaways\", \"football.team.ties\", \"football.team.total_losses\", \"football.team.total_ties\", \"football.team.total_wins\", \"football.team.turnover_drives_percentage\", \"football.team.win_loss_percentage\", \"football.team.wins\", \"football.team.yards\", \"football.team.yards_per_play\", \"football.team.yards_per_rush_attempt\", \"hockey.league\", \"hockey.player.active_status\", \"hockey.player.age\", \"hockey.player.assists\", \"hockey.player.average_time_on_ice\", \"hockey.player.blocks\", \"hockey.player.catches\", \"hockey.player.event_strength_assists\", \"hockey.player.event_strength_goals\", \"hockey.player.faceoff_losses\", \"hockey.player.faceoff_percentage\", \"hockey.player.faceoff_wins\", \"hockey.player.first_name\", \"hockey.player.ga_percentage\", \"hockey.player.game_winning_goals\", \"hockey.player.games_played\", \"hockey.player.games_started\", \"hockey.player.goalie_point_shares\", \"hockey.player.goals\", \"hockey.player.goals_against\", \"hockey.player.goals_against_average\", \"hockey.player.goals_saved_above_average\", \"hockey.player.height\", \"hockey.player.hits\", \"hockey.player.id\", \"hockey.player.jersey_number\", \"hockey.player.last_name\", \"hockey.player.losses\", \"hockey.player.minutes\", \"hockey.player.name\", \"hockey.player.penaltie_minutes\", \"hockey.player.plus_minus\", \"hockey.player.point_shares\", \"hockey.player.points\", \"hockey.player.position\", \"hockey.player.power_play_assists\", \"hockey.player.power_play_goals\", \"hockey.player.quality_starts\", \"hockey.player.quality_starts_percentage\", \"hockey.player.really_bad_starts\", \"hockey.player.save_percentage\", \"hockey.player.saves\", \"hockey.player.shooting_percentage\", \"hockey.player.shoots\", \"hockey.player.short_handed_assists\", \"hockey.player.short_handed_goals\", \"hockey.player.short_on_goals\", \"hockey.player.shots_against\", \"hockey.player.shutouts\", \"hockey.player.ties_plus_overtime_losses\", \"hockey.player.time_on_ice\", \"hockey.player.weight\", \"hockey.player.wins\", \"hockey.stadium.active\", \"hockey.stadium.capacity\", \"hockey.stadium.id\", \"hockey.stadium.name\", \"hockey.team.championship_wins\", \"hockey.team.games_played\", \"hockey.team.goals_against\", \"hockey.team.goals_for\", \"hockey.team.id\", \"hockey.team.losses\", \"hockey.team.name\", \"hockey.team.overtime_losses\", \"hockey.team.playoff_appearances\", \"hockey.team.playoff_games_played\", \"hockey.team.playoff_goal_diff\", \"hockey.team.playoff_goals\", \"hockey.team.playoff_goals_against\", \"hockey.team.playoff_losses\", \"hockey.team.playoff_overtime_losses\", \"hockey.team.playoff_overtime_wins\", \"hockey.team.playoff_ties\", \"hockey.team.playoff_wins\", \"hockey.team.points\", \"hockey.team.points_percentage\", \"hockey.team.r_points_percentage\", \"hockey.team.regulation_time_record\", \"hockey.team.rg_points_percentage\", \"hockey.team.simple_rating_system\", \"hockey.team.stanley_cup_wins\", \"hockey.team.strength_of_schedule\", \"hockey.team.ties\", \"hockey.team.total_division_wins\", \"hockey.team.total_games_played\", \"hockey.team.total_losses\", \"hockey.team.total_overtime_losses\", \"hockey.team.total_playoff_conference_wins\", \"hockey.team.total_points\", \"hockey.team.total_seasons\", \"hockey.team.total_ties\", \"hockey.team.total_wins\", \"hockey.team.win_loss_percentage\", \"hockey.team.wins\", \"hockey.team.wins_in_regulation\", \"latitude\", \"longitude\", \"note\", \"notes\", \"rank\", \"school\", \"soccer.attendance_per_game\", \"soccer.player.90s\", \"soccer.player.age\", \"soccer.player.assists\", \"soccer.player.assists_per_90_min\", \"soccer.player.expected_assists\", \"soccer.player.expected_assists_per_90_min\", \"soccer.player.expected_goals\", \"soccer.player.expected_goals_+assists_per_90_min\", \"soccer.player.expected_goals_per_90_min\", \"soccer.player.expected_non_penalty_goals\", \"soccer.player.expected_non_penalty_goals_+assists\", \"soccer.player.expected_non_penalty_goals_+assists_per_90_min\", \"soccer.player.expected_non_penalty_goals_per_90_min\", \"soccer.player.games_played\", \"soccer.player.games_started\", \"soccer.player.goals\", \"soccer.player.goals_+assists_-penalties_per_90_min\", \"soccer.player.goals_+assists_per_90_min\", \"soccer.player.goals_per_90_min\", \"soccer.player.matches\", \"soccer.player.minutes_played\", \"soccer.player.name\", \"soccer.player.non_penalty_goals\", \"soccer.player.non_penalty_goals_per_90_min\", \"soccer.player.penalties_attemted\", \"soccer.player.penalty_kicks_made\", \"soccer.player.position\", \"soccer.player.red_cards\", \"soccer.player.yellow_cards\", \"soccer.team.draws\", \"soccer.team.expected_goals\", \"soccer.team.expected_goals_allowed\", \"soccer.team.expected_goals_difference\", \"soccer.team.expected_goals_difference_per_90_min\", \"soccer.team.games_played\", \"soccer.team.goals\", \"soccer.team.goals_difference\", \"soccer.team.last5_game_results\", \"soccer.team.losses\", \"soccer.team.name\", \"soccer.team.points\", \"soccer.team.points_per_game\", \"soccer.team.wins\", \"soocer.player.name\", \"state\", \"timestamp\", \"url\", \"year\", \"zip\"]\nProvide just the column types as a JSON list without any introduction or explanation."
    },
    {
        "role": "user",
        "content": "table name: nhl_season_player_stats_2016\nRk,Player,Age,Tm,Pos,GP,G,A,PTS,EV,PP,PP.1,S,S%,TOI,ATOI,BLK,HIT,FOW,FO%\n641,Emile Poirier,21,CGY,LW,2,0,0,0,0,0,0,3,0.0,28,13:54,1,4,0,\n566,Chris Neil,36,OTT,RW,80,5,8,13,5,0,0,70,7.1,744,9:18,12,215,1,50.0\n448,Adam Larsson,23,NJD,D,82,3,15,18,3,0,0,65,4.6,1846,22:31,148,163,0,\n"
    },
    {
        "role": "assistant",
        "content": "[\"rank\", \"hockey.player.name\", \"hockey.player.age\", \"hockey.team.name\", \"hockey.player.position\", \"hockey.player.games_played\", \"hockey.player.goals\", \"hockey.player.assists\", \"hockey.player.points\", \"hockey.player.event_strength_goals\", \"hockey.player.power_play_goals\", \"hockey.player.power_play_assists\", \"hockey.player.short_on_goals\", \"hockey.player.shooting_percentage\", \"hockey.player.time_on_ice\", \"hockey.player.average_time_on_ice\", \"hockey.player.blocks\", \"hockey.player.hits\", \"hockey.player.faceoff_wins\", \"hockey.player.faceoff_percentage\"]"
    },
    {
        "role": "user",
        "content": "table name: nfl_season_player_scrimmage_stats_1997\nRk,Player,Tm,Age,Pos,G,GS,Tgt,Rec,Yds,Y/R,TD,1D,Lng,R/G,Y/G,Ctch%,Y/Tgt,Att,Yds.1,TD.1,1D.1,Lng.1,Y/A,Y/G.1,A/G,Touch,Y/Tch,YScm,RRTD,Fmb\n297,Derek Brown,JAX,27,TE,13,8,11.0,8,84,10.5,1,4,21,0.6,6.5,72.7%,7.6,,,,0,,,,,8,10.5,84,1,0\n198,Brian Stablein,IND,27,WR,16,0,31.0,25,253,10.1,1,13,30,1.6,15.8,80.6%,8.2,,,,0,,,,,25,10.1,253,1,0\n402,Deems May,SEA,28,TE,16,0,5.0,2,21,10.5,0,2,11,0.1,1.3,40.0%,4.2,,,,0,,,,,2,10.5,21,0,0\n"
    }
]
```

Example response by GPT-4o (with table and column names):

```
"message": {
    "role": "assistant",
    "content": "[\"rank\", \"football.player.name\", \"football.team.name\", \"football.player.age\", \"football.player.position\", \"football.player.games_played\", \"football.player.games_started\", \"football.player.pass_targets\", \"football.player.receptions\", \"football.player.receiving_yards\", \"football.player.receiving_yards_per_reception\", \"football.player.receiving_touchdowns\", \"football.player.first_down_receiving\", \"football.player.longest_reception\", \"football.player.reception_per_game\", \"football.player.receiving_yards_per_game\", \"football.player.catch_percentage\", \"football.player.receiving_yards_per_target\", \"football.player.rushing_attempted\", \"football.player.rushing_yards\", \"football.player.rushing_touchdowns\", \"football.player.first_down_rushing\", \"football.player.longest_rush_yards\", \"football.player.yards_per_rush_attempt\", \"football.player.rushing_yards_per_game\", \"football.player.rushing_attempted_per_game\", \"football.player.touches\", \"football.player.scrimmage_yards_per_touch\", \"football.player.scrimmage_yards\", \"football.player.scrimmage_touchdowns\", \"football.player.fumbles\"]",
    "refusal": null
}
```

Example prompt (without table and column names):

```
"messages": [
    {
        "role": "user",
        "content": "Predict the column types of the following tables. \nUse only column types this list: [\"address\", \"baseball.experience_years\", \"baseball.manager.all_star_games_managed\", \"baseball.manager.championship_wins\", \"baseball.manager.ejections\", \"baseball.manager.games_managed\", \"baseball.manager.games_over_.5\", \"baseball.manager.name\", \"baseball.manager.playoff_appearances\", \"baseball.manager.playoff_total_losses\", \"baseball.manager.playoff_total_wins\", \"baseball.manager.playoff_win_loss_percentage\", \"baseball.manager.teams_avg_finish\", \"baseball.manager.teams_best_finish\", \"baseball.manager.teams_worst_finish\", \"baseball.manager.total_championship_wins\", \"baseball.manager.total_losses\", \"baseball.manager.total_ties\", \"baseball.manager.total_wins\", \"baseball.manager.win_loss_percentage\", \"baseball.player.age\", \"baseball.player.batting_side\", \"baseball.player.height\", \"baseball.player.name\", \"baseball.player.position\", \"baseball.player.throwing_hand\", \"baseball.player.weight\", \"baseball.player.wins_above_replacement\", \"baseball.team.at_bats\", \"baseball.team.average_age\", \"baseball.team.balks\", \"baseball.team.bases_on_balls\", \"baseball.team.batters_faced\", \"baseball.team.bb9\", \"baseball.team.cauught_stealing\", \"baseball.team.complete_game\", \"baseball.team.doubles\", \"baseball.team.earned_runs\", \"baseball.team.era\", \"baseball.team.era+\", \"baseball.team.fip\", \"baseball.team.games_behind\", \"baseball.team.games_finished\", \"baseball.team.games_over_.5\", \"baseball.team.games_played\", \"baseball.team.games_started\", \"baseball.team.grounded_double_plays\", \"baseball.team.h9\", \"baseball.team.hit_by_pitch\", \"baseball.team.hits\", \"baseball.team.home_runs\", \"baseball.team.hr9\", \"baseball.team.innings_pitched\", \"baseball.team.intentional_bases_on_balls\", \"baseball.team.losses\", \"baseball.team.name\", \"baseball.team.number_of_hall_of_famers\", \"baseball.team.number_of_players\", \"baseball.team.obp\", \"baseball.team.ops\", \"baseball.team.ops+\", \"baseball.team.plate_appearances\", \"baseball.team.playoffs_participations\", \"baseball.team.runners_left_on_base\", \"baseball.team.runs\", \"baseball.team.runs_allowed_per_game\", \"baseball.team.runs_batted_in\", \"baseball.team.runs_scored_per_game\", \"baseball.team.sacrifice_flies\", \"baseball.team.sacrifice_hits\", \"baseball.team.saves\", \"baseball.team.shutouts\", \"baseball.team.shutouts_by_team\", \"baseball.team.slg\", \"baseball.team.so/w\", \"baseball.team.so9\", \"baseball.team.stolen_bases\", \"baseball.team.strikeouts\", \"baseball.team.total_at_bats\", \"baseball.team.total_ba\", \"baseball.team.total_bases\", \"baseball.team.total_championship_wins\", \"baseball.team.total_division_wins\", \"baseball.team.total_games_played\", \"baseball.team.total_hits\", \"baseball.team.total_home_runs\", \"baseball.team.total_losses\", \"baseball.team.total_number_of_players\", \"baseball.team.total_runs\", \"baseball.team.total_runs_allowed\", \"baseball.team.total_wins\", \"baseball.team.triples\", \"baseball.team.whip\", \"baseball.team.wild_pitches\", \"baseball.team.win_loss_percentage\", \"baseball.team.wins\", \"basketball.coach.franchise_games_coached\", \"basketball.coach.franchise_losses\", \"basketball.coach.franchise_sesaons\", \"basketball.coach.franchise_wins\", \"basketball.coach.name\", \"basketball.coach.playoff_franchise_games_coached\", \"basketball.coach.playoff_franchise_losses\", \"basketball.coach.playoff_franchise_wins\", \"basketball.coach.playoff_total_games_coached\", \"basketball.coach.playoff_total_losses\", \"basketball.coach.playoff_total_wins\", \"basketball.coach.playoffs_games_coached\", \"basketball.coach.playoffs_losses\", \"basketball.coach.playoffs_wins\", \"basketball.coach.season_games_coached\", \"basketball.coach.season_losses\", \"basketball.coach.season_wins\", \"basketball.coach.total_games_coached\", \"basketball.coach.total_losses\", \"basketball.coach.total_seasons\", \"basketball.coach.total_wins\", \"basketball.coach.total_wins_percentage\", \"basketball.player.2-point_field_goals_attempts_per_game\", \"basketball.player.2-point_field_goals_per_game\", \"basketball.player.2-point_field_goals_percentage\", \"basketball.player.3-point_field_goals_attempts_per_game\", \"basketball.player.3-point_field_goals_per_game\", \"basketball.player.3-point_field_goals_percentage\", \"basketball.player.age\", \"basketball.player.assists_per_game\", \"basketball.player.blocks_per_game\", \"basketball.player.defensive_rebounds_per_game\", \"basketball.player.effective_field_goals_percentage\", \"basketball.player.field_goals_attempts_per_game\", \"basketball.player.field_goals_per_game\", \"basketball.player.field_goals_percentage\", \"basketball.player.fouls_per_game\", \"basketball.player.free_throws_per_game\", \"basketball.player.free_throws_percentage\", \"basketball.player.games_played\", \"basketball.player.games_started\", \"basketball.player.minutes_per_game\", \"basketball.player.name\", \"basketball.player.offensive_rebounds_per_game\", \"basketball.player.points_per_game\", \"basketball.player.position\", \"basketball.player.rebounds_per_game\", \"basketball.player.steals_per_game\", \"basketball.player.three_throw_attempts_per_game\", \"basketball.player.turnovers_per_game\", \"basketball.team.2-point_field_goals_attempts_per_game\", \"basketball.team.2-point_field_goals_per_game\", \"basketball.team.2-point_field_goals_percentage\", \"basketball.team.3-point_field_goals_attempts_per_game\", \"basketball.team.3-point_field_goals_per_game\", \"basketball.team.3-point_field_goals_percentage\", \"basketball.team.assists_per_game\", \"basketball.team.blocks_per_game\", \"basketball.team.defensive_rebounds_per_game\", \"basketball.team.field_goals_attempts_per_game\", \"basketball.team.field_goals_per_game\", \"basketball.team.field_goals_percentage\", \"basketball.team.fouls_per_game\", \"basketball.team.free_throws_per_game\", \"basketball.team.free_throws_percentage\", \"basketball.team.games_behind\", \"basketball.team.games_played\", \"basketball.team.losses\", \"basketball.team.minutes_per_game\", \"basketball.team.name\", \"basketball.team.offensive_rebounds_per_game\", \"basketball.team.points_opponent_per_game\", \"basketball.team.points_per_game\", \"basketball.team.rebounds_per_game\", \"basketball.team.simple_rating_system\", \"basketball.team.steals_per_game\", \"basketball.team.three_throw_attempts_per_game\", \"basketball.team.turnovers_per_game\", \"basketball.team.win_loss_percentage\", \"basketball.team.wins\", \"birthdate\", \"city\", \"country\", \"football.coach.name\", \"football.player.adj_net_yards_per_pass_attempt\", \"football.player.adj_yards_per_pass_attempt\", \"football.player.age\", \"football.player.catch_percentage\", \"football.player.comebacks_led\", \"football.player.first_down_passings\", \"football.player.first_down_receiving\", \"football.player.first_down_rushing\", \"football.player.fumbles\", \"football.player.fumbles_forced\", \"football.player.fumbles_recovered\", \"football.player.fumbles_recovered_touchdowns\", \"football.player.fumbles_recovered_yards\", \"football.player.game_winning_drives\", \"football.player.games_played\", \"football.player.games_started\", \"football.player.gets_sacked\", \"football.player.gets_sacked_percentage\", \"football.player.interception_percentage\", \"football.player.interception_touchdowns\", \"football.player.interception_yards\", \"football.player.interception_yards_longest\", \"football.player.interceptions\", \"football.player.interceptions_thrown\", \"football.player.longest_pass_yards\", \"football.player.longest_reception\", \"football.player.longest_rush_yards\", \"football.player.name\", \"football.player.net_yards_per_pass_attempt\", \"football.player.pass_targets\", \"football.player.passes_attempted\", \"football.player.passes_completed\", \"football.player.passes_completed_percentage\", \"football.player.passes_defended\", \"football.player.passing_touchdowns\", \"football.player.passing_touchdowns_percentage\", \"football.player.passing_yards\", \"football.player.passing_yards_per_game\", \"football.player.position\", \"football.player.qb_rating\", \"football.player.qb_rating_old\", \"football.player.qb_record\", \"football.player.receiving_touchdowns\", \"football.player.receiving_yards\", \"football.player.receiving_yards_per_game\", \"football.player.receiving_yards_per_reception\", \"football.player.receiving_yards_per_target\", \"football.player.reception_per_game\", \"football.player.receptions\", \"football.player.rushing_attempted\", \"football.player.rushing_attempted_per_game\", \"football.player.rushing_touchdowns\", \"football.player.rushing_yards\", \"football.player.rushing_yards_per_game\", \"football.player.sacks\", \"football.player.scrimmage_touchdowns\", \"football.player.scrimmage_yards\", \"football.player.scrimmage_yards_per_touch\", \"football.player.tackles_assists\", \"football.player.tackles_combined\", \"football.player.tackles_for_loss\", \"football.player.tackles_qb_hits\", \"football.player.tackles_safeties\", \"football.player.tackles_solo\", \"football.player.touches\", \"football.player.yards_lost_due_to_sack\", \"football.player.yards_per_pass_attempt\", \"football.player.yards_per_pass_completion\", \"football.player.yards_per_rush_attempt\", \"football.stadium.games_played\", \"football.stadium.name\", \"football.team.championship_wins\", \"football.team.conference_championship_wins\", \"football.team.defensive_srs\", \"football.team.division_championship_wins\", \"football.team.expected_points_by_defense\", \"football.team.first_down\", \"football.team.first_down_passings\", \"football.team.first_down_penalties\", \"football.team.first_down_rushing\", \"football.team.fumbles_lost\", \"football.team.games_played\", \"football.team.interceptions_thrown\", \"football.team.losses\", \"football.team.margin_of_victory\", \"football.team.name\", \"football.team.net_yards_per_pass_attempt\", \"football.team.offensive_plays\", \"football.team.offensive_srs\", \"football.team.passes_attempted\", \"football.team.passes_completed\", \"football.team.passing_touchdowns\", \"football.team.passing_yards\", \"football.team.penalties\", \"football.team.penalty_yards\", \"football.team.playoffs_participations\", \"football.team.playoffs_total_losses\", \"football.team.playoffs_total_wins\", \"football.team.playoffs_win_loss_percentage\", \"football.team.points_diff\", \"football.team.points_opponent\", \"football.team.points_scored\", \"football.team.rushing_attempted\", \"football.team.rushing_touchdowns\", \"football.team.rushing_yards\", \"football.team.scoring_drives_percentage\", \"football.team.simple_rating_system\", \"football.team.strength_of_schedule\", \"football.team.super_bowl_wins\", \"football.team.takeaways\", \"football.team.ties\", \"football.team.total_losses\", \"football.team.total_ties\", \"football.team.total_wins\", \"football.team.turnover_drives_percentage\", \"football.team.win_loss_percentage\", \"football.team.wins\", \"football.team.yards\", \"football.team.yards_per_play\", \"football.team.yards_per_rush_attempt\", \"hockey.league\", \"hockey.player.active_status\", \"hockey.player.age\", \"hockey.player.assists\", \"hockey.player.average_time_on_ice\", \"hockey.player.blocks\", \"hockey.player.catches\", \"hockey.player.event_strength_assists\", \"hockey.player.event_strength_goals\", \"hockey.player.faceoff_losses\", \"hockey.player.faceoff_percentage\", \"hockey.player.faceoff_wins\", \"hockey.player.first_name\", \"hockey.player.ga_percentage\", \"hockey.player.game_winning_goals\", \"hockey.player.games_played\", \"hockey.player.games_started\", \"hockey.player.goalie_point_shares\", \"hockey.player.goals\", \"hockey.player.goals_against\", \"hockey.player.goals_against_average\", \"hockey.player.goals_saved_above_average\", \"hockey.player.height\", \"hockey.player.hits\", \"hockey.player.id\", \"hockey.player.jersey_number\", \"hockey.player.last_name\", \"hockey.player.losses\", \"hockey.player.minutes\", \"hockey.player.name\", \"hockey.player.penaltie_minutes\", \"hockey.player.plus_minus\", \"hockey.player.point_shares\", \"hockey.player.points\", \"hockey.player.position\", \"hockey.player.power_play_assists\", \"hockey.player.power_play_goals\", \"hockey.player.quality_starts\", \"hockey.player.quality_starts_percentage\", \"hockey.player.really_bad_starts\", \"hockey.player.save_percentage\", \"hockey.player.saves\", \"hockey.player.shooting_percentage\", \"hockey.player.shoots\", \"hockey.player.short_handed_assists\", \"hockey.player.short_handed_goals\", \"hockey.player.short_on_goals\", \"hockey.player.shots_against\", \"hockey.player.shutouts\", \"hockey.player.ties_plus_overtime_losses\", \"hockey.player.time_on_ice\", \"hockey.player.weight\", \"hockey.player.wins\", \"hockey.stadium.active\", \"hockey.stadium.capacity\", \"hockey.stadium.id\", \"hockey.stadium.name\", \"hockey.team.championship_wins\", \"hockey.team.games_played\", \"hockey.team.goals_against\", \"hockey.team.goals_for\", \"hockey.team.id\", \"hockey.team.losses\", \"hockey.team.name\", \"hockey.team.overtime_losses\", \"hockey.team.playoff_appearances\", \"hockey.team.playoff_games_played\", \"hockey.team.playoff_goal_diff\", \"hockey.team.playoff_goals\", \"hockey.team.playoff_goals_against\", \"hockey.team.playoff_losses\", \"hockey.team.playoff_overtime_losses\", \"hockey.team.playoff_overtime_wins\", \"hockey.team.playoff_ties\", \"hockey.team.playoff_wins\", \"hockey.team.points\", \"hockey.team.points_percentage\", \"hockey.team.r_points_percentage\", \"hockey.team.regulation_time_record\", \"hockey.team.rg_points_percentage\", \"hockey.team.simple_rating_system\", \"hockey.team.stanley_cup_wins\", \"hockey.team.strength_of_schedule\", \"hockey.team.ties\", \"hockey.team.total_division_wins\", \"hockey.team.total_games_played\", \"hockey.team.total_losses\", \"hockey.team.total_overtime_losses\", \"hockey.team.total_playoff_conference_wins\", \"hockey.team.total_points\", \"hockey.team.total_seasons\", \"hockey.team.total_ties\", \"hockey.team.total_wins\", \"hockey.team.win_loss_percentage\", \"hockey.team.wins\", \"hockey.team.wins_in_regulation\", \"latitude\", \"longitude\", \"note\", \"notes\", \"rank\", \"school\", \"soccer.attendance_per_game\", \"soccer.player.90s\", \"soccer.player.age\", \"soccer.player.assists\", \"soccer.player.assists_per_90_min\", \"soccer.player.expected_assists\", \"soccer.player.expected_assists_per_90_min\", \"soccer.player.expected_goals\", \"soccer.player.expected_goals_+assists_per_90_min\", \"soccer.player.expected_goals_per_90_min\", \"soccer.player.expected_non_penalty_goals\", \"soccer.player.expected_non_penalty_goals_+assists\", \"soccer.player.expected_non_penalty_goals_+assists_per_90_min\", \"soccer.player.expected_non_penalty_goals_per_90_min\", \"soccer.player.games_played\", \"soccer.player.games_started\", \"soccer.player.goals\", \"soccer.player.goals_+assists_-penalties_per_90_min\", \"soccer.player.goals_+assists_per_90_min\", \"soccer.player.goals_per_90_min\", \"soccer.player.matches\", \"soccer.player.minutes_played\", \"soccer.player.name\", \"soccer.player.non_penalty_goals\", \"soccer.player.non_penalty_goals_per_90_min\", \"soccer.player.penalties_attemted\", \"soccer.player.penalty_kicks_made\", \"soccer.player.position\", \"soccer.player.red_cards\", \"soccer.player.yellow_cards\", \"soccer.team.draws\", \"soccer.team.expected_goals\", \"soccer.team.expected_goals_allowed\", \"soccer.team.expected_goals_difference\", \"soccer.team.expected_goals_difference_per_90_min\", \"soccer.team.games_played\", \"soccer.team.goals\", \"soccer.team.goals_difference\", \"soccer.team.last5_game_results\", \"soccer.team.losses\", \"soccer.team.name\", \"soccer.team.points\", \"soccer.team.points_per_game\", \"soccer.team.wins\", \"soocer.player.name\", \"state\", \"timestamp\", \"url\", \"year\", \"zip\"]\nProvide just the column types as a JSON list without any introduction or explanation."
    },
    {
        "role": "user",
        "content": "641,Emile Poirier,21,CGY,LW,2,0,0,0,0,0,0,3,0.0,28,13:54,1,4,0,\n566,Chris Neil,36,OTT,RW,80,5,8,13,5,0,0,70,7.1,744,9:18,12,215,1,50.0\n448,Adam Larsson,23,NJD,D,82,3,15,18,3,0,0,65,4.6,1846,22:31,148,163,0,\n"
    },
    {
        "role": "assistant",
        "content": "[\"rank\", \"hockey.player.name\", \"hockey.player.age\", \"hockey.team.name\", \"hockey.player.position\", \"hockey.player.games_played\", \"hockey.player.goals\", \"hockey.player.assists\", \"hockey.player.points\", \"hockey.player.event_strength_goals\", \"hockey.player.power_play_goals\", \"hockey.player.power_play_assists\", \"hockey.player.short_on_goals\", \"hockey.player.shooting_percentage\", \"hockey.player.time_on_ice\", \"hockey.player.average_time_on_ice\", \"hockey.player.blocks\", \"hockey.player.hits\", \"hockey.player.faceoff_wins\", \"hockey.player.faceoff_percentage\"]"
    },
    {
        "role": "user",
        "content": "297,Derek Brown,JAX,27,TE,13,8,11.0,8,84,10.5,1,4,21,0.6,6.5,72.7%,7.6,,,,0,,,,,8,10.5,84,1,0\n198,Brian Stablein,IND,27,WR,16,0,31.0,25,253,10.1,1,13,30,1.6,15.8,80.6%,8.2,,,,0,,,,,25,10.1,253,1,0\n402,Deems May,SEA,28,TE,16,0,5.0,2,21,10.5,0,2,11,0.1,1.3,40.0%,4.2,,,,0,,,,,2,10.5,21,0,0\n"
    }
]
```

Example response by GPT-4o (without table and column names):

```
"message": {
    "role": "assistant",
    "content": "[\"rank\", \"football.player.name\", \"football.team.name\", \"football.player.age\", \"football.player.position\", \"football.player.games_played\", \"football.player.games_started\", \"football.player.receptions\", \"football.player.receiving_yards\", \"football.player.receiving_yards_per_reception\", \"football.player.receiving_touchdowns\", \"football.player.first_down_receiving\", \"football.player.longest_reception\", \"football.player.reception_per_game\", \"football.player.receiving_yards_per_game\", \"football.player.passes_completed_percentage\", \"football.player.yards_per_pass_attempt\", \"football.player.interceptions\", \"football.player.interception_percentage\", \"football.player.passing_touchdowns\", \"football.player.passing_touchdowns_percentage\", \"football.player.passing_yards\", \"football.player.passing_yards_per_game\", \"football.player.passes_attempted\", \"football.player.passes_completed\", \"football.player.receiving_yards_per_reception\", \"football.player.receiving_yards\", \"football.player.receiving_touchdowns\", \"football.player.interceptions_thrown\"]",
    "refusal": null
}
```

## The Task Challenge - Case Study 1

### Exp. 4 - 5: Increasing task complexity & Data errors amplify task complexity

Prompt template:

```
prompt_chat_template:
  - role: "user"
    content: |-
      Do the two table entries refer to the same real-world entity?
      Answer with "Yes" if they do and with "No" if they do not.
  - "{{examples}}"
  - role: "user"
    content: "First entry: {{first_table_row}} Second entry: {{second_table_row}}"

example_chat_template:
  - role: "user"
    content: "First entry: {{first_table_row}} Second entry: {{second_table_row}}"
  - role: "assistant"
    content: "{{ground_truth}}"
```

Example prompt (single table case):

```
"messages": [
    {
        "role": "user",
        "content": "Do the two table entries refer to the same real-world entity?\nAnswer with \"Yes\" if they do and with \"No\" if they do not."
    },
    {
        "role": "user",
        "content": "First entry: MANDT,BURKS,GJAHR,BELNR,BZUEI,ZUONR,VBELN,KUNNR,NAME1,WAERS,WRBTR,BLDAT,ZFBDT\n1,1000,2017,1000022653,1,INV100000000003764,1341323118,BJJ3724086,Jansen & S\u00f6hne AG,USD,115369.64,20170408,20170502\n 
        
        Second entry: PARTN,AVKON,SGTXT,KWBTR,KWAER,BVDAT\nJansen & S\u00f6hne AG,PA83STXY78554166587819,#RECEIPT: INV1000 00000003764 134132318 qkgck9n9uoy,90742.41,USD,20170503\n"
    },
    {
        "role": "assistant",
        "content": "Yes"
    },
    {
        "role": "user",
        "content": "First entry: MANDT,BURKS,GJAHR,BELNR,BZUEI,ZUONR,VBELN,KUNNR,NAME1,WAERS,WRBTR,BLDAT,ZFBDT\n1,1000,2005,1000014729,1,INV100000000000121,1431343122,ABW8381959,Red Maple Ventures,CHF,58454.75,20050407,20050419\n 
        
        Second entry: PARTN,AVKON,SGTXT,KWBTR,KWAER,BVDAT\nJansen & S\u00f6hne AG,PA83STXY78554166587819,#RECEIPT: INV100000000011196  qi8x5op,122771.51,USD,20170223\n"
    },
    {
        "role": "assistant",
        "content": "No"
    },
    {
        "role": "user",
        "content": "First entry: MANDT,BURKS,GJAHR,BELNR,BZUEI,ZUONR,VBELN,KUNNR,NAME1,WAERS,WRBTR,BLDAT,ZFBDT\n1,2000,2008,1000008846,1,INV100000000003993,7988989712,NIL0050239,Galaxy IT Services,USD,237066.71,20080728,20080826\n 
        
        Second entry: PARTN,AVKON,SGTXT,KWBTR,KWAER,BVDAT\nRMV CAPITAL,CH66SOMV52927007000516,PAY + 8777790490 | + 573713149 ,235818.28,CHF,20061222\n"
    }
]
```

Example response by GPT-4o (single table case):

```
"message": {
    "role": "assistant",
    "content": "No",
    "refusal": null
},
```

Example prompt (multiple tables case):

```
"messages": [
    {
        "role": "user",
        "content": "Do the two table entries refer to the same real-world entity?\nAnswer with \"Yes\" if they do and with \"No\" if they do not."
    },
    {
        "role": "user",
        "content": "First entry: MANDT,BURKS,GJAHR,BELNR,BZUEI,ZUONR,VBELN,KUNNR,WRBTR,ZFBDT,ZTERM\n1,2000,2008,1000008846,1,INV100000000003993,7988989712,NIL0050239,237066.71,20080826,14\n   
        
        MANDT,KUNNR,NAME1\n1,NIL0050239,Galaxy IT Services\n1,EUK6855461,Schmidt & Sons Handels\n1,NKE7676369,Rapid Response Couriers\n1,QPM5420052,NorthStar Enterprises\n1,IXM2450446,Fairview Insurance Brokers\n1,KBL4555563,Ramirez & Hijos Consultor\u00eda\n1,BJJ3724086,Jansen & S\u00f6hne AG\n1,GVX1854657,Garc\u00eda & Asociados S.A.\n1,QKY5219436,Nexus Financial Services\n1,ABW8381959,Red Maple Ventures\n   MANDT,BURKS,GJAHR,BELNR,WAERS,BLDAT\n1,2000,2008,1000008846,USD,20080728\n 
        
        Second entry: PARTN,AVKON,SGTXT,KWBTR,KWAER,BVDAT\nJansen & S\u00f6hne AG,PA83STXY78554166587819,#RECEIPT: INV1000 00000003764 134132318 qkgck9n9uoy,90742.41,USD,20170503\n"
    },
    {
        "role": "assistant",
        "content": "Yes"
    },
    {
        "role": "user",
        "content": "First entry: MANDT,BURKS,GJAHR,BELNR,BZUEI,ZUONR,VBELN,KUNNR,WRBTR,ZFBDT,ZTERM\n1,2000,2008,1000008846,1,INV100000000003993,7988989712,NIL0050239,237066.71,20080826,14\n   
        
        MANDT,KUNNR,NAME1\n1,NIL0050239,Galaxy IT Services\n1,EUK6855461,Schmidt & Sons Handels\n1,NKE7676369,Rapid Response Couriers\n1,QPM5420052,NorthStar Enterprises\n1,IXM2450446,Fairview Insurance Brokers\n1,KBL4555563,Ramirez & Hijos Consultor\u00eda\n1,BJJ3724086,Jansen & S\u00f6hne AG\n1,GVX1854657,Garc\u00eda & Asociados S.A.\n1,QKY5219436,Nexus Financial Services\n1,ABW8381959,Red Maple Ventures\n   
        
        MANDT,BURKS,GJAHR,BELNR,WAERS,BLDAT\n1,2000,2008,1000008846,USD,20080728\n Second entry: PARTN,AVKON,SGTXT,KWBTR,KWAER,BVDAT\nJansen & S\u00f6hne AG,PA83STXY78554166587819,#RECEIPT: INV100000000011196  qi8x5op,122771.51,USD,20170223\n"
    },
    {
        "role": "assistant",
        "content": "No"
    },
    {
        "role": "user",
        "content": "First entry: MANDT,BURKS,GJAHR,BELNR,BZUEI,ZUONR,VBELN,KUNNR,WRBTR,ZFBDT,ZTERM\n1,2000,2008,1000008846,1,INV100000000003993,7988989712,NIL0050239,237066.71,20080826,14\n   
        
        MANDT,KUNNR,NAME1\n1,NIL0050239,Galaxy IT Services\n1,EUK6855461,Schmidt & Sons Handels\n1,NKE7676369,Rapid Response Couriers\n1,QPM5420052,NorthStar Enterprises\n1,IXM2450446,Fairview Insurance Brokers\n1,KBL4555563,Ramirez & Hijos Consultor\u00eda\n1,BJJ3724086,Jansen & S\u00f6hne AG\n1,GVX1854657,Garc\u00eda & Asociados S.A.\n1,QKY5219436,Nexus Financial Services\n1,ABW8381959,Red Maple Ventures\n   
        
        MANDT,BURKS,GJAHR,BELNR,WAERS,BLDAT\n1,2000,2008,1000008846,USD,20080728\n Second entry: PARTN,AVKON,SGTXT,KWBTR,KWAER,BVDAT\nRMV CAPITAL,CH66SOMV52927007000516,PAY + 8777790490 | + 573713149 ,235818.28,CHF,20061222\n"
    }
]
```

Example response by GPT-4o (multiple tables case):

```
"message": {
    "role": "assistant",
    "content": "No",
    "refusal": null
}
```

## The Task Challenge - Case Study 2

### Exp. Error propagation in compound tasks

#### Step 1: Schema matching

Prompt template:

```
prompt_chat_template:
  - role: "user"
    content: |-
      Imagine that data should be integrated from a customer table from one database into the customer table of another company.
      Here are three rows from Company A's table: {{company_A_table}}
      And here three rows from Company B's table: {{company_B_table}}
      Please answer with yes or no (without any explanations), whether the information (or part of it) in the column of company B corresponds to information in the column of company A:

  - role: "user"
    content: "Company A column: {{company_A_column}} Company B column: {{company_B_column}}"
```

Example prompt:

```
"messages": [
    {
        "role": "user",
        "content": "Imagine that data should be integrated from a customer table from one database into the customer table of another company.
        
        \nHere are three rows from Company A's table: \nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;3195140297;BR;InovaMed Health Devices;P\u00e1tio Gomes, 5;Alves;54268896;+55 22996640;support@inovamedhealth.com.br;PT;20140514;20140806;BRL;;D2772878905585\n001;5517357987;BR;InovaMed Devices;Campo Cirino, 15;Rios;09811-569;+55 96804975;support@inovamed.com.br;PT;20111012;20150314;BRL;;Y5672092770783\n001;4542788854;IN;Raj Systems;850 \u092e\u091c\u0942\u092e\u0926\u093e\u0930;\u092a\u093e\u0915\u093e\u0932\u093e;139103;+91 45648858;sales@rajsystems.in;HI;20180624;20220712;INR;;V598-8262-65-507\n\n
        
        And here three rows from Company B's table: \nCustomer ID;Organization Name;Address 1;Email Address;Country Prefix;Contact Number\n0472369297;InovaMed Health Devices;P\u00e1tio Gomes, 5 54268896 Alves, Brazil;support@inovamedhealth.com.br;55;22996640\n1476786912;BlueWave Solutions;56157 Gonzalez Lodge 31342 East Ruthshire, United States;support@bluewavesolutions.com;1;76024680\n3340598564;Zhongtian Titan Construction;\u8346\u95e8\u8857E\u5ea7 935022 \u6ce2\u53bf, China;inquiries@zhongtiantitan.com;86;46510848\n\n
        
        Please answer with yes or no (without any explanations), whether the information (or part of it) in the column of company B corresponds to information in the column of company A:"
    },
    {
        "role": "user",
        "content": "Company A column: NAME1 Company B column: Organization Name"
    }
]
```

Example response by GPT-4o:

```
"message": {
    "role": "assistant",
    "content": "Yes",
    "refusal": null
}
```

#### Step 2: Entity matching

Prompt template:

```
prompt_chat_template:
  - role: "user"
    content: |-
      Your task is to detect duplicates in a customer database. 
      Please answer with yes or no (without any explanations), if the following two rows refer to the same customer (note: the format may differ slightly between the rows).
      First row: {{company_A_row}} Second row: {{company_B_row}}
```

Example prompt:

```
"messages": [
    {
        "role": "user",
        "content": "Your task is to detect duplicates in a customer database. \nPlease answer with yes or no (without any explanations), if the following two rows refer to the same customer (note: the format may differ slightly between the rows).\n
        
        First row: \nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;4990527240;BR;EcoBrasa Biofuels;Jardim Maria Isis Abreu, 64;Macedo;10876376;+55 86016279;contact@ecobrasa.com.br;PT;20081001;20180327;BRL;;2488590918\n 
        
        Second row: \nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n;;Walli-Striebitz-Gasse 8 56417 Tecklenburg, Germany 49 ;AutoMeisterwerke AG;Walli-Striebitz-Gasse 8 56417 Tecklenburg, Germany;Walli-Striebitz-Gasse 8 56417 Tecklenburg, Germany;Walli-Striebitz-Gasse 8 56417 Tecklenburg, Germany;18951173;kontakt@automeisterwerke.de;;2008-04-23;2020-02-15;;;DE644348754\n"
    }
]
```

Example response by GPT-4o:

```
"message": {
    "role": "assistant",
    "content": "No",
    "refusal": null
}
```

#### Step 3: Data integration

**Subtask 1: Identified matching customers must be merged into a single row in the format of company A's data.**

Prompt template:

```
prompt_chat_template_merge:
  - role: "user"
    content: |-
      Two companies have customer data that should be merged and the following two rows of data have been found to refer to the same customer.
      Please merge the two rows into one data point, resolving any conflicts in a sensible way and following the structure of Company A's data.
      Return the resulting output table (header and row) in csv format with ; as the delimiter without any explanation.
      Your output must be parsable by pandas.

  - role: "user"
    content: "Company A data: {{company_A_row}} Company B data: {{company_B_row}}"
```

Example prompt:

```
"messages": [
    {
        "role": "user",
        "content": "Two companies have customer data that should be merged and the following two rows of data have been found to refer to the same customer.\nPlease merge the two rows into one data point, resolving any conflicts in a sensible way and following the structure of Company A's data.\nReturn the resulting output table (header and row) in csv format with ; as the delimiter without any explanation.\nYour output must be parsable by pandas."
    },
    {
        "role": "user",
        "content": "
        Company A data: \nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;8542349752;GB;Brightland Resources;Studio 53 Fiona loaf;South Ameliaport;BD7 9FE;+44 67160902;support@brightlandresources.com;EN;20240829;20240917;GBP;GB650808101;\n 
        
        Company B data: \nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n;;Studio 53 Fiona loaf BD7 9FE South Ameliaport, United Kingdom;Brightland Energy Ltd;Studio 53 Fiona loaf BD7 9FE South Ameliaport, United Kingdom;Studio 53 Fiona loaf BD7 9FE South Ameliaport, United Kingdom;Studio 53 Fiona loaf BD7 9FE South Ameliaport, United Kingdom;44 995932 ;info@brightlandenergy.co.uk;;2024-06-26;2024-10-03;;GB650808101;GB650808101\n"
    }
]
```

Example response by GPT-4o:

```
"message": {
    "role": "assistant",
    "content": "```csv\nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;8542349752;GB;Brightland Resources;Studio 53 Fiona loaf;South Ameliaport;BD7 9FE;+44 67160902;support@brightlandresources.com;EN;20240829;20241003;GBP;GB650808101;GB650808101\n```",
    "refusal": null
}
```

**Subtask 2: Customer entries from company B that do not yet exist in company A must be transformed into the format of
company A's data.**

Prompt template:

```
prompt_chat_template_transform:
  - role: "user"
    content: |-
      The customer data from company B has been roughly brought into the schema of company A. 
      However some of the fields are not yet filled or formatted correctly.
      Please return the row from company B to the format of the data in company A.
      Here are three example rows from company A {{company_A_table}}.
      Set the customer ID to xxx.
      Return the resulting output table (header and row) in csv format with ; as the delimiter without any explanation.
      Your output must be parsable by pandas.
  - role: "user"
    content: "Company B data row: {{company_B_row}}"
```

Example prompt:

```
"messages": [
    {
        "role": "user",
        "content": "The customer data from company B has been roughly brought into the schema of company A. \nHowever some of the fields are not yet filled or formatted correctly.\nPlease return the row from company B to the format of the data in company A.\nHere are three example rows from company A \nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;2876528874;IN;RajTech Solutions Pvt. Ltd.;74 \u092a\u0940\u0924\u093e\u092e\u094d\u092c\u0930 \u0938\u0930\u0915\u093e\u0930;\u0905\u0928\u0928\u094d\u0924\u092a\u0941\u0930;528952;+91 76954302;contact@rajtechsolutions.in;HI;20240224;20240408;INR;;274091487526\n001;5580688674;NL;NovaTerra Real Estate;Mauritsstraat 23;Dalerpeel;4019IF;+31 39543992;info@novaterra.nl;NL;20041230;20160129;EUR;NL015201365B89;\n001;102927005;BR;VivaSabor Foods;N\u00facleo de da Concei\u00e7\u00e3o, 79;Garcia;50739-219;+55 62370460;info@vivasabor.com.br;PT;20030914;20110911;BRL;;F65216695691895\n.\nSet the customer ID to xxx.\nReturn the resulting output table (header and row) in csv format with ; as the delimiter without any explanation.\nYour output must be parsable by pandas."
    },
    {
        "role": "user",
        "content": "Company B data row: \nAccount Group;Role;Contract;Creation Date;Modification Date;TAX Number;Customer ID;Organization Name;Address 1;Email Address;Country Prefix;Contact Number\nretail;0005;1;2022-01-06;2024-01-02;FRFf149497954;2615412710;Ing\u00e9nierie M\u00e9canique;63, boulevard Gaillard 26433 Auger, France;contact@ingenierie-mecanique.fr;33;43283251\n"
    }
]
```

Example response by GPT-4o:

```
"message": {
    "role": "assistant",
    "content": "```csv\nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;xxx;FR;Ing\u00e9nierie M\u00e9canique;63, boulevard Gaillard;Auger;26433;+33 43283251;contact@ingenierie-mecanique.fr;FR;20220106;20240102;EUR;;FRFf149497954\n```",
    "refusal": null
}
```

### Exp. 7 - 8 - End-to-end task formulation & End-to-end scaling

We have used two different prompting strategies: (1) *w/o steps* provides only a textual description with instructions
on how to perform the integration but does not mention how to break down the task and (2) *with steps* explicitly
mentions the neccessary intermediate stpes (schema matching, entity matching, and data integration) in the prompt to
provide a hint towards how to execute them.

Prompt templates:

```
(1) prompt_chat_template_text:
  - role: "user"
    content: |-
      Imagine that you need to merge customer data from two different companies into a unified format.
      Company A has acquired Company B and wants to integrate Company B's customer database into its customer table.
      Each company has its own customer data stored in company specific formats, some customers may only exist in one company, some in both.
      Please merge the Company B's database (two related tables) into Company A's customer table. 
      If a customer did not exist in Company A before, please add it and set the customer number to "xxx". Do not add additional columns to Company A's schema. 
      In addition, please detect duplicates and merge them into a single row, in which case please keep the customer ID set in Company A. 
      Return only the resulting output table from Company A after the integration in csv format with ; as the delimiter.
      Your output must be parsable by pandas. Do not give explanations.

  - role: "user"
    content: "Company A customer table: {{company_A_table}} Company B customer database: {{company_B_info_table}} {{company_B_contact_table}}"

(2) prompt_chat_template_steps:
  - role: "user"
    content: |-
      Imagine that you need to merge customer data from two different companies into a unified format.
      Company A has acquired Company B and wants to integrate Company B's customer database into its customer table.
      Each company has its own customer data stored in company specific formats, some customers may only exist in one company, some in both.
      Please perform the following steps:
      1) Schema Matching: Find out which information from Company B needs to be integrated into which parts of Company A's schema.
      2) Entity Matching: Detect duplicates between the databases of the two companies to find out which customers are present in both.
      3) Data Integration & Transformation: Integrate all the data into the schema from Company A. Do not add additional columns to Company A's schema. Merge all the duplicates found and transform the data where necessary. Please keep the customer ID set in Company A. If a customer did not exist in Company A before, please add it and set the customer number to "xxx". 
      Return only the resulting output table from Company A after the integration in csv format with ; as the delimiter.
      Your output must be parsable by pandas. Do not truncate the output table but make sure to merge all duplicate rows. Do not give explanations.

  - role: "user"
    content: "Company A customer table: {{company_A_table}} Company B customer database: {{company_B_info_table}} {{company_B_contact_table}}"

```

Example prompt for (1) Without Steps:

```
"messages": [
    {
        "role": "user",
        "content": "Imagine that you need to merge customer data from two different companies into a unified format.\nCompany A has acquired Company B and wants to integrate Company B's customer database into its customer table.\nEach company has its own customer data stored in company specific formats, some customers may only exist in one company, some in both.\nPlease merge the Company B's database (two related tables) into Company A's customer table. \nIf a customer did not exist in Company A before, please add it and set the customer number to \"xxx\". Do not add additional columns to Company A's schema. \nIn addition, please detect duplicates and merge them into a single row, in which case please keep the customer ID set in Company A. \nReturn only the resulting output table from Company A after the integration in csv format with ; as the delimiter.\nYour output must be parsable by pandas. Do not give explanations."
    },
    {
        "role": "user",
        "content": "Company A customer table: Customers\nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;5724399976;FR;L'Or\u00e9al Beaut\u00e9 Digitale;360, rue de Lopes;Fontaine-sur-Chauvin;41928;+33 16254076;contact@loreal-beaute.fr;FR;20080620;20140908;EUR;FR1k723454994;\n001;3080499910;CN;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7;\u5f20\u5bb6\u6e2f\u5e02;693349;+86 20427767;info@baodegreentech.com;ZH;20180902;20190909;CNY;;\n001;745480683;CN;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7;\u5b81\u5fb7\u5e02;118334;+86 92250456;inquiries@beixinfuturetech.com;ZH;20200305;20200601;CNY;;\n001;8447755608;NL;FoodVerse Gourmet;Chlo\u00ebweg 2;Oostdijk;1499 XS;+31 1077902;info@foodverse.nl;NL;20100503;20150701;EUR;NL268366047B65;\n001;1643152015;NL;NederWoon Furniture Imports;Jessestraat 445;Zwaagdijk-Oost;5007 BV;+31 29758992;info@nederwoonfurniture.nl;NL;20160505;20170526;EUR;NL530243142B39;\n001;3434478642;FR;L'Or\u00e9al Innovation;40, rue de Pichon;Mar\u00e9chalVille;25787;+33 39507135;contact@loreal-innovation.fr;FR;20200309;20241028;EUR;FR5Q759781415;\n001;6311828430;FR;FinTech Solutions;32, rue de Martins;Saint Augustin;51362;+33 62129426;info@fintech-solutions.fr;FR;20070305;20081223;EUR;FR7Q822816108;\n001;5025147270;US;Pinnacle Digital Media;4276 Anthony Trail;South Kevinland;76437;+1 94175362;contact@pinnacledigital.com;EN;20121008;20170105;USD;;Y417746843\n001;6144048848;FR;Estelle Energie;49, chemin Marie Millet;Lecomte;13139;+33 71304025;info@estelleenergie.fr;FR;20070317;20100206;EUR;FRv4464065832;\n001;931818077;US;Oakridge Industries;8506 Clark Trace;North Dawnshire;59756;+1 98201783;sales@oakridgeindustries.com;EN;20020721;20030612;USD;;536598055\n001;8121688489;BR;EcoBrasa Biofuels;Conjunto Cassiano, 123;Macedo;10876376;+55 71174347;contact@ecobrasa.com.br;PT;20110509;20111029;BRL;;2488590918\n001;1635786830;BR;InovaMed Health Devices;P\u00e1tio Gomes, 5;Alves;54268896;+55 22996640;support@inovamedhealth.com.br;PT;20041010;20141006;BRL;;D2772878905585\n001;6670557974;ES;BioTechMed Innovaci\u00f3n;Paseo de C\u00e1ndida Quintana 6;Lugo;08453;+34 81277124;contacto@biotechmed.com;ES;20181116;20201017;EUR;ES77821903L;\n001;271099098;US;Velocity Tech Services;6819 Reid Hills;South Denisehaven;99463;+1 88636252;contact@velocitytech.com;EN;20031129;20040406;USD;;U8259197473018\n001;6731683305;GB;Brightland Energy Ltd;Studio 53 Fiona loaf;South Ameliaport;BD7 9FE;+44 72120472;info@brightlandenergy.co.uk;EN;20240626;20241003;GBP;GB650808101;\n001;1125173551;DE;NaturHof Bio GmbH;Thanelring 230;Schw\u00e4bisch Gm\u00fcnd;61044;+49 94783972;info@naturhof-bio.de;DE;20220211;20220514;EUR;DE054352161;\n001;8190498295;FR;Al\u00e9a Digital;392, boulevard de Lacroix;Duboisboeuf;12751;+33 10580269;contact@aleadigital.fr;FR;20211128;20231017;EUR;FR8w458136934;\n001;5301050982;FR;B\u00e9n\u00e9fice Sant\u00e9;711, rue Giraud;Klein-la-For\u00eat;65854;+33 60469286;info@beneficesante.fr;FR;20200229;20201031;EUR;FRmv654858755;\n001;1502870589;DE;SmartTech Solutions GmbH;Johannring 88;Suhl;88833;+49 10250170;support@smarttech.de;DE;20141104;20150720;EUR;DE279265910;\n001;8924187109;IN;BrightSphere Technologies Pvt. Ltd.;96/8937 \u0924\u092e\u093e\u0902\u0917;\u0905\u0932\u0940\u0917\u0922;570473;+91 15863492;inquiries@brightspheretechnologies.in;HI;20220819;20231104;INR;;K82-05659-339-6\n001;7808954973;ES;Terra Real Estate;Plaza de Marcelo Melero 9 Puerta 2 ;Girona;40715;+34 441171;ventas@terrare.es;ES;20081223;20200104;EUR;ESf9299226y;\n001;1561953322;US;Redstone Enterprises;132 Hester Burg;Youngborough;01941;+1 32791897;service@redstoneenterprises.com;EN;20180915;20181001;USD;;\n001;1555824610;CN;Jinyang Marine Technologies;\u798f\u5dde\u8defq\u5ea7;\u6210\u5e02;720180;+86 6596814;info@jinyangmarine.com;ZH;20071113;20110613;CNY;;E495-3899-16\n001;3985031712;CN;Beixin TechFront Solutions;\u5357\u660c\u8defe\u5ea7;\u6b66\u6c49\u5e02;393276;+86 65035090;inquiries@beixintechfront.com;ZH;20030201;20030419;CNY;;U80-82-09374\n001;8690038112;GB;Pinewood Financial Services;Flat 75l Phillip spring;New Kimberleyburgh;CW0 8HS;+44 61252485;info@pinewoodfinancial.co.uk;EN;20050211;20171201;GBP;GB140199028309;\n001;866048141;CN;Huanxing Oceanic Solutions;\u5408\u5c71\u8defQ\u5ea7;\u592a\u539f\u53bf;434727;+86 53043256;info@huanxingoceanic.com;ZH;20170806;20220822;CNY;;392-768-76\n001;5444421720;US;BlueWave Solutions;56157 Gonzalez Lodge;East Ruthshire;31342;+1 76024680;support@bluewavesolutions.com;EN;20100205;20171122;USD;;X360-8208-72-7\n001;3439890496;BR;PuraMar Seafood Exports;Recanto Marcela Almeida, 82;Dias do Campo;79246689;+55 73734238;sales@puramarexports.com.br;PT;20120501;20220429;BRL;;K67-7206-07-0893-5\n001;7657972298;ES;Alimentos Naturales S.A.;Avenida Bartolom\u00e9 Perez 14 Apt. 14 ;Huesca;01854;+34 81673175;info@alimentosnaturales.com;ES;20130410;20240110;EUR;ESF9874582Q;\n001;2842286809;CN;Jiangnan Precision Systems;\u9648\u8857w\u5ea7;\u6fb3\u95e8\u5e02;328952;+86 28067490;sales@jiangnanprecisionsys.com;ZH;20200616;20240612;CNY;;2745514264994\n Company B customer database: Customer Information Table\nID;Account Group;Role;Contract;Creation Date;Modification Date;TAX Number\n271099098;retail;0004;1;2023-12-17;2024-04-20;\n9924497969;government;0002;0;2010-06-09;2020-12-25;5499197656\n3252792004;wholesale;0003;0;2013-09-10;2014-06-27;NL268366047B65\n2624970231;government;0002;0;2013-01-25;2020-12-11;Q0965503397\n5004985293;retail;0003;0;2006-09-10;2023-10-24;FR8w458136934\n5587874777;wholesale;0005;1;2006-09-06;2012-11-29;FR20942500405\n0441480286;government;0005;1;2008-12-23;2020-01-04;ESf9299226y\n7707045239;retail;0003;1;2017-10-03;2023-11-04;NL722220170B62\n745480683;retail;0003;0;2005-02-11;2017-12-01;GB140199028309\n1046962354;retail;0004;0;2022-04-19;2022-05-21;392-768-76\n1318460154;retail;0001;0;2023-09-02;2023-09-06;K82-05659-339-6\n3080499910;wholesale;0004;0;2013-04-10;2024-01-10;ESF9874582Q\n9290863593;government;0002;1;2001-05-28;2004-03-04;536598055\n6670557974;government;0002;1;2024-10-01;2024-10-13;03-31-1467-43\n1502870589;wholesale;0003;0;2001-04-19;2022-12-08;ESO02430534\n8501549070;government;0001;0;2019-02-15;2021-07-20;FR6U405616401\n8453988787;wholesale;0001;0;2017-06-14;2020-08-06;NL163763325B19\n2842286809;wholesale;0004;0;2017-02-27;2022-07-15;F6899891960\n6163597512;government;0004;1;2003-09-18;2016-03-25;FR7Q822816108\n2993801491;retail;0004;1;2002-08-17;2023-02-21;FR1k723454994\n8351453627;wholesale;0005;0;2006-04-07;2014-05-22;E495-3899-16\n9852168978;retail;0005;1;2020-06-16;2024-06-12;2745514264994\n9211794067;government;0001;1;2008-09-18;2018-04-24;X360-8208-72-7\n8772412460;wholesale;0003;0;2018-01-27;2021-06-25;Z2279944894762\n3985031712;government;0004;1;2002-06-06;2017-06-29;NL530243142B39\n5457825284;retail;0005;1;2011-04-16;2012-01-07;ES52733472x\n8799288424;retail;0002;1;2020-01-06;2020-08-16;T1862086\n7498075056;wholesale;0005;1;2015-02-26;2015-10-11;Y417746843\n2630759141;retail;0004;1;2019-08-04;2021-11-13;772420468220\n3301346043;retail;0001;0;2021-07-17;2021-12-22;X2327940360\n5487814625;government;0003;1;2022-03-07;2022-04-03;DE054352161\n8605948619;wholesale;0002;1;2024-09-05;2024-09-10;GB650808101\n4638431434;wholesale;0002;1;2002-09-03;2010-09-10;GB284405520\n7157200042;wholesale;0003;0;2018-01-14;2022-09-30;FRmv654858755\n5704365015;retail;0001;0;2003-04-04;2003-04-09;\n6816550619;wholesale;0002;1;2004-03-20;2004-03-28;\n1635786830;wholesale;0002;0;2009-04-19;2010-01-15;FRv4464065832\n8447755608;government;0001;0;2019-09-14;2024-07-18;94410483128\n5351417752;government;0001;0;2021-09-11;2023-12-02;8209733735\n5332313005;government;0003;0;2018-08-02;2019-09-22;56705154\n5444421720;government;0005;0;2024-05-22;2024-10-04;C5817897\n5287466408;retail;0003;0;2021-08-19;2022-02-16;K67-7206-07-0893-5\n4352311683;wholesale;0001;1;2009-02-08;2016-09-21;DE410375625\n2322269914;retail;0002;1;2010-06-24;2015-02-10;ES41880379P\n0518173542;retail;0003;0;2019-05-24;2020-09-23;\n7563136213;retail;0001;0;2022-11-30;2024-10-06;GBGD359\n3434478642;retail;0005;1;2006-10-17;2016-10-18;DE279265910\n1484040534;retail;0004;1;2008-10-01;2018-03-27;2488590918\n1561953322;retail;0001;0;2008-12-09;2009-10-12;M4547761167223\n0901404965;retail;0005;1;2007-11-03;2012-10-02;D2772878905585\n Customer Contact Details Table\nCustomer ID;Organization Name;Address 1;Email Address;Country Prefix;Contact Number\n8605948619;Brightland Energy Ltd;599 French cliff LN2 9SP Lukefurt, United Kingdom;info@brightlandenergy.co.uk;44;72120472\n1561953322;Stellar Web Solutions;09925 Justin Haven 33652 East Ashleychester, United States;contact@stellarwebsolutions.com;1;50637915\n0441480286;Terra Real Estate;Plaza de Marcelo Melero 9 Puerta 2  40715 Girona, Spain;ventas@terrare.es;34;441171\n0901404965;MedBrasa Diagnostics;P\u00e1tio Gomes, 5 54268896 Alves, Brazil;contact@medbrasadiag.com.br;55;22996640\n8501549070;Paragone Consulting;1, rue de Blanchard 39938 Saint Joseph, France;contact@paragoneconsulting.fr;33;10186451\n3301346043;Summit Innovations Inc.;581 Carlos Corners Suite 426 12276 New Jenniferbury, United States;contact@summitinnovations.com;1;62483716\n2842286809;Ironclad Manufacturing Co.;88108 Jamie Circles Apt. 770 41625 New Lisa, United States;sales@ironcladmanufacturing.com;1;51766217\n7707045239;GreenFlow Energy Solutions;Carlijnsteeg 75 3901BZ Best, Netherlands;contact@greenflowenergy.nl;31;24296894\n5287466408;PuraMar Seafood Exports;Recanto Marcela Almeida, 82 79246689 Dias do Campo, Brazil;sales@puramarexports.com.br;55;34118398\n3434478642;SmartTech Solutions GmbH;Biggenallee 185 58769 Feuchtwangen, Germany;support@smarttech.de;49;10250170\n5487814625;BioHof Naturprodukte GmbH;Frank-Fischer-Weg 30 61044 Schw\u00e4bisch Gm\u00fcnd, Germany;service@biohof-natur.de;49;94783972\n5457825284;Construcci\u00f3n de Infraestructuras Sostenibles S.L.;Acceso Ariel Pintor 37 Piso 9  24997 Palencia, Spain;contacto@construccionesostenibles.es;34;99880864\n5704365015;Beixin TechFront Solutions;\u5357\u660c\u8defe\u5ea7 393276 \u6b66\u6c49\u5e02, China;inquiries@beixintechfront.com;86;65035090\n2630759141;SummitTech Global;628 Adam Brooks Apt. 090 47178 Julieside, United States;support@summittechglobal.com;1;1701579\n6163597512;FinTech Solutions;52, chemin de Roy 41118 Barbe, France;info@fintech-solutions.fr;33;62129426\n3080499910;Alimentos Naturales S.A.;Avenida Bartolom\u00e9 Perez 14 Apt. 14  01854 Huesca, Spain;info@alimentosnaturales.com;34;81673175\n2993801491;L'Or\u00e9al Beaut\u00e9 Digitale;2, chemin Guillet 41928 Fontaine-sur-Chauvin, France;contact@loreal-beaute.fr;33;16254076\n9852168978;Jiangnan Precision Systems;\u9648\u8857w\u5ea7 328952 \u6fb3\u95e8\u5e02, China;sales@jiangnanprecisionsys.com;86;28067490\n8799288424;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7 118334 \u5b81\u5fb7\u5e02, China;inquiries@beixinfuturetech.com;86;92250456\n8453988787;BlueWave Environmental Services;Saradreef 87 1380LD Bingelrade, Netherlands;services@bluewave.nl;31;59521901\n7157200042;B\u00e9n\u00e9fice Sant\u00e9;711, rue Giraud 65854 Klein-la-For\u00eat, France;info@beneficesante.fr;33;60469286\n3252792004;DutchGourmet Foods;Chlo\u00ebweg 2 1499 XS Oostdijk, Netherlands;contact@dutchgourmet.nl;31;1077902\n8447755608;Quantum Data Systems;3/1 \u0939\u091c\u093e\u0930\u093f\u0915\u093e 911243 \u0905\u092e\u0930\u093e\u0935\u0924\u0940, India;info@quantumdatasys.in;91;64043374\n3985031712;NederWoon Furniture Imports;Jessestraat 445 5007 BV Zwaagdijk-Oost, Netherlands;info@nederwoonfurniture.nl;31;29758992\n2322269914;Soluciones Digitales Avanzadas S.L.;Glorieta Y\u00e9ssica Arribas 1 09718 Cantabria, Spain;soporte@solucionesda.es;34;73049425\n5351417752;VerdeFlora Outdoor Solutions;Praia Rezende, 5 41531504 Pimenta da Prata, Brazil;contact@verdefloraoutdoor.com.br;55;7914152\n7563136213;Edgewater Systems;Flat 10 Roberts trace G9H 7FP Lake Staceychester, United Kingdom;info@edgewatersystems.co.uk;44;60724661\n9924497969;SkyBridge Logistics;718 Melissa Mountain Suite 599 26893 Lake David, United States;support@skybridgelogistics.com;1;18869006\n271099098;L'Or\u00e9al Innovation;40, rue de Pichon 25787 Mar\u00e9chalVille, France;contact@loreal-innovation.fr;33;18252866\n6816550619;Velocity Tech Services;6819 Reid Hills 99463 South Denisehaven, United States;contact@velocitytech.com;1;88636252\n1484040534;EcoBrasa Biofuels;Jardim Maria Isis Abreu, 64 10876376 Macedo, Brazil;contact@ecobrasa.com.br;55;48921425\n1635786830;Estelle Solutions Vertes;49, chemin Marie Millet 13139 Lecomte, France;info@estellesolutionsvertes.fr;33;71304025\n8351453627;Jinyang Marine Technologies;\u798f\u5dde\u8defq\u5ea7 720180 \u6210\u5e02, China;info@jinyangmarine.com;86;54668854\n745480683;Pinewood Financial Services;Flat 75l Phillip spring CW0 8HS New Kimberleyburgh, United Kingdom;info@pinewoodfinancial.co.uk;44;61252485\n5587874777;Artisanat Luxe Paris;5, rue Becker 36973 Daniel, France;contact@artisanatluxeparis.fr;33;15675279\n7498075056;Pinnacle Digital Media;4276 Anthony Trail 76437 South Kevinland, United States;contact@pinnacledigital.com;1;94175362\n1046962354;Huanxing Oceanic Solutions;\u5408\u5c71\u8defQ\u5ea7 434727 \u592a\u539f\u53bf, China;info@huanxingoceanic.com;86;58068634\n5444421720;Quantum Innovations;93577 Pineda Common Apt. 604 15578 Hunthaven, United States;support@quantuminnovations.com;1;73416298\n9211794067;BlueWave Solutions;56157 Gonzalez Lodge 31342 East Ruthshire, United States;support@bluewavesolutions.com;1;76024680\n9290863593;Oakridge Industries;8506 Clark Trace 59756 North Dawnshire, United States;sales@oakridgeindustries.com;1;98201783\n2624970231;Redstone Enterprises;09987 Dylan Causeway Suite 609 86161 Hughesfort, United States;service@redstoneenterprises.com;1;32791897\n1502870589;Oleo Puro;Acceso Andr\u00e9s Felipe Amaya 83 07652 Teruel, Spain;contacto@oleopuro.com;34;8205521\n4352311683;MediCare Solutions GmbH;\u00c4nne-Kusch-Platz 7 22267 Strasburg, Germany;info@medicare-solutions.de;49;60814703\n4638431434;Bluebird Innovations;Flat 4 Jake village HX48 9YS West Rita, United Kingdom;contact@bluebirdinnovations.co.uk;44;22753890\n1318460154;BrightSphere Technologies Pvt. Ltd.;33 \u0905\u0938\u0940\u092e \u0938\u0930\u0940\u0928 570473 \u0905\u0932\u0940\u0917\u0922, India;inquiries@brightspheretechnologies.in;91;15863492\n8772412460;VerdeFlora Landscaping;Quadra de da Rosa, 89 02349-247 Teixeira de Pimenta, Brazil;contact@verdeflora.com.br;55;67782970\n0518173542;BioTechMed Innovaci\u00f3n;Camino de \u00c1gata Pedrosa 115 31807 Huesca, Spain;ventas@biotechmed.net;34;81277124\n5004985293;Al\u00e9a Digital;392, boulevard de Lacroix 12751 Duboisboeuf, France;contact@aleadigital.fr;33;66929679\n6670557974;ZenHealth Systems Pvt. Ltd.;36/980 \u092a\u091f\u0947\u0932 748944 \u092e\u094b\u0915\u093e\u092e\u093e, India;inquiries@zenhealthsys.in;91;5081300\n5332313005;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7 693349 \u5f20\u5bb6\u6e2f\u5e02, China;info@baodegreentech.com;86;20427767\n"
    }
]
 ```

Example response by GPT-4o for (1) Without Steps:

```
"message": {
    "role": "assistant",
    "content": "MANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;5724399976;FR;L'Or\u00e9al Beaut\u00e9 Digitale;360, rue de Lopes;Fontaine-sur-Chauvin;41928;+33 16254076;contact@loreal-beaute.fr;FR;20080620;20140908;EUR;FR1k723454994;\n001;3080499910;CN;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7;\u5f20\u5bb6\u6e2f\u5e02;693349;+86 20427767;info@baodegreentech.com;ZH;20180902;20190909;CNY;ESF9874582Q;\n001;745480683;CN;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7;\u5b81\u5fb7\u5e02;118334;+86 92250456;inquiries@beixinfuturetech.com;ZH;20200305;20200601;CNY;GB140199028309;\n001;8447755608;NL;FoodVerse Gourmet;Chlo\u00ebweg 2;Oostdijk;1499 XS;+31 1077902;info@foodverse.nl;NL;20100503;20150701;EUR;NL268366047B65;94410483128\n001;1643152015;NL;NederWoon Furniture Imports;Jessestraat 445;Zwaagdijk-Oost;5007 BV;+31 29758992;info@nederwoonfurniture.nl;NL;20160505;20170526;EUR;NL530243142B39;\n001;3434478642;FR;L'Or\u00e9al Innovation;40, rue de Pichon;Mar\u00e9chalVille;25787;+33 39507135;contact@loreal-innovation.fr;FR;20200309;20241028;EUR;FR5Q759781415;\n001;6311828430;FR;FinTech Solutions;32, rue de Martins;Saint Augustin;51362;+33 62129426;info@fintech-solutions.fr;FR;20070305;20081223;EUR;FR7Q822816108;\n001;5025147270;US;Pinnacle Digital Media;4276 Anthony Trail;South Kevinland;76437;+1 94175362;contact@pinnacledigital.com;EN;20121008;20170105;USD;;Y417746843\n001;6144048848;FR;Estelle Energie;49, chemin Marie Millet;Lecomte;13139;+33 71304025;info@estelleenergie.fr;FR;20070317;20100206;EUR;FRv4464065832;\n001;931818077;US;Oakridge Industries;8506 Clark Trace;North Dawnshire;59756;+1 98201783;sales@oakridgeindustries.com;EN;20020721;20030612;USD;;536598055\n001;8121688489;BR;EcoBrasa Biofuels;Conjunto Cassiano, 123;Macedo;10876376;+55 71174347;contact@ecobrasa.com.br;PT;20110509;20111029;BRL;;2488590918\n001;1635786830;BR;InovaMed Health Devices;P\u00e1tio Gomes, 5;Alves;54268896;+55 22996640;support@inovamedhealth.com.br;PT;20041010;20141006;BRL;FRv4464065832;D2772878905585\n001;6670557974;ES;BioTechMed Innovaci\u00f3n;Paseo de C\u00e1ndida Quintana 6;Lugo;08453;+34 81277124;contacto@biotechmed.com;ES;20181116;20201017;EUR;ES77821903L;03-31-1467-43\n001;271099098;US;Velocity Tech Services;6819 Reid Hills;South Denisehaven;99463;+1 88636252;contact@velocitytech.com;EN;20031129;20040406;USD;;U8259197473018\n001;6731683305;GB;Brightland Energy Ltd;Studio 53 Fiona loaf;South Ameliaport;BD7 9FE;+44 72120472;info@brightlandenergy.co.uk;EN;20240626;20241003;GBP;GB650808101;\n001;1125173551;DE;NaturHof Bio GmbH;Thanelring 230;Schw\u00e4bisch Gm\u00fcnd;61044;+49 94783972;info@naturhof-bio.de;DE;20220211;20220514;EUR;DE054352161;\n001;8190498295;FR;Al\u00e9a Digital;392, boulevard de Lacroix;Duboisboeuf;12751;+33 10580269;contact@aleadigital.fr;FR;20211128;20231017;EUR;FR8w458136934;\n001;5301050982;FR;B\u00e9n\u00e9fice Sant\u00e9;711, rue Giraud;Klein-la-For\u00eat;65854;+33 60469286;info@beneficesante.fr;FR;20200229;20201031;EUR;FRmv654858755;\n001;1502870589;DE;SmartTech Solutions GmbH;Johannring 88;Suhl;88833;+49 10250170;support@smarttech.de;DE;20141104;20150720;EUR;DE279265910;\n001;8924187109;IN;BrightSphere Technologies Pvt. Ltd.;96/8937 \u0924\u092e\u093e\u0902\u0917;\u0905\u0932\u0940\u0917\u0922;570473;+91 15863492;inquiries@brightspheretechnologies.in;HI;20220819;20231104;INR;;K82-05659-339-6\n001;7808954973;ES;Terra Real Estate;Plaza de Marcelo Melero 9 Puerta 2 ;Girona;40715;+34 441171;ventas@terrare.es;ES;20081223;20200104;EUR;ESf9299226y;\n001;1561953322;US;Redstone Enterprises;132 Hester Burg;Youngborough;01941;+1 32791897;service@redstoneenterprises.com;EN;20180915;20181001;USD;;M4547761167223\n001;1555824610;CN;Jinyang Marine Technologies;\u798f\u5dde\u8defq\u5ea7;\u6210\u5e02;720180;+86 6596814;info@jinyangmarine.com;ZH;20071113;20110613;CNY;;E495-3899-16\n001;3985031712;CN;Beixin TechFront Solutions;\u5357\u660c\u8defe\u5ea7;\u6b66\u6c49\u5e02;393276;+86 65035090;inquiries@beixintechfront.com;ZH;20030201;20030419;CNY;NL530243142B39;U80-82-09374\n001;8690038112;GB;Pinewood Financial Services;Flat 75l Phillip spring;New Kimberleyburgh;CW0 8HS;+44 61252485;info@pinewoodfinancial.co.uk;EN;20050211;20171201;GBP;GB140199028309;\n001;866048141;CN;Huanxing Oceanic Solutions;\u5408\u5c71\u8defQ\u5ea7;\u592a\u539f\u53bf;434727;+86 53043256;info@huanxingoceanic.com;ZH;20170806;20220822;CNY;;392-768-76\n001;5444421720;US;BlueWave Solutions;56157 Gonzalez Lodge;East Ruthshire;31342;+1 76024680;support@bluewavesolutions.com;EN;20100205;20171122;USD;;X360-8208-72-7\n001;3439890496;BR;PuraMar Seafood Exports;Recanto Marcela Almeida, 82;Dias do Campo;79246689;+55 73734238;sales@puramarexports.com.br;PT;20120501;20220429;BRL;;K67-7206-07-0893-5\n001;7657972298;ES;Alimentos Naturales S.A.;Avenida Bartolom\u00e9 Perez 14 Apt. 14 ;Huesca;01854;+34 81673175;info@alimentosnaturales.com;ES;20130410;20240110;EUR;ESF9874582Q;\n001;2842286809;CN;Jiangnan Precision Systems;\u9648\u8857w\u5ea7;\u6fb3\u95e8\u5e02;328952;+86 28067490;sales@jiangnanprecisionsys.com;ZH;20200616;20240612;CNY;;2745514264994\n001;xxx;US;SkyBridge Logistics;718 Melissa Mountain Suite 599 26893 Lake David, United States;;;+1 18869006;support@skybridgelogistics.com;EN;20100609;20201225;USD;;5499197656\n001;xxx;NL;DutchGourmet Foods;Chlo\u00ebweg 2 1499 XS Oostdijk, Netherlands;;;+31 1077902;contact@dutchgourmet.nl;NL;20130910;20140627;EUR;NL268366047B65;\n001;xxx;US;Redstone Enterprises;09987 Dylan Causeway Suite 609 86161 Hughesfort, United States;;;+1 32791897;service@redstoneenterprises.com;EN;20130125;20201211;USD;;Q0965503397\n001;xxx;FR;Al\u00e9a Digital;392, boulevard de Lacroix 12751 Duboisboeuf, France;;;+33 66929679;contact@aleadigital.fr;FR;20060910;20231024;EUR;FR8w458136934;\n001;xxx;FR;Artisanat Luxe Paris;5, rue Becker 36973 Daniel, France;;;+33 15675279;contact@artisanatluxeparis.fr;FR;20060906;20121129;EUR;FR20942500405;\n001;xxx;ES;Terra Real Estate;Plaza de Marcelo Melero 9 Puerta 2  40715 Girona, Spain;;;+34 441171;ventas@terrare.es;ES;20081223;20200104;EUR;ESf9299226y;\n001;xxx;NL;GreenFlow Energy Solutions;Carlijnsteeg 75 3901BZ Best, Netherlands;;;+31 24296894;contact@greenflowenergy.nl;NL;20171003;20231104;EUR;NL722220170B62;\n001;xxx;CN;Huanxing Oceanic Solutions;\u5408\u5c71\u8defQ\u5ea7 434727 \u592a\u539f\u53bf, China;;;+86 58068634;info@huanxingoceanic.com;ZH;20220419;20220521;CNY;;392-768-76\n001;xxx;IN;BrightSphere Technologies Pvt. Ltd.;33 \u0905\u0938\u0940\u092e \u0938\u0930\u0940\u0928 570473 \u0905\u0932\u0940\u0917\u0922, India;;;+91 15863492;inquiries@brightspheretechnologies.in;HI;20230902;20230906;INR;;K82-05659-339-6\n001;xxx;US;Oakridge Industries;8506 Clark Trace 59756 North Dawnshire, United States;;;+1 98201783;sales@oakridgeindustries.com;EN;20010528;20040304;USD;;536598055\n001;xxx;FR;Paragone Consulting;1, rue de Blanchard 39938 Saint Joseph, France;;;+33 10186451;contact@paragoneconsulting.fr;FR;20190215;20210720;EUR;FR6U405616401;\n001;xxx;NL;BlueWave Environmental Services;Saradreef 87 1380LD Bingelrade, Netherlands;;;+31 59521901;services@bluewave.nl;NL;20170614;20200806;EUR;NL163763325B19;\n001;xxx;FR;FinTech Solutions;52, chemin de Roy 41118 Barbe, France;;;+33 62129426;info@fintech-solutions.fr;FR;20030918;20160325;EUR;FR7Q822816108;\n001;xxx;FR;L'Or\u00e9al Beaut\u00e9 Digitale;2, chemin Guillet 41928 Fontaine-sur-Chauvin, France;;;+33 16254076;contact@loreal-beaute.fr;FR;20020817;20230221;EUR;FR1k723454994;\n001;xxx;CN;Jinyang Marine Technologies;\u798f\u5dde\u8defq\u5ea7 720180 \u6210\u5e02, China;;;+86 54668854;info@jinyangmarine.com;ZH;20060407;20140522;CNY;;E495-3899-16\n001;xxx;CN;Jiangnan Precision Systems;\u9648\u8857w\u5ea7 328952 \u6fb3\u95e8\u5e02, China;;;+86 28067490;sales@jiangnanprecisionsys.com;ZH;20200616;20240612;CNY;;2745514264994\n001;xxx;US;BlueWave Solutions;56157 Gonzalez Lodge 31342 East Ruthshire, United States;;;+1 76024680;support@bluewavesolutions.com;EN;20080918;20180424;USD;;X360-8208-72-7\n001;xxx;BR;VerdeFlora Landscaping;Quadra de da Rosa, 89 02349-247 Teixeira de Pimenta, Brazil;;;+55 67782970;contact@verdeflora.com.br;PT;20180127;20210625;BRL;;Z2279944894762\n001;xxx;ES;Construcci\u00f3n de Infraestructuras Sostenibles S.L.;Acceso Ariel Pintor 37 Piso 9  24997 Palencia, Spain;;;+34 99880864;contacto@construccionesostenibles.es;ES;20110416;20120107;EUR;ES52733472x;\n001;xxx;CN;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7 118334 \u5b81\u5fb7\u5e02, China;;;+86 92250456;inquiries@beixinfuturetech.com;ZH;20200106;20200816;CNY;;T1862086\n001;xxx;US;Pinnacle Digital Media;4276 Anthony Trail 76437 South Kevinland, United States;;;+1 94175362;contact@pinnacledigital.com;EN;20150226;20151011;USD;;Y417746843\n001;xxx;US;SummitTech Global;628 Adam Brooks Apt. 090 47178 Julieside, United States;;;+1 1701579;support@summittechglobal.com;EN;20190804;20211113;USD;;772420468220\n001;xxx;US;Summit Innovations Inc.;581 Carlos Corners Suite 426 12276 New Jenniferbury, United States;;;+1 62483716;contact@summitinnovations.com;EN;20210717;20211222;USD;;X2327940360\n001;xxx;DE;BioHof Naturprodukte GmbH;Frank-Fischer-Weg 30 61044 Schw\u00e4bisch Gm\u00fcnd, Germany;;;+49 94783972;service@biohof-natur.de;DE;20220307;20220403;EUR;DE054352161;\n001;xxx;GB;Brightland Energy Ltd;599 French cliff LN2 9SP Lukefurt, United Kingdom;;;+44 72120472;info@brightlandenergy.co.uk;EN;20240905;20240910;GBP;GB650808101;\n001;xxx;GB;Bluebird Innovations;Flat 4 Jake village HX48 9YS West Rita, United Kingdom;;;+44 22753890;contact@bluebirdinnovations.co.uk;EN;20020903;20100910;GBP;GB284405520;\n001;xxx;FR;B\u00e9n\u00e9fice Sant\u00e9;711, rue Giraud 65854 Klein-la-For\u00eat, France;;;+33 60469286;info@beneficesante.fr;FR;20180114;20220930;EUR;FRmv654858755;\n001;xxx;CN;Beixin TechFront Solutions;\u5357\u660c\u8defe\u5ea7 393276 \u6b66\u6c49\u5e02, China;;;+86 65035090;inquiries@beixintechfront.com;ZH;20030404;20030409;CNY;;\n001;xxx;US;Velocity Tech Services;6819 Reid Hills 99463 South Denisehaven, United States;;;+1 88636252;contact@velocitytech.com;EN;20040320;20040328;USD;;\n001;xxx;BR;VerdeFlora Outdoor Solutions;Praia Rezende, 5 41531504 Pimenta da Prata, Brazil;;;+55 7914152;contact@verdefloraoutdoor.com.br;PT;20210911;20231202;BRL;;8209733735\n001;xxx;CN;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7 693349 \u5f20\u5bb6\u6e2f\u5e02, China;;;+86 20427767;info@baodegreentech.com;ZH;20180802;20190922;CNY;;56705154\n001;xxx;BR;PuraMar Seafood Exports;Recanto Marcela Almeida, 82 79246689 Dias do Campo, Brazil;;;+55 34118398;sales@puramarexports.com.br;PT;20210819;20220216;BRL;;K67-7206-07-0893-5\n001;xxx;DE;MediCare Solutions GmbH;\u00c4nne-Kusch-Platz 7 22267 Strasburg, Germany;;;+49 60814703;info@medicare-solutions.de;DE;20090208;20160921;EUR;DE410375625;\n001;xxx;ES;Soluciones Digitales Avanzadas S.L.;Glorieta Y\u00e9ssica Arribas 1 09718 Cantabria, Spain;;;+34 73049425;soporte@solucionesda.es;ES;20100624;20150210;EUR;ES41880379P;\n001;xxx;ES;BioTechMed Innovaci\u00f3n;Camino de \u00c1gata Pedrosa 115 31807 Huesca, Spain;;;+34 81277124;ventas@biotechmed.net;ES;20190524;20200923;EUR;;\n001;xxx;GB;Edgewater Systems;Flat 10 Roberts trace G9H 7FP Lake Staceychester, United Kingdom;;;+44 60724661;info@edgewatersystems.co.uk;EN;20221130;20241006;GBP;GBGD359;\n001;xxx;BR;EcoBrasa Biofuels;Jardim Maria Isis Abreu, 64 10876376 Macedo, Brazil;;;+55 48921425;contact@ecobrasa.com.br;PT;20081001;20180327;BRL;;2488590918\n001;xxx;BR;MedBrasa Diagnostics;P\u00e1tio Gomes, 5 54268896 Alves, Brazil;;;+55 22996640;contact@medbrasadiag.com.br;PT;20071103;20121002;BRL;;D2772878905585",
    "refusal": null
}
```

Example prompt for (2) With Steps:

```
"messages": [
    {
        "role": "user",
        "content": "Imagine that you need to merge customer data from two different companies into a unified format.\nCompany A has acquired Company B and wants to integrate Company B's customer database into its customer table.\nEach company has its own customer data stored in company specific formats, some customers may only exist in one company, some in both.\nPlease perform the following steps:\n1) Schema Matching: Find out which information from Company B needs to be integrated into which parts of Company A's schema.\n2) Entity Matching: Detect duplicates between the databases of the two companies to find out which customers are present in both.\n3) Data Integration & Transformation: Integrate all the data into the schema from Company A. Do not add additional columns to Company A's schema. Merge all the duplicates found and transform the data where necessary. Please keep the customer ID set in Company A. If a customer did not exist in Company A before, please add it and set the customer number to \"xxx\". \nReturn only the resulting output table from Company A after the integration in csv format with ; as the delimiter.\nYour output must be parsable by pandas. Do not truncate the output table but make sure to merge all duplicate rows. Do not give explanations."
    },
    {
        "role": "user",
        "content": "Company A customer table: Customers\nMANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;5724399976;FR;L'Or\u00e9al Beaut\u00e9 Digitale;360, rue de Lopes;Fontaine-sur-Chauvin;41928;+33 16254076;contact@loreal-beaute.fr;FR;20080620;20140908;EUR;FR1k723454994;\n001;3080499910;CN;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7;\u5f20\u5bb6\u6e2f\u5e02;693349;+86 20427767;info@baodegreentech.com;ZH;20180902;20190909;CNY;;\n001;745480683;CN;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7;\u5b81\u5fb7\u5e02;118334;+86 92250456;inquiries@beixinfuturetech.com;ZH;20200305;20200601;CNY;;\n001;8447755608;NL;FoodVerse Gourmet;Chlo\u00ebweg 2;Oostdijk;1499 XS;+31 1077902;info@foodverse.nl;NL;20100503;20150701;EUR;NL268366047B65;\n001;1643152015;NL;NederWoon Furniture Imports;Jessestraat 445;Zwaagdijk-Oost;5007 BV;+31 29758992;info@nederwoonfurniture.nl;NL;20160505;20170526;EUR;NL530243142B39;\n001;3434478642;FR;L'Or\u00e9al Innovation;40, rue de Pichon;Mar\u00e9chalVille;25787;+33 39507135;contact@loreal-innovation.fr;FR;20200309;20241028;EUR;FR5Q759781415;\n001;6311828430;FR;FinTech Solutions;32, rue de Martins;Saint Augustin;51362;+33 62129426;info@fintech-solutions.fr;FR;20070305;20081223;EUR;FR7Q822816108;\n001;5025147270;US;Pinnacle Digital Media;4276 Anthony Trail;South Kevinland;76437;+1 94175362;contact@pinnacledigital.com;EN;20121008;20170105;USD;;Y417746843\n001;6144048848;FR;Estelle Energie;49, chemin Marie Millet;Lecomte;13139;+33 71304025;info@estelleenergie.fr;FR;20070317;20100206;EUR;FRv4464065832;\n001;931818077;US;Oakridge Industries;8506 Clark Trace;North Dawnshire;59756;+1 98201783;sales@oakridgeindustries.com;EN;20020721;20030612;USD;;536598055\n001;8121688489;BR;EcoBrasa Biofuels;Conjunto Cassiano, 123;Macedo;10876376;+55 71174347;contact@ecobrasa.com.br;PT;20110509;20111029;BRL;;2488590918\n001;1635786830;BR;InovaMed Health Devices;P\u00e1tio Gomes, 5;Alves;54268896;+55 22996640;support@inovamedhealth.com.br;PT;20041010;20141006;BRL;;D2772878905585\n001;6670557974;ES;BioTechMed Innovaci\u00f3n;Paseo de C\u00e1ndida Quintana 6;Lugo;08453;+34 81277124;contacto@biotechmed.com;ES;20181116;20201017;EUR;ES77821903L;\n001;271099098;US;Velocity Tech Services;6819 Reid Hills;South Denisehaven;99463;+1 88636252;contact@velocitytech.com;EN;20031129;20040406;USD;;U8259197473018\n001;6731683305;GB;Brightland Energy Ltd;Studio 53 Fiona loaf;South Ameliaport;BD7 9FE;+44 72120472;info@brightlandenergy.co.uk;EN;20240626;20241003;GBP;GB650808101;\n001;1125173551;DE;NaturHof Bio GmbH;Thanelring 230;Schw\u00e4bisch Gm\u00fcnd;61044;+49 94783972;info@naturhof-bio.de;DE;20220211;20220514;EUR;DE054352161;\n001;8190498295;FR;Al\u00e9a Digital;392, boulevard de Lacroix;Duboisboeuf;12751;+33 10580269;contact@aleadigital.fr;FR;20211128;20231017;EUR;FR8w458136934;\n001;5301050982;FR;B\u00e9n\u00e9fice Sant\u00e9;711, rue Giraud;Klein-la-For\u00eat;65854;+33 60469286;info@beneficesante.fr;FR;20200229;20201031;EUR;FRmv654858755;\n001;1502870589;DE;SmartTech Solutions GmbH;Johannring 88;Suhl;88833;+49 10250170;support@smarttech.de;DE;20141104;20150720;EUR;DE279265910;\n001;8924187109;IN;BrightSphere Technologies Pvt. Ltd.;96/8937 \u0924\u092e\u093e\u0902\u0917;\u0905\u0932\u0940\u0917\u0922;570473;+91 15863492;inquiries@brightspheretechnologies.in;HI;20220819;20231104;INR;;K82-05659-339-6\n001;7808954973;ES;Terra Real Estate;Plaza de Marcelo Melero 9 Puerta 2 ;Girona;40715;+34 441171;ventas@terrare.es;ES;20081223;20200104;EUR;ESf9299226y;\n001;1561953322;US;Redstone Enterprises;132 Hester Burg;Youngborough;01941;+1 32791897;service@redstoneenterprises.com;EN;20180915;20181001;USD;;\n001;1555824610;CN;Jinyang Marine Technologies;\u798f\u5dde\u8defq\u5ea7;\u6210\u5e02;720180;+86 6596814;info@jinyangmarine.com;ZH;20071113;20110613;CNY;;E495-3899-16\n001;3985031712;CN;Beixin TechFront Solutions;\u5357\u660c\u8defe\u5ea7;\u6b66\u6c49\u5e02;393276;+86 65035090;inquiries@beixintechfront.com;ZH;20030201;20030419;CNY;;U80-82-09374\n001;8690038112;GB;Pinewood Financial Services;Flat 75l Phillip spring;New Kimberleyburgh;CW0 8HS;+44 61252485;info@pinewoodfinancial.co.uk;EN;20050211;20171201;GBP;GB140199028309;\n001;866048141;CN;Huanxing Oceanic Solutions;\u5408\u5c71\u8defQ\u5ea7;\u592a\u539f\u53bf;434727;+86 53043256;info@huanxingoceanic.com;ZH;20170806;20220822;CNY;;392-768-76\n001;5444421720;US;BlueWave Solutions;56157 Gonzalez Lodge;East Ruthshire;31342;+1 76024680;support@bluewavesolutions.com;EN;20100205;20171122;USD;;X360-8208-72-7\n001;3439890496;BR;PuraMar Seafood Exports;Recanto Marcela Almeida, 82;Dias do Campo;79246689;+55 73734238;sales@puramarexports.com.br;PT;20120501;20220429;BRL;;K67-7206-07-0893-5\n001;7657972298;ES;Alimentos Naturales S.A.;Avenida Bartolom\u00e9 Perez 14 Apt. 14 ;Huesca;01854;+34 81673175;info@alimentosnaturales.com;ES;20130410;20240110;EUR;ESF9874582Q;\n001;2842286809;CN;Jiangnan Precision Systems;\u9648\u8857w\u5ea7;\u6fb3\u95e8\u5e02;328952;+86 28067490;sales@jiangnanprecisionsys.com;ZH;20200616;20240612;CNY;;2745514264994\n Company B customer database: Customer Information Table\nID;Account Group;Role;Contract;Creation Date;Modification Date;TAX Number\n271099098;retail;0004;1;2023-12-17;2024-04-20;\n9924497969;government;0002;0;2010-06-09;2020-12-25;5499197656\n3252792004;wholesale;0003;0;2013-09-10;2014-06-27;NL268366047B65\n2624970231;government;0002;0;2013-01-25;2020-12-11;Q0965503397\n5004985293;retail;0003;0;2006-09-10;2023-10-24;FR8w458136934\n5587874777;wholesale;0005;1;2006-09-06;2012-11-29;FR20942500405\n0441480286;government;0005;1;2008-12-23;2020-01-04;ESf9299226y\n7707045239;retail;0003;1;2017-10-03;2023-11-04;NL722220170B62\n745480683;retail;0003;0;2005-02-11;2017-12-01;GB140199028309\n1046962354;retail;0004;0;2022-04-19;2022-05-21;392-768-76\n1318460154;retail;0001;0;2023-09-02;2023-09-06;K82-05659-339-6\n3080499910;wholesale;0004;0;2013-04-10;2024-01-10;ESF9874582Q\n9290863593;government;0002;1;2001-05-28;2004-03-04;536598055\n6670557974;government;0002;1;2024-10-01;2024-10-13;03-31-1467-43\n1502870589;wholesale;0003;0;2001-04-19;2022-12-08;ESO02430534\n8501549070;government;0001;0;2019-02-15;2021-07-20;FR6U405616401\n8453988787;wholesale;0001;0;2017-06-14;2020-08-06;NL163763325B19\n2842286809;wholesale;0004;0;2017-02-27;2022-07-15;F6899891960\n6163597512;government;0004;1;2003-09-18;2016-03-25;FR7Q822816108\n2993801491;retail;0004;1;2002-08-17;2023-02-21;FR1k723454994\n8351453627;wholesale;0005;0;2006-04-07;2014-05-22;E495-3899-16\n9852168978;retail;0005;1;2020-06-16;2024-06-12;2745514264994\n9211794067;government;0001;1;2008-09-18;2018-04-24;X360-8208-72-7\n8772412460;wholesale;0003;0;2018-01-27;2021-06-25;Z2279944894762\n3985031712;government;0004;1;2002-06-06;2017-06-29;NL530243142B39\n5457825284;retail;0005;1;2011-04-16;2012-01-07;ES52733472x\n8799288424;retail;0002;1;2020-01-06;2020-08-16;T1862086\n7498075056;wholesale;0005;1;2015-02-26;2015-10-11;Y417746843\n2630759141;retail;0004;1;2019-08-04;2021-11-13;772420468220\n3301346043;retail;0001;0;2021-07-17;2021-12-22;X2327940360\n5487814625;government;0003;1;2022-03-07;2022-04-03;DE054352161\n8605948619;wholesale;0002;1;2024-09-05;2024-09-10;GB650808101\n4638431434;wholesale;0002;1;2002-09-03;2010-09-10;GB284405520\n7157200042;wholesale;0003;0;2018-01-14;2022-09-30;FRmv654858755\n5704365015;retail;0001;0;2003-04-04;2003-04-09;\n6816550619;wholesale;0002;1;2004-03-20;2004-03-28;\n1635786830;wholesale;0002;0;2009-04-19;2010-01-15;FRv4464065832\n8447755608;government;0001;0;2019-09-14;2024-07-18;94410483128\n5351417752;government;0001;0;2021-09-11;2023-12-02;8209733735\n5332313005;government;0003;0;2018-08-02;2019-09-22;56705154\n5444421720;government;0005;0;2024-05-22;2024-10-04;C5817897\n5287466408;retail;0003;0;2021-08-19;2022-02-16;K67-7206-07-0893-5\n4352311683;wholesale;0001;1;2009-02-08;2016-09-21;DE410375625\n2322269914;retail;0002;1;2010-06-24;2015-02-10;ES41880379P\n0518173542;retail;0003;0;2019-05-24;2020-09-23;\n7563136213;retail;0001;0;2022-11-30;2024-10-06;GBGD359\n3434478642;retail;0005;1;2006-10-17;2016-10-18;DE279265910\n1484040534;retail;0004;1;2008-10-01;2018-03-27;2488590918\n1561953322;retail;0001;0;2008-12-09;2009-10-12;M4547761167223\n0901404965;retail;0005;1;2007-11-03;2012-10-02;D2772878905585\n Customer Contact Details Table\nCustomer ID;Organization Name;Address 1;Email Address;Country Prefix;Contact Number\n8605948619;Brightland Energy Ltd;599 French cliff LN2 9SP Lukefurt, United Kingdom;info@brightlandenergy.co.uk;44;72120472\n1561953322;Stellar Web Solutions;09925 Justin Haven 33652 East Ashleychester, United States;contact@stellarwebsolutions.com;1;50637915\n0441480286;Terra Real Estate;Plaza de Marcelo Melero 9 Puerta 2  40715 Girona, Spain;ventas@terrare.es;34;441171\n0901404965;MedBrasa Diagnostics;P\u00e1tio Gomes, 5 54268896 Alves, Brazil;contact@medbrasadiag.com.br;55;22996640\n8501549070;Paragone Consulting;1, rue de Blanchard 39938 Saint Joseph, France;contact@paragoneconsulting.fr;33;10186451\n3301346043;Summit Innovations Inc.;581 Carlos Corners Suite 426 12276 New Jenniferbury, United States;contact@summitinnovations.com;1;62483716\n2842286809;Ironclad Manufacturing Co.;88108 Jamie Circles Apt. 770 41625 New Lisa, United States;sales@ironcladmanufacturing.com;1;51766217\n7707045239;GreenFlow Energy Solutions;Carlijnsteeg 75 3901BZ Best, Netherlands;contact@greenflowenergy.nl;31;24296894\n5287466408;PuraMar Seafood Exports;Recanto Marcela Almeida, 82 79246689 Dias do Campo, Brazil;sales@puramarexports.com.br;55;34118398\n3434478642;SmartTech Solutions GmbH;Biggenallee 185 58769 Feuchtwangen, Germany;support@smarttech.de;49;10250170\n5487814625;BioHof Naturprodukte GmbH;Frank-Fischer-Weg 30 61044 Schw\u00e4bisch Gm\u00fcnd, Germany;service@biohof-natur.de;49;94783972\n5457825284;Construcci\u00f3n de Infraestructuras Sostenibles S.L.;Acceso Ariel Pintor 37 Piso 9  24997 Palencia, Spain;contacto@construccionesostenibles.es;34;99880864\n5704365015;Beixin TechFront Solutions;\u5357\u660c\u8defe\u5ea7 393276 \u6b66\u6c49\u5e02, China;inquiries@beixintechfront.com;86;65035090\n2630759141;SummitTech Global;628 Adam Brooks Apt. 090 47178 Julieside, United States;support@summittechglobal.com;1;1701579\n6163597512;FinTech Solutions;52, chemin de Roy 41118 Barbe, France;info@fintech-solutions.fr;33;62129426\n3080499910;Alimentos Naturales S.A.;Avenida Bartolom\u00e9 Perez 14 Apt. 14  01854 Huesca, Spain;info@alimentosnaturales.com;34;81673175\n2993801491;L'Or\u00e9al Beaut\u00e9 Digitale;2, chemin Guillet 41928 Fontaine-sur-Chauvin, France;contact@loreal-beaute.fr;33;16254076\n9852168978;Jiangnan Precision Systems;\u9648\u8857w\u5ea7 328952 \u6fb3\u95e8\u5e02, China;sales@jiangnanprecisionsys.com;86;28067490\n8799288424;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7 118334 \u5b81\u5fb7\u5e02, China;inquiries@beixinfuturetech.com;86;92250456\n8453988787;BlueWave Environmental Services;Saradreef 87 1380LD Bingelrade, Netherlands;services@bluewave.nl;31;59521901\n7157200042;B\u00e9n\u00e9fice Sant\u00e9;711, rue Giraud 65854 Klein-la-For\u00eat, France;info@beneficesante.fr;33;60469286\n3252792004;DutchGourmet Foods;Chlo\u00ebweg 2 1499 XS Oostdijk, Netherlands;contact@dutchgourmet.nl;31;1077902\n8447755608;Quantum Data Systems;3/1 \u0939\u091c\u093e\u0930\u093f\u0915\u093e 911243 \u0905\u092e\u0930\u093e\u0935\u0924\u0940, India;info@quantumdatasys.in;91;64043374\n3985031712;NederWoon Furniture Imports;Jessestraat 445 5007 BV Zwaagdijk-Oost, Netherlands;info@nederwoonfurniture.nl;31;29758992\n2322269914;Soluciones Digitales Avanzadas S.L.;Glorieta Y\u00e9ssica Arribas 1 09718 Cantabria, Spain;soporte@solucionesda.es;34;73049425\n5351417752;VerdeFlora Outdoor Solutions;Praia Rezende, 5 41531504 Pimenta da Prata, Brazil;contact@verdefloraoutdoor.com.br;55;7914152\n7563136213;Edgewater Systems;Flat 10 Roberts trace G9H 7FP Lake Staceychester, United Kingdom;info@edgewatersystems.co.uk;44;60724661\n9924497969;SkyBridge Logistics;718 Melissa Mountain Suite 599 26893 Lake David, United States;support@skybridgelogistics.com;1;18869006\n271099098;L'Or\u00e9al Innovation;40, rue de Pichon 25787 Mar\u00e9chalVille, France;contact@loreal-innovation.fr;33;18252866\n6816550619;Velocity Tech Services;6819 Reid Hills 99463 South Denisehaven, United States;contact@velocitytech.com;1;88636252\n1484040534;EcoBrasa Biofuels;Jardim Maria Isis Abreu, 64 10876376 Macedo, Brazil;contact@ecobrasa.com.br;55;48921425\n1635786830;Estelle Solutions Vertes;49, chemin Marie Millet 13139 Lecomte, France;info@estellesolutionsvertes.fr;33;71304025\n8351453627;Jinyang Marine Technologies;\u798f\u5dde\u8defq\u5ea7 720180 \u6210\u5e02, China;info@jinyangmarine.com;86;54668854\n745480683;Pinewood Financial Services;Flat 75l Phillip spring CW0 8HS New Kimberleyburgh, United Kingdom;info@pinewoodfinancial.co.uk;44;61252485\n5587874777;Artisanat Luxe Paris;5, rue Becker 36973 Daniel, France;contact@artisanatluxeparis.fr;33;15675279\n7498075056;Pinnacle Digital Media;4276 Anthony Trail 76437 South Kevinland, United States;contact@pinnacledigital.com;1;94175362\n1046962354;Huanxing Oceanic Solutions;\u5408\u5c71\u8defQ\u5ea7 434727 \u592a\u539f\u53bf, China;info@huanxingoceanic.com;86;58068634\n5444421720;Quantum Innovations;93577 Pineda Common Apt. 604 15578 Hunthaven, United States;support@quantuminnovations.com;1;73416298\n9211794067;BlueWave Solutions;56157 Gonzalez Lodge 31342 East Ruthshire, United States;support@bluewavesolutions.com;1;76024680\n9290863593;Oakridge Industries;8506 Clark Trace 59756 North Dawnshire, United States;sales@oakridgeindustries.com;1;98201783\n2624970231;Redstone Enterprises;09987 Dylan Causeway Suite 609 86161 Hughesfort, United States;service@redstoneenterprises.com;1;32791897\n1502870589;Oleo Puro;Acceso Andr\u00e9s Felipe Amaya 83 07652 Teruel, Spain;contacto@oleopuro.com;34;8205521\n4352311683;MediCare Solutions GmbH;\u00c4nne-Kusch-Platz 7 22267 Strasburg, Germany;info@medicare-solutions.de;49;60814703\n4638431434;Bluebird Innovations;Flat 4 Jake village HX48 9YS West Rita, United Kingdom;contact@bluebirdinnovations.co.uk;44;22753890\n1318460154;BrightSphere Technologies Pvt. Ltd.;33 \u0905\u0938\u0940\u092e \u0938\u0930\u0940\u0928 570473 \u0905\u0932\u0940\u0917\u0922, India;inquiries@brightspheretechnologies.in;91;15863492\n8772412460;VerdeFlora Landscaping;Quadra de da Rosa, 89 02349-247 Teixeira de Pimenta, Brazil;contact@verdeflora.com.br;55;67782970\n0518173542;BioTechMed Innovaci\u00f3n;Camino de \u00c1gata Pedrosa 115 31807 Huesca, Spain;ventas@biotechmed.net;34;81277124\n5004985293;Al\u00e9a Digital;392, boulevard de Lacroix 12751 Duboisboeuf, France;contact@aleadigital.fr;33;66929679\n6670557974;ZenHealth Systems Pvt. Ltd.;36/980 \u092a\u091f\u0947\u0932 748944 \u092e\u094b\u0915\u093e\u092e\u093e, India;inquiries@zenhealthsys.in;91;5081300\n5332313005;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7 693349 \u5f20\u5bb6\u6e2f\u5e02, China;info@baodegreentech.com;86;20427767\n"
    }
]
```

Example response by GPT-4o for (2) With Steps:

```
"message": {
    "role": "assistant",
    "content": "MANDT;KUNNR;LAND1;NAME1;STRAS;ORT01;PSTLZ;TELF1;SMTP_ADDR;SPRAS;ERDAT;UPDAT;WAERS;STCEG;STCD1\n001;5724399976;FR;L'Or\u00e9al Beaut\u00e9 Digitale;360, rue de Lopes;Fontaine-sur-Chauvin;41928;+33 16254076;contact@loreal-beaute.fr;FR;20020817;20230221;EUR;FR1k723454994;\n001;3080499910;CN;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7;\u5f20\u5bb6\u6e2f\u5e02;693349;+86 20427767;info@baodegreentech.com;ZH;20130410;20240110;CNY;;\n001;745480683;CN;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7;\u5b81\u5fb7\u5e02;118334;+86 92250456;inquiries@beixinfuturetech.com;ZH;20050211;20200601;CNY;;\n001;8447755608;NL;FoodVerse Gourmet;Chlo\u00ebweg 2;Oostdijk;1499 XS;+31 1077902;info@foodverse.nl;NL;20100503;20240718;EUR;NL268366047B65;\n001;1643152015;NL;NederWoon Furniture Imports;Jessestraat 445;Zwaagdijk-Oost;5007 BV;+31 29758992;info@nederwoonfurniture.nl;NL;20020606;20170629;EUR;NL530243142B39;\n001;3434478642;FR;L'Or\u00e9al Innovation;40, rue de Pichon;Mar\u00e9chalVille;25787;+33 39507135;contact@loreal-innovation.fr;FR;20061017;20241028;EUR;FR5Q759781415;\n001;6311828430;FR;FinTech Solutions;32, rue de Martins;Saint Augustin;51362;+33 62129426;info@fintech-solutions.fr;FR;20030918;20160325;EUR;FR7Q822816108;\n001;5025147270;US;Pinnacle Digital Media;4276 Anthony Trail;South Kevinland;76437;+1 94175362;contact@pinnacledigital.com;EN;20121008;20170105;USD;;Y417746843\n001;6144048848;FR;Estelle Energie;49, chemin Marie Millet;Lecomte;13139;+33 71304025;info@estelleenergie.fr;FR;20070317;20100206;EUR;FRv4464065832;\n001;931818077;US;Oakridge Industries;8506 Clark Trace;North Dawnshire;59756;+1 98201783;sales@oakridgeindustries.com;EN;20010528;20040304;USD;;536598055\n001;8121688489;BR;EcoBrasa Biofuels;Conjunto Cassiano, 123;Macedo;10876376;+55 71174347;contact@ecobrasa.com.br;PT;20081001;20180327;BRL;;2488590918\n001;1635786830;BR;InovaMed Health Devices;P\u00e1tio Gomes, 5;Alves;54268896;+55 22996640;support@inovamedhealth.com.br;PT;20041010;20141006;BRL;;D2772878905585\n001;6670557974;ES;BioTechMed Innovaci\u00f3n;Paseo de C\u00e1ndida Quintana 6;Lugo;08453;+34 81277124;contacto@biotechmed.com;ES;20181116;20241013;EUR;ES77821903L;\n001;271099098;US;Velocity Tech Services;6819 Reid Hills;South Denisehaven;99463;+1 88636252;contact@velocitytech.com;EN;20031129;20240420;USD;;U8259197473018\n001;6731683305;GB;Brightland Energy Ltd;Studio 53 Fiona loaf;South Ameliaport;BD7 9FE;+44 72120472;info@brightlandenergy.co.uk;EN;20240626;20241003;GBP;GB650808101;\n001;1125173551;DE;NaturHof Bio GmbH;Thanelring 230;Schw\u00e4bisch Gm\u00fcnd;61044;+49 94783972;info@naturhof-bio.de;DE;20220211;20220514;EUR;DE054352161;\n001;8190498295;FR;Al\u00e9a Digital;392, boulevard de Lacroix;Duboisboeuf;12751;+33 10580269;contact@aleadigital.fr;FR;20060910;20231024;EUR;FR8w458136934;\n001;5301050982;FR;B\u00e9n\u00e9fice Sant\u00e9;711, rue Giraud;Klein-la-For\u00eat;65854;+33 60469286;info@beneficesante.fr;FR;20180114;20220930;EUR;FRmv654858755;\n001;1502870589;DE;SmartTech Solutions GmbH;Johannring 88;Suhl;88833;+49 10250170;support@smarttech.de;DE;20010419;20221208;EUR;DE279265910;\n001;8924187109;IN;BrightSphere Technologies Pvt. Ltd.;96/8937 \u0924\u092e\u093e\u0902\u0917;\u0905\u0932\u0940\u0917\u0922;570473;+91 15863492;inquiries@brightspheretechnologies.in;HI;20220819;20231104;INR;;K82-05659-339-6\n001;7808954973;ES;Terra Real Estate;Plaza de Marcelo Melero 9 Puerta 2 ;Girona;40715;+34 441171;ventas@terrare.es;ES;20081223;20200104;EUR;ESf9299226y;\n001;1561953322;US;Redstone Enterprises;132 Hester Burg;Youngborough;01941;+1 32791897;service@redstoneenterprises.com;EN;20081209;20181001;USD;M4547761167223;\n001;1555824610;CN;Jinyang Marine Technologies;\u798f\u5dde\u8defq\u5ea7;\u6210\u5e02;720180;+86 6596814;info@jinyangmarine.com;ZH;20060407;20140522;CNY;;E495-3899-16\n001;3985031712;CN;Beixin TechFront Solutions;\u5357\u660c\u8defe\u5ea7;\u6b66\u6c49\u5e02;393276;+86 65035090;inquiries@beixintechfront.com;ZH;20020606;20170629;CNY;;U80-82-09374\n001;8690038112;GB;Pinewood Financial Services;Flat 75l Phillip spring;New Kimberleyburgh;CW0 8HS;+44 61252485;info@pinewoodfinancial.co.uk;EN;20050211;20171201;GBP;GB140199028309;\n001;866048141;CN;Huanxing Oceanic Solutions;\u5408\u5c71\u8defQ\u5ea7;\u592a\u539f\u53bf;434727;+86 53043256;info@huanxingoceanic.com;ZH;20170806;20220822;CNY;;392-768-76\n001;5444421720;US;BlueWave Solutions;56157 Gonzalez Lodge;East Ruthshire;31342;+1 76024680;support@bluewavesolutions.com;EN;20100205;20241004;USD;;X360-8208-72-7\n001;3439890496;BR;PuraMar Seafood Exports;Recanto Marcela Almeida, 82;Dias do Campo;79246689;+55 73734238;sales@puramarexports.com.br;PT;20120501;20220429;BRL;;K67-7206-07-0893-5\n001;7657972298;ES;Alimentos Naturales S.A.;Avenida Bartolom\u00e9 Perez 14 Apt. 14 ;Huesca;01854;+34 81673175;info@alimentosnaturales.com;ES;20130410;20240110;EUR;ESF9874582Q;\n001;2842286809;CN;Jiangnan Precision Systems;\u9648\u8857w\u5ea7;\u6fb3\u95e8\u5e02;328952;+86 28067490;sales@jiangnanprecisionsys.com;ZH;20170227;20240612;CNY;;2745514264994\n001;xxx;US;SkyBridge Logistics;718 Melissa Mountain Suite 599;Lake David;26893;+1 18869006;support@skybridgelogistics.com;EN;20100609;20201225;USD;5499197656;\n001;xxx;FR;Artisanat Luxe Paris;5, rue Becker;Daniel;36973;+33 15675279;contact@artisanatluxeparis.fr;FR;20060906;20121129;EUR;FR20942500405;\n001;xxx;NL;GreenFlow Energy Solutions;Carlijnsteeg 75;Best;3901BZ;+31 24296894;contact@greenflowenergy.nl;NL;20171003;20231104;EUR;;\n001;xxx;FR;Paragone Consulting;1, rue de Blanchard;Saint Joseph;39938;+33 10186451;contact@paragoneconsulting.fr;FR;20190215;20210720;EUR;;\n001;xxx;NL;BlueWave Environmental Services;Saradreef 87;Bingelrade;1380LD;+31 59521901;services@bluewave.nl;NL;20170614;20200806;EUR;NL163763325B19;\n001;xxx;BR;VerdeFlora Landscaping;Quadra de da Rosa, 89;Teixeira de Pimenta;02349-247;+55 67782970;contact@verdeflora.com.br;PT;20180127;20210625;BRL;Z2279944894762;\n001;xxx;ES;Construcci\u00f3n de Infraestructuras Sostenibles S.L.;Acceso Ariel Pintor 37 Piso 9;Palencia;24997;+34 99880864;contacto@construccionesostenibles.es;ES;20110416;20120107;EUR;ES52733472x;\n001;xxx;CN;Beixin Future Tech;\u897f\u5b89\u8defw\u5ea7;\u5b81\u5fb7\u5e02;118334;+86 92250456;inquiries@beixinfuturetech.com;ZH;20200106;20200816;CNY;;\n001;xxx;ES;Soluciones Digitales Avanzadas S.L.;Glorieta Y\u00e9ssica Arribas 1;Cantabria;09718;+34 73049425;soporte@solucionesda.es;ES;20100624;20150210;EUR;ES41880379P;\n001;xxx;BR;VerdeFlora Outdoor Solutions;Praia Rezende, 5;Pimenta da Prata;41531504;+55 7914152;contact@verdefloraoutdoor.com.br;PT;20210911;20231202;BRL;8209733735;\n001;xxx;GB;Edgewater Systems;Flat 10 Roberts trace;Lake Staceychester;G9H 7FP;+44 60724661;info@edgewatersystems.co.uk;EN;20221130;20241006;GBP;GBGD359;\n001;xxx;US;Velocity Tech Services;6819 Reid Hills;South Denisehaven;99463;+1 88636252;contact@velocitytech.com;EN;20040320;20040328;USD;;\n001;xxx;DE;MediCare Solutions GmbH;\u00c4nne-Kusch-Platz 7;Strasburg;22267;+49 60814703;info@medicare-solutions.de;DE;20090208;20160921;EUR;DE410375625;\n001;xxx;GB;Bluebird Innovations;Flat 4 Jake village;West Rita;HX48 9YS;+44 22753890;contact@bluebirdinnovations.co.uk;EN;20020903;20100910;GBP;GB284405520;\n001;xxx;ES;BioTechMed Innovaci\u00f3n;Camino de \u00c1gata Pedrosa 115;Huesca;31807;+34 81277124;ventas@biotechmed.net;ES;20190524;20200923;EUR;;\n001;xxx;CN;Baode GreenTech Solutions;\u9b4f\u8857E\u5ea7;\u5f20\u5bb6\u6e2f\u5e02;693349;+86 20427767;info@baodegreentech.com;ZH;20180802;20190922;CNY;56705154;",
    "refusal": null
}
```

## The Knowledge Challenge

### Exp. 9: Text-to-SIGNAL

We compare three different approaches:  
(1) we prompt the LLMs only with a short instruction explaining the task (Zero-shot)   
(2) we add three representative example queries that we hand-picked from the SIGNAL documentation (+ Examples)  
(3) we include both the examples as well as the full documentation of the SIGNAL language in the prompt (+
Documentation)

Prompt templates:

```
(1) prompt_chat_template:
  - role: "system"
    content: |-
      You are a SIGNAL assistant which translates textual descriptions into SIGNAL queries. SIGNAL stands for Signavio Analytics Language and is a domain-specific query language for SAP Signavio's Process Intelligence Suite.
      Your task is to construct a SIGNAL query that returns precisely the information asked for in the given textual description.
      
      Follow these rules:
      Put all variables and parameters in parentheses in your response.
      Make sure to state only the signal query and no additional explaining text.
      Do not reference THIS_PROCESS, but instead replace it with the actual data source table name. Never ever generate THIS_PROCESS in your response.
      The names of the actual data source table name must be put in double quotes.
      Never generate a * (asterisk or star character).
  - role: "user"
    content: "{{signal}}"

(2) prompt_chat_fewshot_template:
  - role: "system"
    content: |-
      You are a SIGNAL assistant which translates textual descriptions into SIGNAL queries. SIGNAL stands for Signavio Analytics Language and is a domain-specific query language for SAP Signavio's Process Intelligence Suite.
      Your task is to construct a SIGNAL query that returns precisely the information asked for in the given textual description.
      
      Follow these rules:
      Put all variables and parameters in parentheses in your response.
      Make sure to state only the signal query and no additional explaining text.
      Do not reference THIS_PROCESS, but instead replace it with the actual data source table name. Never ever generate THIS_PROCESS in your response.
      The names of the actual data source table name must be put in double quotes.
      Never generate a * (asterisk or star character).
      
      Here are some example SIGNAL queries:
      SELECT AVG ((SELECT FIRST (END_TIME) FILTER (WHERE EVENT_NAME LIKE 'Complete%' AND "Routing Step" = '0010')) - (SELECT FIRST (END_TIME) FILTER (WHERE EVENT_NAME LIKE 'Start%' AND "Routing Step" = '0010'))) FROM "2c30aebe-08ac-4606-934e-9d4946edfc8a"
      SELECT COUNT(case_id) FILTER (WHERE ("Last Inv. Item Clearing Date" IS NULL) AND "Last Inv. Item Due Date" < DATE_TRUNC('day', NOW())) FROM "defaultview-225"
      SELECT COUNT(event_name) AS "# Created Process Orders", (COUNT (EVENT_NAME) FILTER (WHERE "Event Created By User Type" NOT IN ('Dialog'))) / (COUNT (EVENT_NAME)) * 100 AS "Automation Rate", "Division" FROM FLATTEN("defaultview-183") WHERE "Planned Order Number" IS NULL AND EVENT_NAME = 'Create Process Order' ORDER BY 1 desc LIMIT 10
  - role: "user"
    content: "{{signal}}"

(3) prompt_chat_fewshot_doc_template:
  - role: "system"
    content: |-
      You are a SIGNAL assistant which translates textual descriptions into SIGNAL queries. SIGNAL stands for Signavio Analytics Language and is a domain-specific query language for SAP Signavio's Process Intelligence Suite.
      Your task is to construct a SIGNAL query that returns precisely the information asked for in the given textual description.
      
      Follow these rules:
      Put all variables and parameters in parentheses in your response.
      Make sure to state only the signal query and no additional explaining text.
      Do not reference THIS_PROCESS, but instead replace it with the actual data source table name. Never ever generate THIS_PROCESS in your response.
      The names of the actual data source table name must be put in double quotes.
      Never generate a * (asterisk or star character).
      
      Here is the SIGNAL documentation:
      {{documentation}}
      
      Here are some example SIGNAL queries:
      SELECT AVG ((SELECT FIRST (END_TIME) FILTER (WHERE EVENT_NAME LIKE 'Complete%' AND "Routing Step" = '0010')) - (SELECT FIRST (END_TIME) FILTER (WHERE EVENT_NAME LIKE 'Start%' AND "Routing Step" = '0010'))) FROM "2c30aebe-08ac-4606-934e-9d4946edfc8a"
      SELECT COUNT(case_id) FILTER (WHERE ("Last Inv. Item Clearing Date" IS NULL) AND "Last Inv. Item Due Date" < DATE_TRUNC('day', NOW())) FROM "defaultview-225"
      SELECT COUNT(event_name) AS "# Created Process Orders", (COUNT (EVENT_NAME) FILTER (WHERE "Event Created By User Type" NOT IN ('Dialog'))) / (COUNT (EVENT_NAME)) * 100 AS "Automation Rate", "Division" FROM FLATTEN("defaultview-183") WHERE "Planned Order Number" IS NULL AND EVENT_NAME = 'Create Process Order' ORDER BY 1 desc LIMIT 10
  - role: "user"
    content: "{{signal}}"
```

Example prompt for (1) Zero-shot:

```
"messages": [
    {
        "role": "system",
        "content": "You are a SIGNAL assistant which translates textual descriptions into SIGNAL queries. SIGNAL stands for Signavio Analytics Language and is a domain-specific query language for SAP Signavio's Process Intelligence Suite.\nYour task is to construct a SIGNAL query that returns precisely the information asked for in the given textual description.\n\nFollow these rules:\nPut all variables and parameters in parentheses in your response.\nMake sure to state only the signal query and no additional explaining text.\nDo not reference THIS_PROCESS, but instead replace it with the actual data source table name. Never ever generate THIS_PROCESS in your response.\nThe names of the actual data source table name must be put in double quotes.\nNever generate a * (asterisk or star character)."
    },
    {
        "role": "user",
        "content": "Summarize the number of ongoing SLA (Service Level Agreement) requests in the 'defaultview-21' table."
    }
]
```

Example response by GPT-4o for (1) Zero-shot:

```
"message": {
    "content":" ```\nSELECT COUNT() AS (Number_of_Ongoing_SLA_Requests)\nFROM \"defaultview-21\"\nWHERE (SLA_Status) = 'Ongoing'\n```",
    "refusal": null,
    "role": "assistant"
}
```

Example prompt for (2) Few-shot:

```
"messages": [
    {
        "role": "system",
        "content": "You are a SIGNAL assistant which translates textual descriptions into SIGNAL queries. SIGNAL stands for Signavio Analytics Language and is a domain-specific query language for SAP Signavio's Process Intelligence Suite.\nYour task is to construct a SIGNAL query that returns precisely the information asked for in the given textual description.\n\nFollow these rules:\nPut all variables and parameters in parentheses in your response.\nMake sure to state only the signal query and no additional explaining text.\nDo not reference THIS_PROCESS, but instead replace it with the actual data source table name. Never ever generate THIS_PROCESS in your response.\nThe names of the actual data source table name must be put in double quotes.\nNever generate a * (asterisk or star character).\n\nHere are some example SIGNAL queries:\nSELECT AVG ((SELECT FIRST (END_TIME) FILTER (WHERE EVENT_NAME LIKE 'Complete%' AND \"Routing Step\" = '0010')) - (SELECT FIRST (END_TIME) FILTER (WHERE EVENT_NAME LIKE 'Start%' AND \"Routing Step\" = '0010'))) FROM \"2c30aebe-08ac-4606-934e-9d4946edfc8a\"\nSELECT COUNT(case_id) FILTER (WHERE (\"Last Inv. Item Clearing Date\" IS NULL) AND \"Last Inv. Item Due Date\" < DATE_TRUNC('day', NOW())) FROM \"defaultview-225\"\nSELECT COUNT(event_name) AS \"# Created Process Orders\", (COUNT (EVENT_NAME) FILTER (WHERE \"Event Created By User Type\" NOT IN ('Dialog'))) / (COUNT (EVENT_NAME)) * 100 AS \"Automation Rate\", \"Division\" FROM FLATTEN(\"defaultview-183\") WHERE \"Planned Order Number\" IS NULL AND EVENT_NAME = 'Create Process Order' ORDER BY 1 desc LIMIT 10"
    },
    {
        "role": "user",
        "content": "Summarize the number of ongoing SLA (Service Level Agreement) requests in the 'defaultview-21' table."
    }
]
```

Example response by GPT-4o for (2) Few-shot:

```
"message": {
    "content": "SELECT COUNT(case_id) FILTER (WHERE \"SLA Status\" = 'Ongoing') FROM \"defaultview-21\"",
    "refusal": null,
    "role": "assistant"
}
```

Example prompt for (3) Few-shot + Documentation:


```
{
  "model":"gpt-4o-2024-08-06",
  "max_tokens":null,
  "temperature":0,
  "messages":[
    {
      "role":"system",
      "content":"You are a SIGNAL assistant which translates textual descriptions into SIGNAL queries. SIGNAL stands for Signavio Analytics Language and is a domain-specific query language for SAP Signavio's Process Intelligence Suite.\nYour task is to construct a SIGNAL query that returns precisely the information asked for in the given textual description.\n\nFollow these rules:\nPut all variables and parameters in parentheses in your response.\nMake sure to state only the signal query and no additional explaining text.\nDo not reference THIS_PROCESS, but instead replace it with the actual data source table name. Never ever generate THIS_PROCESS in your response.\nThe names of the actual data source table name must be put in double quotes.\nNever generate a * (asterisk or star character).\n\nHere is the SIGNAL documentation:
      
      [Skipped here because the full documentation is too long.]
      
    },
    {
      "role":"user",
      "content":"Summarize the number of ongoing SLA (Service Level Agreement) requests in the 'defaultview-21' table."
    }
  ]
}

```

Example response by GPT-4o for (3) Few-shot + Documentation:

```
"message": {
    "content": "SELECT COUNT(case_id) AS \"Ongoing SLA Requests\" FROM \"defaultview-21\" WHERE (SELECT LAST(event_name)) NOT IN ('SLA Completed', 'SLA Canceled')",
    "refusal": null,
    "role": "assistant"
}
```

### Exp. 10: Schema customizations

Prompt template:

```
prompt_chat_template:
  - role: "user"
    content: |-
      Tell me all column names of the following SAP table. Provide just the column names as a JSON list without any introduction or explanation.
      SAP Table name is: {{table}}
```

Example prompt:

```
"messages": [
    {
        "role": "user",
        "content": "Tell me all column names of the following SAP table. Provide just the column names as a JSON list without any introduction or explanation.\nSAP Table name is: A4BM"
    }
]
```

Example response by GPT-4o-mini:

```
"message":{
    "content": "```json\n[\"MANDT\", \"BUKRS\", \"BELNR\", \"GJAHR\", \"BLART\", \"BLDAT\", \"BUDAT\", \"CPUDT\", \"CPUTM\", \"USNAM\", \"TCODE\", \"XBLNR\", \"AWKEY\", \"AWORG\", \"AWART\", \"AWBAS\", \"AWBAS2\", \"AWBAS3\", \"AWBAS4\", \"AWBAS5\", \"AWBAS6\", \"AWBAS7\", \"AWBAS8\", \"AWBAS9\", \"AWBAS10\"]\n```",
    "refusal": null,
    "role": "assistant"
}
```
