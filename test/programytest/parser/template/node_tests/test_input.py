import xml.etree.ElementTree as ET

from programy.parser.template.nodes.base import TemplateNode
from programy.parser.template.nodes.input import TemplateInputNode
from programy.dialog import Conversation, Question

from programytest.parser.base import ParserTestsBaseClass


class MockTemplateInputNode(TemplateInputNode):
    def __init__(self):
        TemplateInputNode.__init__(self)

    def resolve_to_string(self, bot, clientid):
        raise Exception("This is an error")


class TemplateInputNodeTests(ParserTestsBaseClass):

    def test_to_str_defaults(self):
        node = TemplateInputNode()
        self.assertEquals("INPUT", node.to_string())

    def test_to_str_no_defaults(self):
        node = TemplateInputNode(index=2)
        self.assertEquals("INPUT index=2", node.to_string())

    def test_to_xml_defaults(self):
        root = TemplateNode()
        node = TemplateInputNode()
        root.append(node)

        xml = root.xml_tree(self._bot, self._clientid)
        self.assertIsNotNone(xml)
        xml_str = ET.tostring(xml, "utf-8").decode("utf-8")
        self.assertEqual("<template><input /></template>", xml_str)

    def test_to_xml_no_defaults(self):
        root = TemplateNode()
        node = TemplateInputNode(index=3)
        root.append(node)

        xml = root.xml_tree(self._bot, self._clientid)
        self.assertIsNotNone(xml)
        xml_str = ET.tostring(xml, "utf-8").decode("utf-8")
        self.assertEqual('<template><input index="3" /></template>', xml_str)

    def test_resolve_with_defaults(self):
        root = TemplateNode()
        self.assertIsNotNone(root)
        self.assertIsNotNone(root.children)
        self.assertEqual(len(root.children), 0)

        node = TemplateInputNode()
        self.assertIsNotNone(node)

        root.append(node)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(0, node.index)

        conversation = Conversation("testid", self._bot)

        question = Question.create_from_text(self._bot.brain.tokenizer, "Hello world")
        question.current_sentence()._response = "Hello matey"
        conversation.record_dialog(question)

        self._bot._conversations["testid"] = conversation

        response = root.resolve(self._bot, "testid")
        self.assertIsNotNone(response)
        self.assertEqual(response, "Hello world")

    def test_resolve_no_defaults(self):
        root = TemplateNode()
        self.assertIsNotNone(root)
        self.assertIsNotNone(root.children)
        self.assertEqual(len(root.children), 0)

        node = TemplateInputNode(index=1)
        self.assertIsNotNone(node)

        root.append(node)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(1, node.index)

        conversation = Conversation("testid", self._bot)

        question = Question.create_from_text(self._bot.brain.tokenizer, "Hello world")
        question.current_sentence()._response = "Hello matey"
        conversation.record_dialog(question)

        question = Question.create_from_text(self._bot.brain.tokenizer, "How are you. Are you well")
        question.current_sentence()._response = "Fine thanks"
        conversation.record_dialog(question)

        self._bot._conversations["testid"] = conversation

        response = root.resolve(self._bot, "testid")
        self.assertIsNotNone(response)
        self.assertEqual(response, "How are you")

    def test_resolve_no_sentence(self):
        root = TemplateNode()
        self.assertIsNotNone(root)
        self.assertIsNotNone(root.children)
        self.assertEqual(len(root.children), 0)

        node = TemplateInputNode(index=3)
        self.assertIsNotNone(node)

        root.append(node)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(3, node.index)

        conversation = Conversation("testid", self._bot)

        question = Question.create_from_text(self._bot.brain.tokenizer, "Hello world")
        question.current_sentence()._response = "Hello matey"
        conversation.record_dialog(question)

        question = Question.create_from_text(self._bot.brain.tokenizer, "How are you. Are you well")
        question.current_sentence()._response = "Fine thanks"
        conversation.record_dialog(question)

        self._bot._conversations["testid"] = conversation

        response = root.resolve(self._bot, "testid")
        self.assertIsNotNone(response)
        self.assertEqual(response, "")

    def test_node_exception_handling(self):
        root = TemplateNode()
        node = MockTemplateInputNode()
        root.append(node)

        result = root.resolve(self._bot, self._clientid)
        self.assertIsNotNone(result)
        self.assertEquals("", result)