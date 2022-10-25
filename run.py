import builder


builder.Builder('purdue-2022', week=7, n_sim=30000).build_report()

builder.Builder('morton-2022', week=7, n_sim=20000).build_report()

builder.Builder('capitalone-2022', week=7, n_sim=10000).build_report()

# builder.Builder('purdue-baseball-2022', week=16, n_sim=20000).build_report()

# builder.Builder('purdue-2021', week=14, n_sim=20000).build_report()

# builder.Builder('morton-2021', week=11, n_sim=20000).build_report()


builder.build_homepage()
