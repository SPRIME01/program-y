import unittest
import os
import datetime

from programy.brain import Brain
from programy.bot import Bot
from programy.config.sections.brain.brain import BrainConfiguration
from programy.config.sections.bot.bot import BotConfiguration
from programy.config.programy import ProgramyConfiguration
from programy.config.sections.client.console import ConsoleConfiguration
from programy.dialog import Sentence
from programy.config.sections.brain.debugfile import DebugFileConfiguration

class MockBrain(Brain):
    def __init__(self, configuration):
        Brain.__init__(self, configuration)
        self._response = ""

    def ask_question(self, bot, clientid, sentence, srai=False):
        return self._response


class BotTests(unittest.TestCase):

    def test_bot_init_blank(self):
        test_brain = Brain(BrainConfiguration())
        bot = Bot(test_brain, None)

        self.assertIsNone(bot.spell_checker)
        self.assertIsNotNone(bot.brain)
        self.assertIsNotNone(bot.conversations)
        self.assertIsNotNone(bot.license_keys)
        self.assertIsNotNone(bot.prompt)
        self.assertIsNotNone(bot.default_response)
        self.assertIsNotNone(bot.exit_response)
        self.assertIsNotNone(bot.initial_question)
        self.assertFalse(bot.override_properties)
        self.assertIsNotNone(bot.get_version_string)

    def test_bot_init_with_config(self):
        test_brain = Brain(BrainConfiguration())
        bot_config = BotConfiguration()
        bot_config._license_keys          = None
        bot_config._bot_root              = BotConfiguration.DEFAULT_ROOT
        bot_config._prompt                = BotConfiguration.DEFAULT_PROMPT
        bot_config._default_response      = BotConfiguration.DEFAULT_RESPONSE
        bot_config._exit_response         = BotConfiguration.DEFAULT_EXIT_RESPONSE
        bot_config._initial_question      = BotConfiguration.DEFAULT_INITIAL_QUESTION
        bot_config._empty_string          = BotConfiguration.DEFAULT_EMPTY_STRING
        bot_config._override_properties   = BotConfiguration.DEFAULT_OVERRIDE_PREDICATES
        bot_config._max_question_recursion = 1000
        bot_config._max_question_timeout   = 60
        bot_config._max_search_depth       = 100
        bot_config._max_search_timeout     = 60

        bot = Bot(test_brain, bot_config)

        self.assertIsNone(bot.spell_checker)
        self.assertIsNotNone(bot.brain)
        self.assertIsNotNone(bot.conversations)
        self.assertIsNotNone(bot.license_keys)
        self.assertIsNotNone(bot.prompt)
        self.assertIsNotNone(bot.default_response)
        self.assertIsNotNone(bot.exit_response)
        self.assertIsNotNone(bot.initial_question)
        self.assertTrue(bot.override_properties)
        self.assertIsNotNone(bot.get_version_string)

    def test_bot_init_no_spellchecker(self):
        test_brain = Brain(BrainConfiguration())
        bot_config = BotConfiguration()
        bot_config.spelling._classname = None
        bot = Bot(test_brain, bot_config)
        self.assertIsNotNone(bot)

    def test_bot_init_with_invalid_spellchecker(self):
        test_brain = Brain(BrainConfiguration())
        bot_config = BotConfiguration()
        bot_config.spelling._classname = "programy.spelling.checker.SpellingCheckerX"
        bot = Bot(test_brain, bot_config)
        self.assertIsNotNone(bot)

    def test_bot_init_with_spellchecker(self):
        test_brain = Brain(BrainConfiguration())
        bot_config = BotConfiguration()
        bot_config.spelling._classname = "programy.spelling.norvig.NorvigSpellingChecker"
        bot_config.spelling._corpus = os.path.dirname(__file__) + os.sep + "test_corpus.txt"
        bot_config.spelling._check_before = True
        bot_config.spelling._check_and_retry = True
        bot = Bot(test_brain, bot_config)
        self.assertIsNotNone(bot)

        test_sentence = Sentence(bot.brain.tokenizer, "locetion")
        bot.check_spelling_before(test_sentence)
        self.assertIsNotNone(test_sentence)
        self.assertEqual("LOCATION", test_sentence.text())

        test_sentence = Sentence(bot.brain.tokenizer, "locetion")
        response = bot.check_spelling_and_retry("testid", test_sentence)
        self.assertIsNone(response)

    def test_bot_init_no_license_keys(self):
        test_brain = Brain(BrainConfiguration())
        bot_config = BotConfiguration()
        bot_config._license_keys = None
        bot = Bot(test_brain, bot_config)
        self.assertIsNotNone(bot)

    def test_bot_init_with_license_keys(self):
        test_brain = Brain(BrainConfiguration())
        bot_config = BotConfiguration()
        bot_config._license_keys = os.path.dirname(__file__) + os.sep + "test_license.keys"
        bot = Bot(test_brain, bot_config)
        self.assertIsNotNone(bot)

    def test_bot_init_default_brain(self):
        test_brain = Brain(BrainConfiguration())
        bot = Bot(test_brain, BotConfiguration())
        self.assertIsNotNone(bot)
        self.assertIsNotNone(bot.brain)

    def test_bot_init_supplied_brain(self):
        test_brain = Brain(BrainConfiguration())
        bot = Bot(test_brain, BotConfiguration())
        self.assertIsNotNone(bot)
        self.assertIsNotNone(bot.brain)

    def test_bot_defaultresponses(self):
        test_brain = Brain(BrainConfiguration())
        bot = Bot(test_brain, BotConfiguration())
        self.assertIsNotNone(bot)

        self.assertEqual(bot.prompt, ">>> ")
        self.assertEqual(bot.default_response, "")
        self.assertEqual(bot.exit_response, "Bye!")

    def test_bot_with_config(self):
        configuration = ProgramyConfiguration(ConsoleConfiguration())
        self.assertIsNotNone(configuration)
        self.assertIsNotNone(configuration.bot_configuration)
        self.assertIsNotNone(configuration.brain_configuration)

        configuration.bot_configuration.prompt = ":"
        configuration.bot_configuration.default_response = "No answer for that"
        configuration.bot_configuration.exit_response = "See ya!"

        test_brain = Brain(BrainConfiguration())
        test_brain.load(configuration.brain_configuration)

        bot = Bot(test_brain, config=configuration.bot_configuration)
        self.assertIsNotNone(bot)

        self.assertEqual(bot.prompt, ":")
        self.assertEqual(bot.default_response, "No answer for that")
        self.assertEqual(bot.exit_response, "See ya!")

    def test_bot_with_conversation(self):
        test_brain = Brain(BrainConfiguration())
        self.assertIsNotNone(test_brain)

        bot = Bot(test_brain, BotConfiguration())
        self.assertIsNotNone(bot)

        self.assertFalse(bot.has_conversation("testid"))

        response = bot.ask_question("testid", "hello")
        self.assertIsNotNone(response)
        self.assertTrue(bot.has_conversation("testid"))

        response = bot.ask_question("testid", "hello")
        self.assertIsNotNone(response)
        self.assertTrue(bot.has_conversation("testid"))

        response = bot.ask_question("testid2", "hello")
        self.assertIsNotNone(response)
        self.assertTrue(bot.has_conversation("testid2"))

    def test_bot_chat_loop(self):

        test_brain = Brain(BrainConfiguration())
        self.assertIsNotNone(test_brain)
        self.assertIsInstance(test_brain, Brain)

        bot = Bot(test_brain, BotConfiguration())
        self.assertIsNotNone(bot)
        self.assertIsInstance(bot, Bot)
        bot.configuration._default_response = "Sorry, I don't have an answer for that right now"

        response = bot.ask_question("testid", "hello")
        self.assertIsNotNone(response)
        self.assertEqual(response, "Sorry, I don't have an answer for that right now")

        response = bot.ask_question("testid", "hello again")
        self.assertIsNotNone(response)
        self.assertEqual(response, "Sorry, I don't have an answer for that right now")

        response = bot.ask_question("testid", "goodbye")
        self.assertIsNotNone(response)
        self.assertEqual(response, "Sorry, I don't have an answer for that right now")

        conversation = bot.get_conversation("testid")
        self.assertIsNotNone(conversation)

        self.assertEqual(conversation.previous_nth_question(2).sentence(0).text(), "hello")
        self.assertEqual(conversation.previous_nth_question(2).sentence(0).response, "Sorry, I don't have an answer for that right now")

        self.assertEqual(conversation.previous_nth_question(1).sentence(0).text(), "hello again")
        self.assertEqual(conversation.previous_nth_question(1).sentence(0).response, "Sorry, I don't have an answer for that right now")

        self.assertEqual(conversation.previous_nth_question(0).sentence(0).text(), "goodbye")
        self.assertEqual(conversation.previous_nth_question(0).sentence(0).response, "Sorry, I don't have an answer for that right now")

    def test_max_recusion(self):

        test_brain = Brain(BrainConfiguration())
        self.assertIsNotNone(test_brain)

        bot = Bot(test_brain, BotConfiguration())
        self.assertIsNotNone(bot)
        bot.configuration._default_response = "Sorry, I don't have an answer for that right now"
        bot.configuration._max_question_recursion = 0

        with self.assertRaises(Exception):
            bot.ask_question("testid", "hello")

    def test_total_search_time(self):

        test_brain = Brain(BrainConfiguration())
        self.assertIsNotNone(test_brain)

        bot = Bot(test_brain, BotConfiguration())
        self.assertIsNotNone(bot)

        bot._question_start_time = datetime.datetime.now()
        self.assertTrue(bot.total_search_time() >= 0)

        bot.configuration._max_question_timeout = -1
        bot.check_max_timeout()

        bot.configuration._max_question_timeout = 0
        with self.assertRaises(Exception):
            bot.check_max_timeout()

    def test_get_default_response_empty_string(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("", bot.get_default_response("testid"))

    def test_get_default_response_default_response_only(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.default_response = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Default response!", bot.get_default_response("testid"))

    def test_get_default_response_default_response_srai_no_match(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.default_response_srai = "YDEFAULTRESPONSE"
        bot_config.default_response = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Default response!", bot.get_default_response("testid"))

    def test_get_default_response_default_response_srai_match(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = MockBrain(brain_config)
        test_brain._response = "Y DEFAULT RESPONSE"
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.default_response_srai = "YDEFAULTRESPONSE"
        bot_config.default_response = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Y DEFAULT RESPONSE", bot.get_default_response("testid"))

    ############################

    def test_get_initial_question_empty_string(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Hello", bot.get_initial_question("testid"))

    def test_get_initial_question_initial_question_only(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.initial_question = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Default response!", bot.get_initial_question("testid"))

    def test_get_initial_question_initial_question_srai_no_match(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.initial_question_srai = "YDEFAULTRESPONSE"
        bot_config.initial_question = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Default response!", bot.get_initial_question("testid"))

    def test_get_initial_question_initial_question_srai_match(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = MockBrain(brain_config)
        test_brain._response = "Y DEFAULT RESPONSE"
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.initial_question_srai = "YDEFAULTRESPONSE"
        bot_config.initial_question = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Y DEFAULT RESPONSE", bot.get_initial_question("testid"))

    ###################

    def test_get_exit_response_empty_string(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Bye!", bot.get_exit_response("testid"))

    def test_get_exit_response_exit_response_only(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.exit_response = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Default response!", bot.get_exit_response("testid"))

    def test_get_exit_response_exit_response_srai_no_match(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = Brain(brain_config)
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.exit_response_srai = "YDEFAULTRESPONSE"
        bot_config.exit_response = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Default response!", bot.get_exit_response("testid"))

    def test_get_exit_response_exit_response_srai_match(self):

        brain_config = BrainConfiguration()
        self.assertIsNotNone(brain_config)
        test_brain = MockBrain(brain_config)
        test_brain._response = "Y DEFAULT RESPONSE"
        self.assertIsNotNone(test_brain)
        bot_config = BotConfiguration()
        self.assertIsNotNone(bot_config)
        bot_config.exit_response_srai = "YDEFAULTRESPONSE"
        bot_config.exit_response = "Default response!"
        bot = Bot(test_brain,  bot_config)
        self.assertIsNotNone(bot)

        self.assertEquals("Y DEFAULT RESPONSE", bot.get_exit_response("testid"))
