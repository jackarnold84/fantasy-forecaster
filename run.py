from build.builder import Builder, build_homepage
import metrics.players.evaluator as Player
import metrics.league.evaluator as League

p = Player.Evaluator(year=2022, week=16)
l = League.Evaluator('purdue-2022', week=16, players=p.players, draft_recap_week=13)

Builder('purdue-2022', week=8, n_sim=10000).build_report()

# Builder('morton-2022', week=14, n_sim=20000).build_report()

# Builder('capitalone-2022', week=14, n_sim=10000).build_report()

# Builder('capitalone-basketball-2022', week=9, n_sim=10000).build_report()

# Builder('purdue-baseball-2022', week=16, n_sim=20000).build_report()

# Builder('purdue-2021', week=14, n_sim=20000).build_report()

# Builder('morton-2021', week=11, n_sim=20000).build_report()


build_homepage()
