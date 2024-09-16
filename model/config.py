from datetime import datetime

from db import db

# config data is read from the fantasy forecaster s3 bucket at config.json
config_data = db.read_s3_config()

leagues = config_data['leagues']
week_dates = config_data['weeks']
aliases = config_data['aliases']

def get_current_week(sport):
    current_date = datetime.now().date()
    if sport not in week_dates:
        return 0
    sorted_weeks = sorted(week_dates[sport].items(), reverse=True)

    for week, start_date in sorted_weeks:
        if current_date >= datetime.strptime(start_date, '%Y-%m-%d').date():
            return int(week)
    return 0
