import builder
import metrics.players.evaluator as Player
import metrics.league.evaluator as League

p = Player.Evaluator(year=2022, week=15)
l = League.Evaluator('purdue-2022', week=15, players=p.players, draft_recap_week=13)

# builder.Builder('purdue-2022', week=15, n_sim=1000).build_report()

# builder.Builder('morton-2022', week=14, n_sim=20000).build_report()

# builder.Builder('capitalone-2022', week=14, n_sim=10000).build_report()

# builder.Builder('capitalone-basketball-2022', week=9, n_sim=10000).build_report()

# builder.Builder('purdue-baseball-2022', week=16, n_sim=20000).build_report()

# builder.Builder('purdue-2021', week=14, n_sim=20000).build_report()

# builder.Builder('morton-2021', week=11, n_sim=20000).build_report()


# builder.build_homepage()
