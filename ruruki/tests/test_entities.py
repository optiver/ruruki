# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods

import unittest2
from ruruki.interfaces import IEdge, VertexError, EntityUpdateError
from ruruki.entities import Entity, Edge, Vertex
from ruruki.test_utils import base
from ruruki.graphs import Graph


class TestEntityBase(unittest2.TestCase):
    def setUp(self):
        self.marko = Entity(label="person", name="marko", age=29)

    def test_is_bound(self):
        graph = Graph()
        self.marko.graph = graph  # mock is bound
        self.assertEqual(
            self.marko.is_bound(),
            True
        )

    def test_is_bound_not_bound(self):
        self.assertEqual(
            self.marko.is_bound(),
            False
        )

    def test_remove_property(self):
        self.marko.remove_property("name")
        self.assertDictEqual(
            self.marko.properties,
            {
                "age": 29,
            }
        )

    def test_remove_property_no_such_key(self):
        self.marko.remove_property("surname")
        self.assertDictEqual(
            self.marko.properties,
            {
                "name": "marko",
                "age": 29,
            }
        )

    def test_set_property_kwargs(self):
        self.marko.set_property(surname="McDonald")
        self.assertDictEqual(
            self.marko.properties,
            {
                "name": "marko",
                "surname": "McDonald",
                "age": 29,
            }
        )

    def test_set_property_no_kwargs(self):
        self.assertRaises(
            EntityUpdateError,
            self.marko.set_property,
        )

    def test_set_property_args_and_kwargs(self):
        self.marko.set_property(surname="McDonald", age=30)
        self.assertDictEqual(
            self.marko.properties,
            {
                "name": "marko",
                "surname": "McDonald",
                "age": 30,
            }
        )

    def test_as_dict(self):
        self.assertDictEqual(
            self.marko.as_dict(),
            {
                "id": None,
                "label": "person",
                "properties": {
                    "name": "marko",
                    "age": 29
                },
                "metadata": {},
            },
        )

    def test_get_property_as_attribute(self):
        self.assertEqual(
            self.marko.prop__name,
            "marko"
        )

    def test_get_attribute(self):
        self.assertEqual(
            self.marko.label,
            "person"
        )

    def test_get_attribute_no_propery_or_attr(self):
        self.assertRaises(
            AttributeError,
            self.marko.__getattribute__,
            "prop__bogus"
        )


class TestVertex(base.TestBase, TestEntityBase):
    def setUp(self):
        self.marko = Vertex(label="person", name="marko", age=29)
        super(TestVertex, self).setUp()

    def test_is_bound_not_bound(self):
        self.marko.graph = None
        self.assertEqual(
            self.marko.is_bound(),
            False
        )

    def test_add_in_edge_bound_to_graph(self):
        sue = self.graph.get_or_create_vertex("person", name="sue")
        new_edge = sue.add_in_edge(self.josh, "brother")

        self.assertIsInstance(
            new_edge,
            IEdge
        )

        self.assertIn(
            new_edge,
            sue.in_edges,
        )

        self.assertEqual(
            sue.get_both_edges().sorted(),
            sorted(
                [
                    new_edge
                ]
            )
        )

    def test_add_in_edge_unbound(self):
        marko = Vertex("person", name="marko")
        josh = Vertex("person", name="josh")
        new_edge = marko.add_in_edge(josh, "brother")

        self.assertIsInstance(
            new_edge,
            IEdge
        )

        self.assertIn(
            new_edge,
            marko.in_edges,
        )

        self.assertEqual(
            marko.get_both_edges().sorted(),
            [new_edge],
        )

    def test_add_out_edge_unbound(self):
        marko = Vertex("person", name="marko")
        josh = Vertex("person", name="josh")
        new_edge = marko.add_out_edge(josh, "knows")

        self.assertIsInstance(
            new_edge,
            IEdge
        )

        self.assertIn(
            new_edge,
            marko.out_edges,
        )

        self.assertEqual(
            marko.get_both_edges().sorted(),
            [new_edge],
        )

    def test_add_out_edge(self):
        sue = self.graph.get_or_create_vertex("person", name="sue")
        new_edge = sue.add_out_edge(self.josh, "sister")

        self.assertIsInstance(
            new_edge,
            IEdge
        )

        self.assertIn(
            new_edge,
            sue.out_edges,
        )

        self.assertEqual(
            sue.get_both_edges().sorted(),
            sorted([new_edge]),
        )

    def test_in_edge_count(self):
        self.marko.add_in_edge(self.josh, "brother")
        self.assertEqual(
            self.marko.in_edge_count(),
            len(self.marko.get_in_edges()),
        )

    def test_out_edge_count(self):
        self.assertEqual(
            self.marko.out_edge_count(),
            len(self.marko.get_out_edges()),
        )

    def test_out_edge_count_remove_edge(self):
        edge = self.marko.get_out_edges().all()[0]
        self.marko.remove_edge(edge)
        self.assertEqual(
            self.marko.out_edge_count(),
            len(self.marko.get_out_edges()),
        )

    def test_in_edge_count_remove_edge(self):
        edge = self.josh.get_in_edges().all()[0]
        self.josh.remove_edge(edge)
        self.assertEqual(
            self.marko.in_edge_count(),
            len(self.marko.get_in_edges()),
        )

    def test_remove_edge(self):
        self.marko.remove_edge(self.marko_created_lop)
        self.assertEqual(
            self.marko.get_both_edges().sorted(),
            sorted([self.marko_knows_josh, self.marko_knows_vadas])
        )

    def test_remove_edge_with_unknown_head(self):
        self.assertRaises(
            VertexError,
            self.marko.remove_edge,
            self.josh_created_lop
        )

    def test_get_in_edges(self):
        self.assertEqual(
            self.josh.get_in_edges().sorted(),
            sorted([self.marko_knows_josh])
        )

    def test_get_in_edges_with_property(self):
        self.assertEqual(
            self.josh.get_in_edges(weight=1).sorted(),
            sorted([self.marko_knows_josh])
        )

    def test_get_in_edges_with_property_that_contains(self):
        self.marko_knows_josh.set_property(since="work")
        self.assertEqual(
            self.josh.get_in_edges(since__contains="r").sorted(),
            sorted([self.marko_knows_josh])
        )

    def test_get_in_edges_with_property_that_startswith(self):
        self.marko_knows_josh.set_property(since="work")
        self.assertEqual(
            self.josh.get_in_edges(since__startswith="w").sorted(),
            sorted([self.marko_knows_josh])
        )

    def test_get_in_edges_with_property_that_endswith(self):
        self.marko_knows_josh.set_property(since="work")
        self.assertEqual(
            self.josh.get_in_edges(since__endswith="k").sorted(),
            sorted([self.marko_knows_josh])
        )

    def test_get_out_edges(self):
        self.assertEqual(
            self.josh.get_out_edges().sorted(),
            sorted([self.josh_created_lop, self.josh_created_ripple])
        )

    def test_get_out_edges_with_property(self):
        self.assertEqual(
            self.josh.get_out_edges(weight=1).sorted(),
            sorted([self.josh_created_ripple])
        )

    def test_get_out_edges_with_property_that_contains(self):
        self.josh_created_lop.set_property(since="work")
        self.josh_created_ripple.set_property(since="class")
        self.assertEqual(
            self.josh.get_out_edges(since__contains="o").sorted(),
            sorted([self.josh_created_lop])
        )

    def test_get_out_edges_with_property_that_startswith(self):
        self.josh_created_lop.set_property(since="work")
        self.josh_created_ripple.set_property(since="class")
        self.assertEqual(
            self.josh.get_out_edges(since__startswith="w").sorted(),
            sorted([self.josh_created_lop])
        )

    def test_get_out_edges_with_property_that_endswith(self):
        self.josh_created_lop.set_property(since="work")
        self.josh_created_ripple.set_property(since="class")
        self.assertEqual(
            self.josh.get_out_edges(since__endswith="s").sorted(),
            sorted([self.josh_created_ripple])
        )

    def test_get_both_edges(self):
        self.assertEqual(
            self.josh.get_both_edges().sorted(),
            sorted(
                [
                    self.josh_created_lop,
                    self.josh_created_ripple,
                    self.marko_knows_josh,
                ]
            )
        )

    def test_get_both_edges_with_property(self):
        self.assertEqual(
            self.josh.get_out_edges().sorted(),
            sorted(
                [
                    self.josh_created_lop,
                    self.josh_created_ripple,
                ]
            )
        )

    def test_get_both_edges_with_property_that_contains(self):
        e = self.graph.get_or_create_edge(
            self.marko,
            "friend",
            self.josh,
            since="school",
        )
        x = self.marko.get_in_edges() | self.marko.get_out_edges()
        x.update_index(e, **e.properties)  # pylint: disable=no-member
        self.assertEqual(
            self.marko.get_both_edges(since__contains="o").all(),
            [e],
        )

    def test_get_both_edges_with_property_that_startswith(self):
        e = self.graph.get_or_create_edge(
            self.marko,
            "friend",
            self.josh,
            since="school",
        )
        self.assertEqual(
            self.marko.get_both_edges(since__startswith="s").all(),
            [e],
        )

    def test_get_both_edges_with_property_that_endswith(self):
        e = self.graph.get_or_create_edge(
            self.marko,
            "friend",
            self.josh,
            since="school",
        )
        self.assertEqual(
            self.marko.get_both_edges(since__endswith="l").all(),
            [e],
        )

    def test_get_in_vertices(self):
        self.assertEqual(
            self.josh.get_in_vertices().sorted(),
            sorted([self.marko])
        )

    def test_get_in_vertices_by_label(self):
        self.assertEqual(
            self.josh.get_in_vertices(label="person").sorted(),
            sorted([self.marko])
        )

    def test_get_in_vertices_by_property(self):
        self.assertEqual(
            self.josh.get_in_vertices(name="marko").sorted(),
            sorted([self.marko])
        )

    def test_get_in_vertices_by_property_that_contains(self):
        self.assertEqual(
            self.josh.get_in_vertices(name__contains="r").sorted(),
            sorted([self.marko])
        )

    def test_get_in_vertices_by_property_that_startswith(self):
        self.assertEqual(
            self.josh.get_in_vertices(name__startswith="m").sorted(),
            sorted([self.marko])
        )

    def test_get_in_vertices_by_property_that_endswith(self):
        self.assertEqual(
            self.josh.get_in_vertices(name__endswith="o").sorted(),
            sorted([self.marko])
        )

    def test_get_out_vertices(self):
        self.assertEqual(
            self.josh.get_out_vertices().sorted(),
            sorted([self.lop, self.ripple])
        )

    def test_get_out_vertices_by_label(self):
        self.assertEqual(
            self.josh.get_out_vertices(label="app").sorted(),
            sorted([self.lop, self.ripple])
        )

    def test_get_out_vertices_by_property(self):
        self.assertEqual(
            self.josh.get_out_vertices(name="ripple").sorted(),
            sorted([self.ripple])
        )

    def test_get_out_vertices_by_property_that_contains(self):
        self.assertEqual(
            self.josh.get_out_vertices(name__contains="i").sorted(),
            sorted([self.ripple])
        )

    def test_get_out_vertices_by_property_that_startswith(self):
        self.assertEqual(
            self.josh.get_out_vertices(name__startswith="l").sorted(),
            sorted([self.lop])
        )

    def test_get_out_vertices_by_property_that_endswith(self):
        self.assertEqual(
            self.josh.get_out_vertices(name__endswith="p").sorted(),
            sorted([self.lop])
        )

    def test_get_both_vertices(self):
        self.assertEqual(
            self.josh.get_both_vertices().sorted(),
            sorted([self.marko, self.lop, self.ripple])
        )

    def test_get_both_vertices_by_label(self):
        self.assertEqual(
            self.josh.get_both_vertices(label="person").sorted(),
            sorted([self.marko])
        )

    def test_get_both_vertices_by_property(self):
        self.assertEqual(
            self.josh.get_both_vertices(age=29).sorted(),
            sorted([self.marko])
        )

    def test_get_both_vertices_by_property_that_contains(self):
        self.assertEqual(
            self.josh.get_both_vertices(name__contains="r").sorted(),
            sorted([self.marko, self.ripple])
        )

    def test_get_both_vertices_by_property_that_startswith(self):
        self.assertEqual(
            self.josh.get_both_vertices(name__startswith="m").sorted(),
            sorted([self.marko])
        )

    def test_get_both_vertices_by_property_that_endsswith(self):
        self.assertEqual(
            self.josh.get_both_vertices(name__endswith="o").sorted(),
            sorted([self.marko])
        )

    def test_as_dict(self):
        self.assertDictEqual(
            self.marko.as_dict(),
            {
                "id": 0,
                "label": "person",
                "metadata": {
                    "in_edge_count": 0,
                    "out_edge_count": 3,
                },
                "properties": {
                    "name": "marko",
                    "age": 29,
                },
            }
        )


class TestEdge(base.TestBase, TestEntityBase):
    def setUp(self):
        self.marko = Vertex(label="person", name="marko", age=29)
        super(TestEdge, self).setUp()

    def test_is_bound(self):
        edge = Edge(self.marko, "de-friends", self.josh)
        graph = Graph()
        graph.bind_to_graph(edge)
        self.assertEqual(
            edge.is_bound(),
            True
        )

    def test_is_bound_not_bound(self):
        edge = Edge(self.marko, "de-friends", self.josh)
        self.assertEqual(
            edge.is_bound(),
            False
        )

    def test_remove_property(self):
        self.marko_knows_josh.remove_property("weight")
        self.assertEqual(self.marko_knows_josh.properties.keys(), [])

    def test_get_out_vertex(self):
        self.assertEqual(self.marko_knows_josh.get_out_vertex(), self.josh)

    def test_get_in_vertex(self):
        self.assertEqual(self.marko_knows_josh.get_in_vertex(), self.marko)

    def test_as_dict(self):
        self.assertDictEqual(
            self.marko_knows_josh.as_dict(),
            {
                "id": 3,
                "label": "knows",
                "metadata": {},
                "properties": {
                    "weight": 1,
                },
                "head_id": 0,
                "tail_id": 3,
            }
        )
