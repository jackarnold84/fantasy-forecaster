from datetime import datetime

from db.db import read_s3_config


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.config_data = read_s3_config()
        self.leagues = self.config_data['leagues']
        self.week_dates = self.config_data['weeks']
        self.aliases = self.config_data['aliases']

    def get_current_week(self, sport):
        current_date = datetime.now().date()
        if sport not in self.week_dates:
            return 0
        sorted_weeks = sorted(
            self.week_dates[sport].items(),
            key=lambda x: int(x[0]),
            reverse=True,
        )

        for week, start_date in sorted_weeks:
            if current_date >= datetime.strptime(start_date, '%Y-%m-%d').date():
                return int(week)
        return 0
