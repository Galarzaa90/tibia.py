import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import PvpType, RuleSet, ScoreSet, Tournament

FILE_TOURNAMENT_SIGN_UP = "tournaments/tournament_information_sign_up.txt"
FILE_TOURNAMENT_ARCHIVE = "tournaments/tournament_archive.txt"


class TestTournaments(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_tournament_from_content(self):
        """Testing parsing a tournament's info page"""
        content = self._load_resource(FILE_TOURNAMENT_SIGN_UP)
        tournament = Tournament.from_content(content)
        self.assertEqual(tournament.title, "TRIUMPH")
        self.assertEqual("sign up", tournament.phase)
        self.assertIsInstance(tournament.start_date, datetime.datetime)
        self.assertIsInstance(tournament.end_date, datetime.datetime)
        self.assertEqual(6, len(tournament.worlds))
        self.assertIsInstance(tournament.rule_set, RuleSet)
        self.assertIsInstance(tournament.score_set, ScoreSet)

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
        content = self._load_resource(FILE_TOURNAMENT_ARCHIVE)
        tournament = Tournament.from_content(content)
        self.assertEqual(tournament.title, "GLORY")
        self.assertEqual("ended", tournament.phase)
        self.assertIsInstance(tournament.start_date, datetime.datetime)
        self.assertIsInstance(tournament.end_date, datetime.datetime)
        self.assertEqual(6, len(tournament.worlds))
        self.assertIsInstance(tournament.rule_set, RuleSet)
        self.assertIsInstance(tournament.score_set, ScoreSet)

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
    # endregion
