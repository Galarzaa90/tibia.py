import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent, ListedTournament, PvpType, RuleSet, ScoreSet, Tournament, TournamentLeaderboard, \
    TournamentPhase

FILE_TOURNAMENT_SIGN_UP = "tournaments/tibiacom_sign_up.txt"
FILE_TOURNAMENT_ARCHIVE = "tournaments/tibiacom_archive.txt"
FILE_TOURNAMENT_NOT_ACTIVE = "tournaments/tibiacom_not_active.txt"
FILE_TOURNAMENT_NOT_FOUND = "tournaments/tibiacom_not_found.txt"
FILE_TOURNAMENT_LEADERBOARD_ENDED = "tournaments/tibiacom_leaderboard_ended.txt"
FILE_TOURNAMENT_LEADERBOARD_CURRENT = "tournaments/tibiacom_leaderboard_current.txt"
FILE_TOURNAMENT_LEADERBOARD_NO_DATA = "tournaments/tibiacom_leaderboard_no_data.txt"
FILE_TOURNAMENT_LEADERBOARD_SELECTOR = "tournaments/tibiacom_leaderboard_selector.txt"


class TestTournaments(TestCommons, unittest.TestCase):
    # region Tournaments Tests
    def test_tournament_from_content(self):
        """Testing parsing a tournament's info page"""
        content = self.load_resource(FILE_TOURNAMENT_SIGN_UP)
        tournament = Tournament.from_content(content)
        self.assertEqual(tournament.title, "TRIUMPH")
        self.assertEqual(TournamentPhase.SIGN_UP, tournament.phase)
        self.assertIsInstance(tournament.start_date, datetime.datetime)
        self.assertIsInstance(tournament.end_date, datetime.datetime)
        self.assertEqual(6, len(tournament.worlds))
        self.assertIsInstance(tournament.rule_set, RuleSet)
        self.assertIsInstance(tournament.score_set, ScoreSet)

        self.assertEqual(datetime.timedelta(days=7), tournament.duration)

        # Rule Set
        rule_set = tournament.rule_set
        self.assertEqual(PvpType.OPEN_PVP, rule_set.pvp_type)
        self.assertEqual(datetime.timedelta(hours=4), rule_set.daily_tournament_playtime)
        self.assertEqual(datetime.timedelta(hours=14), rule_set.total_tournament_playtime)
        self.assertTrue(rule_set.playtime_reduced_only_in_combat)
        self.assertEqual(2.0, rule_set.death_penalty_modifier)
        self.assertEqual(7.0, rule_set.xp_multiplier)
        self.assertEqual(10.0, rule_set.skill_multiplier)
        self.assertEqual(2.0, rule_set.spawn_rate_multiplier)
        self.assertEqual(2.0, rule_set.loot_probability)
        self.assertEqual(10, rule_set.rent_percentage)
        self.assertEqual(0, rule_set.house_auction_durations)

        # Score Set
        score_set = tournament.score_set
        self.assertEqual(100, score_set.level_gain_loss)
        self.assertEqual(30, score_set.charm_point_multiplier)
        self.assertEqual(-200, score_set.character_death)

        # Reward Set
        reward_set = tournament.reward_set
        first_prize = reward_set[0]
        self.assertEqual(1, first_prize.initial_rank)
        self.assertEqual(1, first_prize.last_rank)
        self.assertEqual(4000, first_prize.tibia_coins)
        self.assertEqual(2500, first_prize.tournament_coins)
        self.assertEqual(0, first_prize.tournament_ticker_voucher)
        self.assertEqual("gold cup", first_prize.cup)
        self.assertEqual("golden deed", first_prize.deed)
        self.assertEqual("golden crown", first_prize.other_rewards)
        self.assertEqual((1, 9999), tournament.rewards_range)
        reward = tournament.rewards_for_rank(80)
        self.assertEqual(400, reward.tournament_coins)
        self.assertIsNone(tournament.rewards_for_rank(50000))

        last_prize = reward_set[-1]
        self.assertEqual(201, last_prize.initial_rank)
        self.assertEqual(9999, last_prize.last_rank)
        self.assertEqual(0, last_prize.tibia_coins)
        self.assertEqual(100, last_prize.tournament_coins)
        self.assertEqual(0, first_prize.tournament_ticker_voucher)
        self.assertIsNone(last_prize.cup)
        self.assertEqual("papyrus deed", last_prize.deed)
        self.assertIsNone(last_prize.other_rewards)

    def test_tournament_from_content_archived(self):
        """Testing parsing a tournament archive info page"""
        content = self.load_resource(FILE_TOURNAMENT_ARCHIVE)
        tournament = Tournament.from_content(content)
        self.assertEqual(tournament.title, "GLORY")
        self.assertEqual(TournamentPhase.ENDED, tournament.phase)
        self.assertIsInstance(tournament.start_date, datetime.datetime)
        self.assertIsInstance(tournament.end_date, datetime.datetime)
        self.assertEqual(6, len(tournament.worlds))
        self.assertIsInstance(tournament.rule_set, RuleSet)
        self.assertIsInstance(tournament.score_set, ScoreSet)
        self.assertEqual(tournament.url, Tournament.get_url(tournament.cycle))

        # Rule Set
        rule_set = tournament.rule_set
        self.assertEqual(PvpType.OPEN_PVP, rule_set.pvp_type)
        self.assertEqual(datetime.timedelta(hours=2), rule_set.daily_tournament_playtime)
        self.assertIsNone(rule_set.total_tournament_playtime)
        self.assertFalse(rule_set.playtime_reduced_only_in_combat)
        self.assertEqual(1.0, rule_set.death_penalty_modifier)
        self.assertEqual(7.0, rule_set.xp_multiplier)
        self.assertEqual(10.0, rule_set.skill_multiplier)
        self.assertEqual(1.0, rule_set.spawn_rate_multiplier)
        self.assertEqual(1.0, rule_set.loot_probability)
        self.assertEqual(10, rule_set.rent_percentage)
        self.assertEqual(0, rule_set.house_auction_durations)

        # Score Set
        score_set = tournament.score_set
        self.assertEqual(100, score_set.level_gain_loss)
        self.assertEqual(0, score_set.charm_point_multiplier)
        self.assertEqual(0, score_set.character_death)

        # Reward Set
        reward_set = tournament.reward_set
        first_prize = reward_set[0]
        self.assertEqual(1, first_prize.initial_rank)
        self.assertEqual(1, first_prize.last_rank)
        self.assertEqual(3000, first_prize.tibia_coins)
        self.assertEqual(1750, first_prize.tournament_coins)
        self.assertEqual(1, first_prize.tournament_ticker_voucher)

        last_prize = reward_set[-1]
        self.assertEqual(201, last_prize.initial_rank)
        self.assertEqual(99999, last_prize.last_rank)
        self.assertEqual(0, last_prize.tibia_coins)
        self.assertEqual(0, last_prize.tournament_ticker_voucher)
        self.assertEqual(100, last_prize.tournament_coins)
        self.assertIsNone(last_prize.cup)
        self.assertIsNone(last_prize.deed)
        self.assertIsNone(last_prize.other_rewards)

    def test_tournament_from_content_not_active(self):
        """Testing parsing the tournament page when ther'es no active tournament.."""
        content = self.load_resource(FILE_TOURNAMENT_NOT_ACTIVE)
        tournament = Tournament.from_content(content)
        self.assertIsNone(tournament)

    def test_tournament_from_content_not_found(self):
        """Testing parsing a tournament that doesn't exist."""
        content = self.load_resource(FILE_TOURNAMENT_NOT_FOUND)
        tournament = Tournament.from_content(content)
        self.assertIsNone(tournament)

    def test_tournament_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            Tournament.from_content(content)
    # endregion
    # region Tournament Leaderboards

    def test_tournament_leaderboard_from_content_running(self):
        """Testing parsing the leaderboards for a tournament that is currently running."""
        content = self.load_resource(FILE_TOURNAMENT_LEADERBOARD_CURRENT)
        leaderboard = TournamentLeaderboard.from_content(content)

        self.assertIsInstance(leaderboard.tournament, ListedTournament)
        self.assertEqual("TRIUMPH", leaderboard.tournament.title)
        self.assertIsNone(leaderboard.tournament.start_date)
        self.assertIsNone(leaderboard.tournament.end_date)
        self.assertIsNone(leaderboard.tournament.duration)
        self.assertEqual(4, leaderboard.tournament.cycle)
        self.assertEqual(1, leaderboard.from_rank)
        self.assertEqual(100, leaderboard.to_rank)
        self.assertEqual(100, len(leaderboard.entries))
        self.assertEqual(1, leaderboard.page)
        self.assertEqual(2, leaderboard.total_pages)
        self.assertEqual(198, leaderboard.results_count)
        self.assertEqual("Endebra", leaderboard.world)

    def test_tournament_leaderboard_from_content_ended(self):
        """Testing parsing the leaderboards for a tournament that already ended."""
        content = self.load_resource(FILE_TOURNAMENT_LEADERBOARD_ENDED)
        leaderboard = TournamentLeaderboard.from_content(content)

        self.assertIsInstance(leaderboard.tournament, ListedTournament)
        self.assertEqual("GLORY", leaderboard.tournament.title)
        self.assertIsInstance(leaderboard.tournament.start_date, datetime.date)
        self.assertIsInstance(leaderboard.tournament.end_date, datetime.date)
        self.assertEqual(datetime.timedelta(days=7), leaderboard.tournament.duration)
        self.assertEqual(3, leaderboard.tournament.cycle)
        self.assertEqual(1, leaderboard.from_rank)
        self.assertEqual(65, len(leaderboard.entries))
        self.assertEqual(1, leaderboard.total_pages)
        self.assertEqual(65, leaderboard.results_count)
        self.assertEqual("Endebra", leaderboard.world)

    def test_tournament_leaderboard_from_content_no_data(self):
        """Testing parsing the leaderboards's when there's no data."""
        content = self.load_resource(FILE_TOURNAMENT_LEADERBOARD_NO_DATA)
        leaderboard = TournamentLeaderboard.from_content(content)

        self.assertIsInstance(leaderboard.tournament, ListedTournament)
        self.assertEqual("TRIUMPH", leaderboard.tournament.title)
        self.assertIsNone(leaderboard.tournament.start_date)
        self.assertIsNone(leaderboard.tournament.end_date)
        self.assertIsNone(leaderboard.tournament.duration)
        self.assertEqual(4, leaderboard.tournament.cycle)
        self.assertEqual(0, leaderboard.from_rank)
        self.assertEqual(0, leaderboard.to_rank)
        self.assertEqual(0, len(leaderboard.entries))
        self.assertEqual(0, leaderboard.page)
        self.assertEqual(0, leaderboard.total_pages)
        self.assertEqual(0, leaderboard.results_count)
        self.assertEqual("Endebra", leaderboard.world)

    def test_tournament_leaderboard_from_content_selector(self):
        """Testing parsing the leaderboards's initial page."""
        content = self.load_resource(FILE_TOURNAMENT_LEADERBOARD_SELECTOR)
        leaderboard = TournamentLeaderboard.from_content(content)

        self.assertIsNone(leaderboard)

    def test_tournament_leaderboards_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            TournamentLeaderboard.from_content(content)
    # endregion
