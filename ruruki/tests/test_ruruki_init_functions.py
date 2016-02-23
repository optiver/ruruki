# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods

import json
import unittest2
import ruruki
from ruruki import graphs
from ruruki.test_utils import helpers


class TestInitHelperFunctions(unittest2.TestCase):
    def test_get_graph_plugins(self):
        self.assertEqual(
            sorted(ruruki.get_graph_plugins()),
            sorted(["graph", "persistent-graph"]),
        )

    def test_create_graph(self):
        self.assertIsInstance(
            ruruki.create_graph(),
            ruruki.interfaces.IGraph
        )

    def test_create_graph_invalid_plugin(self):
        self.assertRaises(
            ImportError,
            ruruki.create_graph,
            graph_plugin="blah"
        )

    def test_create_graph_with_data(self):
        # reset the counters for a clean run.
        ruruki._VID = 0
        ruruki._EID = 0

        data = helpers.get_test_dump_graph_file_handler()
        graph = ruruki.create_graph(data=data)

        tmp_file = helpers.create_tmp_file_handler()
        graph.dump(tmp_file)

        data.seek(0)
        tmp_file.seek(0)

        # sorted the edges and vertices before comparing the two dicts
        d1 = json.load(data)
        for key in d1:
            d1[key].sort()

        d2 = json.load(tmp_file)
        for key in d2:
            d2[key].sort()

        self.assertDictEqual(
            d1,
            d2,
        )

    def test_create_mem_graph(self):
        self.assertIsInstance(
            ruruki.create_graph(graph_plugin="graph"),
            graphs.Graph,
        )

    def test_create_persistence_graph(self):
        self.assertIsInstance(
            ruruki.create_graph(graph_plugin="persistent-graph"),
            graphs.PersistentGraph,
        )
