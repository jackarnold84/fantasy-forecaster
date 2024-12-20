import itertools
import random
from collections import defaultdict
from functools import lru_cache
from typing import Iterable, Iterator, List, Tuple, TypeAlias

from league.team import Team
from players.universe import PlayerUniverse
from players.weights import team_position_weights
from tqdm import tqdm

Package: TypeAlias = Tuple[str, ...]
Trade: TypeAlias = Tuple[str, str, Package, Package]
TeamPair: TypeAlias = Tuple[str, str]
Eval: TypeAlias = Tuple[float, float, float]

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
                if pid in player_universe.players
                and self.player_positions[pid] in self.pos_weights
                and player_universe.players[pid].get_status(week) != 'injured'
            ]
            for t in teams
        }

        self.team_names = {
            t.id: t.name
            for t in teams
        }

        # assertions
        for t in self.teams:
            for pid in self.teams[t]:
                assert self.player_positions[pid] in self.pos_weights

    def run(self) -> List[List[dict]]:
        featured_trades = self.filter_and_select_trades()
        return featured_trades

    def filter_and_select_trades(self) -> List[List[dict]]:
        trades_list = [
            {
                'benefit': benefit,
                'trade': (tid1, tid2, pkg1, pkg2),
                'teams': (tid1, tid2),
                'gains': (t1_gain, t2_gain),
                'players': frozenset(pkg1 + pkg2),
                'positions': (
                    tuple(sorted(self.player_positions[pid] for pid in pkg1)),
                    tuple(sorted(self.player_positions[pid] for pid in pkg2))
                ),
            }
            for (benefit, t1_gain, t2_gain), (tid1, tid2, pkg1, pkg2) in self.get_beneficial_trades()
        ]

        # sort functions
        def rating_sorter(pid): return -self.player_ratings[pid]
        def benefit_sorter(x): return (-x['benefit'], len(x['players']))
        def gain_sorter(x): return -x['gain']

        trades_by_teams = defaultdict(list)
        for trade in trades_list:
            trades_by_teams[trade['teams']].append(trade)

        # remove trades with extra non-benefit players
        keep_trades = []
        for trades in trades_by_teams.values():
            trades.sort(key=benefit_sorter)
            for i, trade1 in enumerate(trades):
                keep = True
                for trade2 in trades[:i]:
                    if trade2['players'].issubset(trade1['players']):
                        keep = False
                        break
                if keep:
                    keep_trades.append(trade1)

        trades_list = keep_trades

        # keep top 60% of trades
        trades_list.sort(key=benefit_sorter)
        trades_list = trades_list[:int(len(keep_trades) * 0.6)]

        # group trades by team pair and position
        trades_by_teams_pos = defaultdict(lambda: defaultdict(list))
        for trade in trades_list:
            teams = trade['teams']
            pos = trade['positions']
            trades_by_teams_pos[teams][pos].append(trade)

        # random select featured trades
        n_featured = len(self.teams) // 2 + 1
        teams_keys = list(trades_by_teams_pos.keys())
        team_pairs = self.select_team_pairs(teams_keys, n_featured)

        featured_trades = []
        for teams in team_pairs:
            trade_pos = trades_by_teams_pos[teams]
            trades = random.choice(list(trade_pos.values()))
            selected = random.choice(trades)
            featured_trades.append(selected)

        # format for output
        result = [
            sorted(
                [
                    {
                        'team': self.team_names[t['teams'][0]],
                        'players': sorted(list(t['trade'][2]), key=rating_sorter),
                        'gain': round(t['gains'][0], 3),
                    },
                    {
                        'team': self.team_names[t['teams'][1]],
                        'players': sorted(list(t['trade'][3]), key=rating_sorter),
                        'gain': round(t['gains'][1], 3),
                    },
                ],
                key=gain_sorter
            ) for t in featured_trades
        ]
        return result

    def select_team_pairs(self, pairings: List[TeamPair], max_len: int) -> List[TeamPair]:
        to_include = set([item for sublist in pairings for item in sublist])
        random.shuffle(pairings)
        counts = defaultdict(int)
        res = []
        # attempt to select subset representing all teams
        for a, b in pairings:
            if (counts[a] == 0 and counts[b] < 2) or (counts[b] == 0 and counts[a] < 2):
                res.append((a, b))
                counts[a] += 1
                counts[b] += 1
            if len(counts) >= len(to_include):
                break

        random.shuffle(res)
        return res[:max_len]

    def get_beneficial_trades(self) -> Iterator[Tuple[Eval, Trade]]:
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
                t1_gain = rtg1_after - rtg1_before
                t2_gain = rtg2_after - rtg2_before
                benefit_score = (t1_gain * t2_gain)**0.5
                yield (benefit_score, t1_gain, t2_gain), (tid1, tid2, pkg1, pkg2)

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

        return float(team_rating)

    @lru_cache(maxsize=10_000)
    def get_pos_group_rating(self, pos: str, ratings: Tuple[float, ...]) -> float:
        total = 0
        for idx, rating in enumerate(ratings):
            total += rating * self.get_position_weight(pos, idx)
        return total
