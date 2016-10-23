from .base_case import ChatBotTestCase
from chatterbot.conversation import Statement
from chatterbot.utils.graphs import find_sequence_in_tree
from chatterbot.utils.graphs import get_all_ordered_subsets
from chatterbot.utils.graphs import StatementGraph


class GraphTestCase(ChatBotTestCase):

    def setUp(self):
        super(GraphTestCase, self).setUp()
        from chatterbot.trainers import ListTrainer
        self.chatbot.set_trainer(ListTrainer)
        self.chatbot.train([
            'Hi, how are you?',
            'I am good, how about you?',
            'I am also good.'
        ])
        self.graph = StatementGraph(self.chatbot.storage)

    def test_get_child_nodes(self):
        nodes = self.graph.get_child_nodes(Statement('Hi, how are you?'))

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, 'I am good, how about you?')

    def test_get_parent_nodes(self):
        nodes = self.graph.get_parent_nodes(Statement('I am also good.'))

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, 'I am good, how about you?')

    def test_search_children_for_best_match_exact(self):
        conversations = [
            [
                Statement('Hi, how are you?'),
                Statement('I am good, how about you?'),
                Statement('I am also good.')
            ],
            [
                Statement('Hi, how are you?'),
                Statement('I am great!'),
                Statement('That is good to hear.')
            ]
        ]

        for conversation in conversations:
            self.chatbot.train(list(statement.text for statement in conversation))

        search_node = Statement('I am great!')
        root_nodes = self.graph.get_parent_nodes(search_node)

        value, best_match = self.graph.search_children_for_best_match(search_node, root_nodes)

        self.assertEqual(best_match, search_node)
        self.assertEqual(value, 100)

    def test_check_for_matching_sequence(self):
        pass

    def test_list_close_matches_for_statements(self):
        statements = [
            Statement('Close'),
            Statement('Close.'),
            Statement('Close..'),
            Statement('Hello'),
            Statement('Hello!'),
            Statement('Hello!!!')
        ]

        for statement in statements:
            self.graph.storage.update(statement)

        results = self.graph.list_close_matches_for_statements([
            Statement('Close'),
            Statement('Hello')
        ], max_results=2)

        self.assertEqual(len(results), 4)
        self.assertIn('Close', results[1])
        self.assertIn('Close.', results[0])
        self.assertIn('Hello', results[3])
        self.assertIn('Hello!', results[2])


class SequenceMatchingTestCase(ChatBotTestCase):

    def test_get_all_ordered_subsets(self):
        subsets = list(get_all_ordered_subsets([1, 2, 3]))

        self.assertEqual(len(subsets), 6)
        self.assertIn([1], subsets)
        self.assertIn([2], subsets)
        self.assertIn([3], subsets)
        self.assertIn([1, 2], subsets)
        self.assertIn([2, 3], subsets)
        self.assertIn([1, 2, 3], subsets)


class SubtreeMatchingTestCase(ChatBotTestCase):

    def setUp(self):
        super(SubtreeMatchingTestCase, self).setUp()
        from chatterbot.trainers import ListTrainer
        self.chatbot.set_trainer(ListTrainer)

    def test_exact_match(self):
        sequence = [
            Statement('Hi, how are you?'),
            Statement('I am good, how about you?'),
            Statement('I am also good.')
        ]

        self.chatbot.train([
            sequence[0].text, sequence[1].text, sequence[2].text
        ])

        found = find_sequence_in_tree(self.chatbot.storage, sequence)

        print('found:', found)

        self.assertEqual(len(found), len(sequence))
        self.assertEqual(found[0], sequence[0])
        self.assertEqual(found[1], sequence[1])
        self.assertEqual(found[2], sequence[2])

    def test_no_match(self):
        pass

    def test_close_match(self):
        pass

    def test_partial_sequence_match(self):
        pass

    def test_partial_tree_match(self):
        pass
