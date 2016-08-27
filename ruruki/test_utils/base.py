# pylint: disable=too-many-instance-attributes
"""
Base Test setup.
"""
import unittest
from ruruki import graphs
from ruruki.test_utils import helpers


class TestBase(unittest.TestCase):
    """
    Base test class.
    """
    def setUp(self):
        self.graph = graphs.Graph()
        self.graph.load(helpers.get_test_dump_graph_file_handler())

        # See test_utils/small_people_graph.dump
        # get and set each of the vertices and edges for later use.
        self.marko = self.graph.get_vertices(name="marko").all()[0]
        self.vadas = self.graph.get_vertices(name="vadas").all()[0]
        self.lop = self.graph.get_vertices(name="lop").all()[0]
        self.josh = self.graph.get_vertices(name="josh").all()[0]
        self.ripple = self.graph.get_vertices(name="ripple").all()[0]
        self.peter = self.graph.get_vertices(name="peter").all()[0]

        self.peter_created_lop = self.graph.get_edges(
            self.peter, "created", self.lop
        ).all()[0]

        self.josh_created_lop = self.graph.get_edges(
            self.josh, "created", self.lop
        ).all()[0]

        self.marko_created_lop = self.graph.get_edges(
            self.marko, "created", tail=self.lop
        ).all()[0]

        self.marko_knows_josh = self.graph.get_edges(
            self.marko, "knows", self.josh
        ).all()[0]

        self.marko_knows_vadas = self.graph.get_edges(
            self.marko, "knows", self.vadas
        ).all()[0]

        self.josh_created_ripple = self.graph.get_edges(
            self.josh, "created", self.ripple
        ).all()[0]
