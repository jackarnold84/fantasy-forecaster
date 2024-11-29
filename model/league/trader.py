import itertools
from collections import defaultdict
from functools import lru_cache
from typing import Iterable, Iterator, List, Tuple, TypeAlias

from league.team import Team
from players.universe import PlayerUniverse
from players.weights import team_position_weights
from tqdm import tqdm

Package: TypeAlias = Tuple[str, ...]
Trade: TypeAlias = Tuple[str, str, Package, Package]

position_exclusions = {
    'football': ['K', 'DST'],
    'baseball': [],
    'basketball': [],
}


class Trader:

    def __init__(self, sport: str, week: int, teams: List[Team], player_universe: PlayerUniverse):
        self.pos_weights = {
            pos: team_position_weights[sport][pos]
            for pos in team_position_weights[sport]
            if pos not in position_exclusions[sport]
        }

        self.player_positions = {
            pid: player_universe.players[pid].pos_group
            for pid in player_universe.players
        }

        self.player_ratings = {
            pid: player_universe.players[pid].get_rating(week)
            for pid in player_universe.players
        }

        self.teams = {
            t.id: [
                pid for pid in t.get_roster(week)
                if self.player_positions[pid] in self.pos_weights
                and player_universe.players[pid].get_status(week) != 'injured'
            ]
            for t in teams
        }

        # assertions
        for t in self.teams:
            for pid in self.teams[t]:
                assert self.player_positions[pid] in self.pos_weights

    def run(self):
        print('running trader')
        self.get_filtered_trades()

    # TODO: complete filter trades function
    def get_filtered_trades(self):
        beneficial_trades = self.get_beneficial_trades()
        trades = [
            {
                "score": score,
                "trade": (tid1, tid2, pkg1, pkg2),
                "managers": (tid1, tid2),
                "players": frozenset(pkg1 + pkg2),
                "positions": (
                    tuple(sorted(self.player_positions[pid] for pid in pkg1)),
                    tuple(sorted(self.player_positions[pid] for pid in pkg2))
                ),
            }
            for score, (tid1, tid2, pkg1, pkg2) in beneficial_trades
            if score > 0.1
        ]

        trades_by_managers = defaultdict(list)
        for trade in trades:
            trades_by_managers[trade['managers']].append(trade)

        # remove trades with extra non-benefit players
        keep_trades = []
        for managers, grouped_trades in trades_by_managers.items():
            grouped_trades.sort(key=lambda x: (-x['score'], len(x['players'])))
            for i, trade1 in enumerate(grouped_trades):
                keep = True
                for trade2 in grouped_trades[:i]:
                    if trade2['players'].issubset(trade1['players']):
                        keep = False
                        break
                if keep:
                    keep_trades.append(trade1)

        print("before", len(trades), "--> after", len(keep_trades))

        # keep bottom 30% of trades
        keep_trades.sort(key=lambda x: -x['score'])
        keep_trades = keep_trades[:int(len(keep_trades) * 0.4)]

        trades = keep_trades

        trades_by_managers = defaultdict(list)
        for trade in trades:
            trades_by_managers[trade['managers']].append(trade)

        for managers, grouped_trades in trades_by_managers.items():
            dist_pos = set(x['positions'] for x in grouped_trades)
            print(managers, len(grouped_trades), "->", len(dist_pos))

        for managers, grouped_trades in trades_by_managers.items():
            trades_by_pos = defaultdict(list)
            for trade in grouped_trades:
                trades_by_pos[trade['positions']].append(trade)

            print("\n\nmanagers", managers)
            for positions, pos_grouped_trades in trades_by_pos.items():
                pos_grouped_trades.sort(key=lambda x: -x['score'])
                print(positions, len(pos_grouped_trades))

                for trade in pos_grouped_trades:
                    print(round(trade['score'], 3), trade['trade'])

    def get_beneficial_trades(self) -> Iterator[Tuple[float, Trade]]:
        initial_team_ratings = {
            tid: self.get_team_rating(self.teams[tid])
            for tid in self.teams
        }

        for tid1, tid2, pkg1, pkg2 in tqdm(self.generate_all_trade_combos()):
            team1 = self.teams[tid1].copy()
            team2 = self.teams[tid2].copy()

            rtg1_before = initial_team_ratings[tid1]
            rtg2_before = initial_team_ratings[tid2]

            for pid in pkg1:
                team1.remove(pid)
                team2.append(pid)
            for pid in pkg2:
                team2.remove(pid)
                team1.append(pid)

            rtg1_after = self.get_team_rating(team1)
            rtg2_after = self.get_team_rating(team2)

            if rtg1_after > rtg1_before and rtg2_after > rtg2_before:
                benefit_score = ((rtg1_after - rtg1_before) *
                                 (rtg2_after - rtg2_before))**0.5
                yield benefit_score, (tid1, tid2, pkg1, pkg2)

    def generate_all_trade_combos(self) -> Iterator[Trade]:
        team_combinations = itertools.combinations(
            sorted(self.teams.keys()), 2,
        )
        for tid1, tid2 in team_combinations:
            team1 = self.teams[tid1]
            team2 = self.teams[tid2]

            for n_players1 in [1, 2]:
                for n_players2 in [1, 2]:
                    for pkg1 in itertools.combinations(team1, n_players1):
                        for pkg2 in itertools.combinations(team2, n_players2):
                            yield (tid1, tid2, pkg1, pkg2)

    def get_position_weight(self, pos: str, idx: int, default=0.05) -> float:
        return self.pos_weights[pos][idx] if idx < len(self.pos_weights[pos]) else default

    def get_team_rating(self, team: Iterable[str]) -> float:
        eval_groups = defaultdict(list)

        for pid in team:
            pos = self.player_positions[pid]
            rating = self.player_ratings[pid]
            eval_groups[pos].append(rating)

        team_rating = 0
        for pos, ratings in eval_groups.items():
            ratings.sort(reverse=True)
            team_rating += self.get_pos_group_rating(pos, tuple(ratings))

        return team_rating

    @lru_cache(maxsize=10_000)
    def get_pos_group_rating(self, pos: str, ratings: Tuple[float, ...]) -> float:
        total = 0
        for idx, rating in enumerate(ratings):
            total += rating * self.get_position_weight(pos, idx)
        return total
