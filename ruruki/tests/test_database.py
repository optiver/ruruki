# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines

import json
import os
import shutil
import tempfile
import unittest2
from ruruki import interfaces
from ruruki.graphs import Graph, PersistentGraph
from ruruki.entities import Entity, Edge, Vertex
from ruruki.entities import PersistentVertex, PersistentEdge
from ruruki.test_utils import base, helpers


class TestGraph(base.TestBase):
    def test_dump(self):
        self.maxDiff = None
        tmp_file = helpers.create_tmp_file_handler()
        self.graph.dump(tmp_file)
        tmp_file.seek(0)

        # sorted the edges and vertices before comparing the two dicts
        loaded_temp = json.load(tmp_file)
        for key in loaded_temp:
            loaded_temp[key].sort()

        loaded_dump = json.load(helpers.get_test_dump_graph_file_handler())
        for key in loaded_dump:
            loaded_dump[key].sort()

        self.assertDictEqual(
            loaded_temp,
            loaded_dump,
        )

    def test_load(self):
        graph = Graph()
        fh = helpers.get_test_dump_graph_file_handler()
        graph.load(fh)

        marko = self.graph.get_vertex(0)
        vadas = self.graph.get_vertex(1)
        lop = self.graph.get_vertex(2)
        josh = self.graph.get_vertex(3)
        ripple = self.graph.get_vertex(4)
        peter = self.graph.get_vertex(5)

        peter_created_lop = self.graph.get_edge(0)
        josh_created_lop = self.graph.get_edge(1)
        marko_created_lop = self.graph.get_edge(2)
        marko_knows_josh = self.graph.get_edge(3)
        marko_knows_vadas = self.graph.get_edge(4)
        josh_created_ripple = self.graph.get_edge(5)

        # The containers that the graph uses checks the attributes on
        # vertices and edges and not the `id` from the python built-in
        # function.
        self.assertIn(marko, self.graph)
        self.assertEqual(marko.label, "person")
        self.assertEqual(marko.ident, 0)
        self.assertDictEqual(
            marko.properties,
            {
                "age": 29,
                "name": "marko",
            },
        )

        self.assertIn(vadas, self.graph)
        self.assertEqual(vadas.label, "person")
        self.assertEqual(vadas.ident, 1)
        self.assertDictEqual(
            vadas.properties,
            {
                "age": 27,
                "name": "vadas",
            },
        )

        self.assertIn(lop, self.graph)
        self.assertEqual(lop.label, "app")
        self.assertEqual(lop.ident, 2)
        self.assertDictEqual(
            lop.properties,
            {
                "lang": "java",
                "name": "lop",
            },
        )

        self.assertIn(josh, self.graph)
        self.assertEqual(josh.label, "person")
        self.assertEqual(josh.ident, 3)
        self.assertDictEqual(
            josh.properties,
            {
                "age": 32,
                "name": "josh",
            },
        )

        self.assertIn(ripple, self.graph)
        self.assertEqual(ripple.label, "app")
        self.assertEqual(ripple.ident, 4)
        self.assertDictEqual(
            ripple.properties,
            {
                "lang": "java",
                "name": "ripple",
            },
        )

        self.assertIn(peter, self.graph)
        self.assertEqual(peter.label, "person")
        self.assertEqual(peter.ident, 5)
        self.assertDictEqual(
            peter.properties,
            {
                "age": 35,
                "name": "peter",
            },
        )

        self.assertIn(peter_created_lop, self.graph)
        self.assertEqual(
            peter_created_lop.label, "created"
        )
        self.assertEqual(
            peter_created_lop.head, peter
        )
        self.assertEqual(
            peter_created_lop.tail, lop
        )
        self.assertDictEqual(
            peter_created_lop.properties,
            {
                "weight": 0.2
            }
        )

        self.assertIn(josh_created_lop, self.graph)
        self.assertEqual(
            josh_created_lop.label, "created"
        )
        self.assertEqual(
            josh_created_lop.head, josh
        )
        self.assertEqual(
            josh_created_lop.tail, lop
        )
        self.assertDictEqual(
            josh_created_lop.properties,
            {
                "weight": 0.4
            }
        )

        self.assertIn(marko_created_lop, self.graph)
        self.assertEqual(
            marko_created_lop.label, "created"
        )
        self.assertEqual(
            marko_created_lop.head, marko
        )
        self.assertEqual(
            marko_created_lop.tail, lop
        )
        self.assertDictEqual(
            marko_created_lop.properties,
            {
                "weight": 0.4
            }
        )

        self.assertIn(marko_knows_josh, self.graph)
        self.assertEqual(
            marko_knows_josh.label, "knows"
        )
        self.assertEqual(
            marko_knows_josh.head, marko
        )
        self.assertEqual(
            marko_knows_josh.tail, josh
        )
        self.assertDictEqual(
            marko_knows_josh.properties,
            {
                "weight": 1
            }
        )

        self.assertIn(marko_knows_vadas, self.graph)
        self.assertEqual(
            marko_knows_vadas.label, "knows"
        )
        self.assertEqual(
            marko_knows_vadas.head, marko
        )
        self.assertEqual(
            marko_knows_vadas.tail, vadas
        )
        self.assertDictEqual(
            marko_knows_vadas.properties,
            {
                "weight": 0.5
            }
        )

        self.assertIn(josh_created_ripple, self.graph)
        self.assertEqual(
            josh_created_ripple.label, "created"
        )
        self.assertEqual(
            josh_created_ripple.head, josh
        )
        self.assertEqual(
            josh_created_ripple.tail, ripple
        )
        self.assertDictEqual(
            josh_created_ripple.properties,
            {
                "weight": 1
            }
        )

    def test_append_vertex(self):
        node = Vertex(label="NODE")
        self.graph.append_vertex(node)
        self.assertEqual(node.ident, self.graph._id_tracker.vid - 1)
        self.assertIn(node, self.graph)
        self.assertEqual(node.is_bound(), True)

    def test_append_vertex_with_ident_set(self):
        node = Vertex(label="NODE")
        node.ident = 0
        self.assertRaises(
            interfaces.EntityIDError,
            self.graph.append_vertex,
            node
        )

    def test_append_vertex_that_already_belongs_to_the_graph(self):
        node = self.graph.get_vertex(0)
        node_appended = self.graph.append_vertex(node)
        self.assertIs(node_appended, node)

    def test_append_vertex_bound_to_another_graph(self):
        g = Graph()
        node = g.add_vertex()
        self.assertRaises(
            interfaces.DatabaseException,
            self.graph.append_vertex,
            node
        )

    def test_append_edge(self):
        node1 = Vertex(label="NODE")
        node2 = Vertex(label="NODE")
        edge = Edge(node1, "knows", node2)
        self.graph.append_edge(edge)

        self.assertEqual(edge.ident, self.graph._id_tracker.eid - 1)
        self.assertIn(edge, self.graph)
        self.assertEqual(edge.is_bound(), True)

    def test_append_edge_with_ident_set(self):
        node1 = Vertex(label="NODE")
        node2 = Vertex(label="NODE")
        edge = Edge(node1, "knows", node2)
        edge.ident = 0
        self.assertRaises(
            interfaces.DatabaseException,
            self.graph.append_edge,
            edge
        )

    def test_append_edge_that_already_belongs_to_the_graph(self):
        edge = self.graph.get_edge(0)
        edge_appended = self.graph.append_edge(edge)
        self.assertIs(edge_appended, edge)

    def test_append_edge_bound_to_another_graph(self):
        g = Graph()
        node1 = g.add_vertex(label="NODE")
        node2 = g.add_vertex(label="NODE")
        edge = g.add_edge(node1, "knows", node2)

        # hack for testing only
        node1.ident = None
        node2.ident = None
        node1.graph = None
        node2.graph = None

        self.assertRaises(
            interfaces.DatabaseException,
            self.graph.append_edge,
            edge
        )

    def test_add_vertex(self):
        node = self.graph.add_vertex(label="NODE")
        self.assertEqual(node.label, "NODE")
        self.assertIsInstance(node, interfaces.IVertex)
        self.assertIn(node, self.graph)

    def test_add_vertex_set_id(self):
        last = max(each.ident for each in self.graph.get_vertices())
        node = self.graph.add_vertex(label="NODE")
        self.assertEqual(node.ident, last + 1)

    def test_get_vertex(self):
        self.assertEqual(self.graph.get_vertex(1), self.vadas)

    def test_get_verticies(self):
        self.assertEqual(
            self.graph.get_vertices().sorted(),
            sorted(
                [
                    self.marko, self.vadas, self.lop,
                    self.josh, self.peter, self.ripple,
                ]
            ),
        )

    def test_get_verticies_by_label(self):
        self.assertEqual(
            sorted(self.graph.get_vertices(label="app")),
            sorted([self.lop, self.ripple]),
        )

    def test_get_verticies_by_unknown_label(self):
        self.assertEqual(
            sorted(self.graph.get_vertices(label="UNKNOWN")),
            [],
        )

    def test_get_verticies_with_property(self):
        self.assertEqual(
            sorted(self.graph.get_vertices(name="josh")),
            [self.josh],
        )

    def test_get_verticies_with_contains(self):
        self.assertEqual(
            sorted(self.graph.get_vertices(name__contains="s")),
            sorted([self.vadas, self.josh]),
        )

    def test_get_verticies_where_startswith(self):
        self.assertEqual(
            sorted(self.graph.get_vertices(name__startswith="m")),
            sorted([self.marko]),
        )

    def test_get_verticies_where_endswith(self):
        self.assertEqual(
            sorted(self.graph.get_vertices(name__endswith="o")),
            sorted([self.marko]),
        )

    def test_remove_vertex(self):
        # First we need to remove all the edges before we can remove the
        # vertex.
        edges = self.lop.get_both_edges().all()
        for e in edges:
            self.graph.remove_edge(e)
        self.graph.remove_vertex(self.lop)
        self.assertNotIn(self.lop, self.graph)

    def test_remove_vertex_that_has_edges(self):
        self.assertRaises(
            interfaces.VertexBoundByEdges,
            self.graph.remove_vertex,
            self.lop
        )

    def test_add_edge(self):
        new_edge = self.graph.add_edge(self.marko, "FRIENDS", self.peter)
        self.assertEqual(new_edge.label, "FRIENDS")
        self.assertEqual(new_edge.head, self.marko)
        self.assertEqual(new_edge.tail, self.peter)
        self.assertIsInstance(new_edge, interfaces.IEdge)
        self.assertIn(new_edge, self.graph)

    def test_add_edge_check_id_are_set(self):
        last = max(each.ident for each in self.graph.get_edges())
        new_edge = self.graph.add_edge(self.marko, "FRIENDS", self.peter)
        self.assertEqual(new_edge.ident, last + 1)  # +1 since the last edge

    def test_get_edge(self):
        self.assertEqual(self.graph.get_edge(1), self.josh_created_lop)

    def test_get_edges(self):
        self.assertEqual(
            sorted(self.graph.get_edges()),
            sorted(
                [
                    self.peter_created_lop,
                    self.josh_created_lop,
                    self.marko_created_lop,
                    self.marko_knows_josh,
                    self.marko_knows_vadas,
                    self.josh_created_ripple,
                ]
            ),
        )

    def test_get_edges_by_with_head(self):
        self.assertEqual(
            sorted(self.graph.get_edges(head=self.marko)),
            sorted(
                [
                    self.marko_created_lop,
                    self.marko_knows_josh,
                    self.marko_knows_vadas,
                ]
            ),
        )

    def test_get_edges_by_with_tail(self):
        self.assertEqual(
            sorted(self.graph.get_edges(tail=self.lop)),
            sorted(
                [
                    self.marko_created_lop,
                    self.josh_created_lop,
                    self.peter_created_lop,
                ]
            ),
        )

    def test_get_edges_by_label(self):
        self.assertEqual(
            sorted(self.graph.get_edges(label="knows")),
            sorted([self.marko_knows_josh, self.marko_knows_vadas])
        )

    def test_get_edges_by_unknown_label(self):
        self.assertEqual(
            sorted(self.graph.get_edges(label="UNKNOWN")),
            [],
        )

    def test_get_edges_with_property(self):
        self.assertEqual(
            sorted(self.graph.get_edges(weight=0.2)),
            sorted([self.peter_created_lop]),
        )

    def test_get_edges_property_that_contains(self):
        marko_friend_josh = self.graph.get_or_create_edge(
            self.marko, "friend", self.josh,
            since="work"
        )
        self.assertEqual(
            self.graph.get_edges(since__contains="o").sorted(),
            sorted([marko_friend_josh]),
        )

    def test_get_edges_property_that_startswith(self):
        marko_friend_josh = self.graph.get_or_create_edge(
            self.marko, "friend", self.josh,
            since="work"
        )
        self.assertEqual(
            self.graph.get_edges(since__startswith="w").sorted(),
            sorted([marko_friend_josh]),
        )

    def test_get_edges_property_that_endswith(self):
        marko_friend_josh = self.graph.get_or_create_edge(
            self.marko, "friend", self.josh,
            since="work"
        )
        self.assertEqual(
            self.graph.get_edges(since__endswith="k").sorted(),
            sorted([marko_friend_josh]),
        )

    def test_remove_edge(self):
        self.graph.remove_edge(self.marko_created_lop)
        self.assertNotIn(self.marko_created_lop, self.graph)

    def test_contains_unsupported_types(self):
        unsupported = "unsupported object"
        self.assertRaises(
            TypeError,
            self.graph.__contains__,
            unsupported,
        )

    def test_contains_vertex(self):
        self.assertEqual(self.graph.__contains__(self.marko), True)

    def test_contains_vertex_not_found(self):
        v = Vertex("person", name="not_in_graph")
        self.assertEqual(self.graph.__contains__(v), False)

    def test_contains_edge(self):
        self.assertEqual(self.graph.__contains__(self.marko_knows_josh), True)

    def test_contains_edge_not_found(self):
        e = Edge(self.marko, "friend", self.josh)
        self.assertEqual(self.graph.__contains__(e), False)

    def test_set_property(self):
        self.graph.set_property(self.marko, new_prop="prop_value")

        self.assertDictEqual(
            self.marko.properties,
            {
                "name": "marko",
                "new_prop": "prop_value",
                "age": 29,
            }
        )

        self.assertEqual(
            sorted(self.graph.vertices.get_indexes()),
            sorted(
                [
                    ("app", "lang"),
                    ("app", "name"),
                    ("person", "age"),
                    ("person", "name"),
                    ("person", "new_prop"),
                ]
            ),
        )

    def test_set_property_on_an_unknown_entity(self):
        dog = Vertex("dog", name="socks")
        self.assertRaises(
            interfaces.UnknownEntityError,
            self.graph.set_property,
            dog,
            name="spot"
        )

    def test_set_property_with_empty_prop_index(self):
        dog = self.graph.get_or_create_vertex("dog", name="socks")
        self.graph.add_vertex_constraint("dog", "color")
        self.graph.set_property(dog, color="brown")
        self.assertDictEqual(
            dog.properties,
            {
                "name": "socks",
                "color": "brown",
            }
        )

    def test_set_property_indexed_entity_property(self):
        self.graph.get_or_create_vertex("dog", name="socks")
        self.graph.add_vertex_constraint("dog", "color")
        # add in another dog that would be indexed.
        self.graph.get_or_create_vertex("dog", name="patch", color="black")
        spot = self.graph.get_or_create_vertex(
            "dog", name="spot", color="white"
        )
        self.graph.set_property(spot, color="brown")
        self.assertDictEqual(
            spot.properties,
            {
                "name": "spot",
                "color": "brown",
            }
        )

    def test_entity_set_property_constraint_violation(self):
        self.graph.add_vertex_constraint("person", "surname")
        self.graph.get_or_create_vertex("person", name="John", surname="Doe")
        jane = self.graph.get_or_create_vertex("person", name="Jane")
        self.assertRaises(
            interfaces.ConstraintViolation,
            jane.set_property,
            surname="Doe",
        )

    def test_set_property_on_edge(self):
        self.graph.set_property(self.marko_knows_josh, new_prop="prop_value")

        self.assertDictEqual(
            self.marko_knows_josh.properties,
            {
                "new_prop": "prop_value",
                "weight": 1,
            }
        )

    def test_set_property_unknown_type(self):
        some_entity = Entity("SomeEntity")
        self.assertRaises(
            TypeError,
            self.graph.set_property,
            some_entity,
            name="should_not_be_set"
        )

        self.assertDictEqual(
            some_entity.properties,
            {},
        )

    def test_get_vertex_constraints(self):
        self.assertEqual(
            sorted(self.graph.get_vertex_constraints()),
            sorted(
                [
                    ("app", "name"),
                    ("person", "name"),
                ]
            ),
        )

    def test_add_vertex_constraint(self):
        current_constraints = self.graph.get_vertex_constraints()
        self.graph.add_vertex_constraint("dog", "name")
        self.assertEqual(
            sorted(self.graph.get_vertex_constraints()),
            sorted(
                [
                    ("app", "name"),
                    ("dog", "name"),
                    ("person", "name"),
                ]
            ),
        )
        self.assertNotIn(
            ("dog", "name"),
            current_constraints,
        )

    def test_bind_to_graph(self):
        sue = Vertex(100, name="Sue")
        self.graph.bind_to_graph(sue)
        self.assertIs(
            sue.graph,
            self.graph
        )

    def test_bind_to_graph_unsupported_type(self):
        sue = Entity(100, name="Sue")
        self.assertRaises(
            interfaces.UnknownEntityError,
            self.graph.bind_to_graph,
            sue
        )


class TestGraphGetOrCreateVertices(base.TestBase):
    def test_add_new(self):
        vertices = self.graph.get_vertices().all()
        v = self.graph.get_or_create_vertex("person", name="mock_vertex")
        self.assertIn(v, self.graph)
        self.assertNotIn(v, vertices)

    def test_add_new_constraint_prop_key_not_in_kwargs(self):
        vertices = self.graph.get_vertices().all()
        self.graph.add_vertex_constraint("person", "surname")
        v = self.graph.get_or_create_vertex("person", name="mock_vertex")
        self.assertIn(v, self.graph)
        self.assertNotIn(v, vertices)

    def test_add_new_constraint_prop_key_in_kwargs(self):
        self.graph.add_vertex_constraint("person", "name")
        self.graph.add_vertex_constraint("person", "surname")
        vertices = self.graph.get_vertices().all()
        v = self.graph.get_or_create_vertex("person", surname="Marko")
        self.assertNotIn(v, vertices)

    def test_multi_add_new_no_constraints(self):
        # clear out the current constraints loaded from the dump
        self.graph._vconstraints = {}
        v = self.graph.get_or_create_vertex("person", name="mock_vertex")
        vertices = self.graph.get_vertices().all()
        dup = self.graph.get_or_create_vertex(
            "person",
            name="mock_vertex",
            age=30,
        )
        self.assertIn(dup, self.graph)
        self.assertNotIn(dup, vertices)
        self.assertNotEqual(dup, v)

    def test_multi_add_new_with_constraints(self):
        # add in a person name constraint
        self.graph.add_vertex_constraint("person", "name")
        v = self.graph.get_or_create_vertex("person", name="mock_vertex")
        vertices = self.graph.get_vertices().all()
        dup = self.graph.get_or_create_vertex(
            "person",
            name="mock_vertex",
            age=30,
        )
        self.assertIn(dup, self.graph)
        self.assertIn(dup, vertices)
        self.assertEqual(dup, v)

    def test_multi_add_new_with_constraints_unique_vertices_by_name(self):
        # add in a person name constraint
        self.graph.add_vertex_constraint("person", "name")
        v = self.graph.get_or_create_vertex(
            "person",
            name="mock_vertex",
        )

        v1 = self.graph.get_or_create_vertex(
            "person",
            name="mock_vertex1",
        )

        self.assertIn(v, self.graph)
        self.assertIn(v1, self.graph)
        self.assertNotEqual(v, v1)

    def test_more_then_one_found_with_no_constraints(self):
        self.graph.add_vertex(
            "person",
            name="mock_vertex",
            age=20
        )

        self.graph.add_vertex(
            "person",
            name="mock_vertex2",
            age=20
        )

        self.assertRaises(
            interfaces.MultipleFoundExpectedOne,
            self.graph.get_or_create_vertex,
            "person", age=20
        )

    def test_no_constraints_filter_found_one_vertex(self):
        graph = Graph()
        graph.add_vertex("dog", name="rex")

        spot = graph.add_vertex("dog", name="spot")
        spot2 = graph.get_or_create_vertex("dog", name="spot")

        self.assertEqual(
            spot2,
            spot,
        )

    def test_no_label_no_kwargs(self):
        self.assertEqual(
            self.graph.get_or_create_vertex(),
            None
        )


class TestGraphGetOrCreateEdges(base.TestBase):
    def test_add_edge_with_head_tuple(self):
        vertices = self.graph.get_vertices("person", name="sue")
        edge = self.graph.get_or_create_edge(
            ("person", {"name": "sue"}),
            "knowns",
            self.marko,
        )

        self.assertIn(
            edge,
            self.graph
        )

        sue = self.graph.get_vertices("person", name="sue").all()[0]
        self.assertNotIn(
            sue,
            vertices,
        )

        self.assertIn(
            sue,
            self.graph,
        )

    def test_add_edge_with_tail_tuple(self):
        vertices = self.graph.get_vertices("person", name="sue")
        edge = self.graph.get_or_create_edge(
            self.marko,
            "knowns",
            ("person", {"name": "sue"}),
        )

        self.assertIn(
            edge,
            self.graph
        )

        sue = self.graph.get_vertices("person", name="sue").all()[0]
        self.assertNotIn(
            sue,
            vertices,
        )

        self.assertIn(
            sue,
            self.graph,
        )

    def test_add_edge_constraint_violation(self):
        self.assertRaises(
            interfaces.ConstraintViolation,
            self.graph.add_edge,
            self.marko,
            "knows",
            self.josh,
            place="work",
        )

    def test_edge_already_indexed(self):
        self.assertEqual(
            self.graph.get_or_create_edge(self.marko, "knows", self.josh),
            self.marko_knows_josh,
        )


def create_graph_mock_path():
    """
    Create the folllowing

    path
       |_ vertices
       |     |_ constraints.json (file)
       |     |_ label
       |     |     |_ 0
       |     |        |_ properties.json (file)
       |     |        |_ in-edges
       |     |        |     |_ 0 -> ../../../../edges/label/0 (symlink)
       |     |        |_ out-edges
       |     |              |_
       |     |
       |     |_ label
       |         |_ 1
       |              |_ properties.json (file)
       |              |_ in-edges
       |              |     |_
       |              |_ out-edges
       |                    |_ 0 -> ../../../../edges/label/0 (symlink)
       |
       |_ edges
             |_ constraints.json
             |_ label
                   |
                   |_0
                     |_ properties.json (file)
                     |_ head
                     |   |_ ../../../vertices/0 (symlik)
                     |_ tail
                         |_ ../../../vertices/1 (symlik)
    """
    path = tempfile.mkdtemp()
    vertices_path = os.path.join(path, "vertices")
    os.makedirs(vertices_path)
    edges_path = os.path.join(path, "edges")
    os.makedirs(edges_path)

    # create constraints
    open(os.path.join(edges_path, "constraints.json"), "w").close()
    json.dump(
        [
            {
                "label": "person",
                "key": "name",
            }
        ],
        open(os.path.join(vertices_path, "constraints.json"), "w"),
        indent=4,
    )

    # create two vertices
    marko_path = os.path.join(vertices_path, "person", "0")
    marko_in_edges_path = os.path.join(marko_path, "in-edges")
    marko_out_edges_path = os.path.join(marko_path, "out-edges")
    os.makedirs(marko_path)
    os.makedirs(marko_in_edges_path)
    os.makedirs(marko_out_edges_path)
    json.dump(
        {"name": "Marko"},
        open(os.path.join(marko_path, "properties.json"), "w"),
        indent=4,
    )

    josh_path = os.path.join(vertices_path, "person", "1")
    josh_in_edges_path = os.path.join(josh_path, "in-edges")
    josh_out_edges_path = os.path.join(josh_path, "out-edges")
    os.makedirs(josh_path)
    os.makedirs(josh_in_edges_path)
    os.makedirs(josh_out_edges_path)
    json.dump(
        {"name": "Josh"},
        open(os.path.join(josh_path, "properties.json"), "w"),
        indent=4,
    )

    # create edge between the vertices
    edge_path = os.path.join(edges_path, "knows", "0")
    head_path = os.path.join(edge_path, "head")
    tail_path = os.path.join(edge_path, "tail")
    os.makedirs(edge_path)
    os.makedirs(head_path)
    os.makedirs(tail_path)
    json.dump(
        {"since": "school"},
        open(os.path.join(edge_path, "properties.json"), "w"),
        indent=4,
    )

    os.symlink(marko_path, os.path.join(head_path, "0"))
    os.symlink(josh_path, os.path.join(tail_path, "1"))

    return path


class TestPersistentGraph(unittest2.TestCase):
    def setUp(self):
        path = tempfile.mkdtemp()
        self.graph = PersistentGraph(path)

    def test_import_from_path(self):
        path = create_graph_mock_path()
        graph = PersistentGraph(path)

        # check that the paths are setup correctly
        self.assertEqual(graph.path, path)

        self.assertEqual(
            graph.vertices_path,
            os.path.join(path, "vertices")
        )
        self.assertEqual(
            graph.vertices_constraints_path,
            os.path.join(path, "vertices", "constraints.json")
        )

        self.assertEqual(
            graph.edges_path,
            os.path.join(path, "edges")
        )

        # check that the constraints have been imported
        self.assertEqual(
            sorted(graph.get_vertex_constraints()),
            [("person", "name")],
        )

    def test_import_from_empty_path_with_auto_create(self):
        path = tempfile.mkdtemp()
        graph = PersistentGraph(path, auto_create=True)

        # check the top level directories have been created.
        self.assertEqual(
            sorted(os.listdir(graph.path)),
            sorted([".lock", "vertices", "edges"]),
        )

        # check the vertices directory and other files have been created.
        self.assertEqual(
            sorted(os.listdir(graph.vertices_path)),
            sorted(["constraints.json"]),
        )

    def test_import_from_empty_path_without_auto_create(self):
        path = tempfile.mkdtemp()
        self.assertRaises(
            IOError,
            PersistentGraph,
            path,
            auto_create=False
        )

    def test_import_from_path_auto_create_has_edges_missing_vertices(self):
        path = create_graph_mock_path()
        shutil.rmtree(
            os.path.join(
                path,
                "vertices",
            )
        )

        self.assertRaises(
            OSError,
            PersistentGraph,
            path,
            auto_create=True
        )

    def test_import_from_path_auto_create_has_no_missing_dirs(self):
        path = create_graph_mock_path()
        graph = PersistentGraph(path, auto_create=True)
        self.assertEqual(len(graph.vertices), 2)
        self.assertEqual(len(graph.edges), 1)

    def test_import_from_empty_path_data_written_new_empty_path(self):
        # this is just to check that data is written to the empty
        # path that was provided and automatically setup.
        path = tempfile.mkdtemp()
        graph = PersistentGraph(path, auto_create=True)

        marko = graph.get_or_create_vertex("person", name="Marko")
        spot = graph.get_or_create_vertex("dog", name="Spot")
        graph.get_or_create_edge(marko, "owns", spot)


        # Just check a couple things, because we will assume that if
        # we have some data in the right place, all the reset should be
        # there too.

        self.assertEqual(
            sorted(os.listdir(graph.vertices_path)),
            sorted(["constraints.json", "person", "dog"]),
        )

        self.assertEqual(
            sorted(os.listdir(marko.path)),
            sorted(["in-edges", "out-edges", "properties.json"]),
        )

        self.assertEqual(
            sorted(os.listdir(graph.edges_path)),
            sorted(["owns"]),
        )

    def test_import_with_vertices_missing_properties_file(self):
        path = create_graph_mock_path()
        os.remove(
            os.path.join(
                path,
                "vertices",
                "person",
                "0",
                "properties.json"
            )
        )
        graph = PersistentGraph(path)
        vertex = graph.get_vertex(0)
        self.assertDictEqual(vertex.properties, {})

    def test_import_from_path_missing_vertices_directory(self):
        path = tempfile.mkdtemp()
        os.makedirs(os.path.join(path, "edges"))
        self.assertRaises(
            IOError,
            PersistentGraph,
            path,
            auto_create=False,
        )

    def test_import_from_path_missing_vertices_constraints(self):
        path = tempfile.mkdtemp()
        os.makedirs(os.path.join(path, "vertices"))
        os.makedirs(os.path.join(path, "edges"))
        self.assertRaises(
            IOError,
            PersistentGraph,
            path
        )

    def test_import_from_path_missing_edges_directory(self):
        path = tempfile.mkdtemp()
        os.makedirs(os.path.join(path, "vertices"))
        fh = open(os.path.join(path, "vertices", "constraints.json"), "w")
        fh.write("{}")
        fh.close()
        self.assertRaises(
            OSError,
            PersistentGraph,
            path
        )

    def test_import_from_path_loaded_edges(self):
        path = create_graph_mock_path()
        graph = PersistentGraph(path)

        self.assertEqual(len(graph.edges), 1)
        marko_josh = graph.get_edge(0)

        self.assertIsInstance(marko_josh, PersistentEdge)

        self.assertEqual(
            marko_josh.path,
            os.path.join(graph.edges_path, "knows", "0"),
        )

        self.assertDictEqual(
            marko_josh.as_dict(),
            {
                "id": 0,
                "label": "knows",
                "metadata": {},
                "head_id": 0,
                "tail_id": 1,
                "properties": {
                    "since": "school",
                },
            }
        )

    def test_import_from_path_edges_with_bogus_extra_dir(self):
        path = create_graph_mock_path()
        os.mkdir(os.path.join(path, "edges", "knows", "bogus_dir"))
        graph = PersistentGraph(path)
        # should still have loaded the edge
        self.assertEqual(len(graph.edges), 1)

    def test_import_from_path_vertices_with_bogus_extra_dir(self):
        path = create_graph_mock_path()
        os.mkdir(os.path.join(path, "vertices", "person", "bogus_dir"))
        graph = PersistentGraph(path)
        # should still have loaded the edge
        self.assertEqual(len(graph.vertices), 2)

    def test_import_from_path_loaded_edges_missing_properties_file(self):
        path = create_graph_mock_path()

        # deleted the edges properties file.
        os.remove(
            os.path.join(
                path,
                "edges",
                "knows",
                "0",
                "properties.json"
            )
        )

        graph = PersistentGraph(path)

        marko = graph.get_vertex(0)
        josh = graph.get_vertex(1)
        marko_josh = graph.get_edge(0)

        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(marko_josh.head, marko)
        self.assertEqual(marko_josh.tail, josh)
        self.assertIsInstance(marko_josh, PersistentEdge)
        self.assertEqual(
            marko_josh.path,
            os.path.join(graph.edges_path, "knows", "0"),
        )
        self.assertDictEqual(marko_josh.properties, {})

    def test_import_from_path_loaded_edges_unknown_vertex(self):
        path = create_graph_mock_path()
        old = os.path.join(
            path,
            "edges",
            "knows",
            "0",
            "head",
            "0"
        )
        new = os.path.join(
            path,
            "edges",
            "knows",
            "0",
            "head",
            "5"
        )
        os.rename(old, new)

        self.assertRaises(
            KeyError,
            PersistentGraph,
            path
        )

    def test_import_from_path_loaded_edges_head_vertex_not_a_int(self):
        path = create_graph_mock_path()
        old = os.path.join(
            path,
            "edges",
            "knows",
            "0",
            "head",
            "0"
        )
        new = os.path.join(
            path,
            "edges",
            "knows",
            "0",
            "head",
            "non-int"
        )
        os.rename(old, new)

        graph = PersistentGraph(path)
        self.assertEqual(len(graph.edges), 0)

    def test_import_from_path_loaded_edges_tail_vertex_not_a_int(self):
        path = create_graph_mock_path()
        old = os.path.join(
            path,
            "edges",
            "knows",
            "0",
            "tail",
            "1"
        )
        new = os.path.join(
            path,
            "edges",
            "knows",
            "0",
            "tail",
            "non-int"
        )
        os.rename(old, new)

        graph = PersistentGraph(path)
        self.assertEqual(len(graph.edges), 0)

    def test_import_from_path_loaded_vertices(self):
        path = create_graph_mock_path()
        graph = PersistentGraph(path)

        self.assertEqual(len(graph.vertices), 2)

        # test marko was imported and has id 0
        marko = graph.get_vertex(0)
        self.assertIsInstance(marko, PersistentVertex)
        self.assertEqual(
            marko.path,
            os.path.join(graph.vertices_path, "person", "0")
        )
        self.assertDictEqual(
            marko.properties,
            {
                "name": "Marko"
            }
        )

        # test josh was imported and has id 1
        josh = graph.get_vertex(1)
        self.assertIsInstance(josh, PersistentVertex)
        self.assertEqual(
            josh.path,
            os.path.join(graph.vertices_path, "person", "1")
        )
        self.assertDictEqual(
            josh.properties,
            {
                "name": "Josh"
            }
        )

        # check that the next vertex has an id of 3
        spot = graph.add_vertex("dog", name="Spot")
        self.assertEqual(spot.ident, 2)

    def test_create_persistent_graph_with_no_path(self):
        self.assertEqual(
            sorted(os.listdir(self.graph.path)),
            sorted([".lock", "edges", "vertices"]),
        )

        # check for the constraints files
        self.assertEqual(
            sorted(os.listdir(self.graph.vertices_path)),
            sorted(["constraints.json"]),
        )

    def test_add_vertex(self):
        marko = self.graph.add_vertex("person", name="Marko")
        josh = self.graph.add_vertex("person", name="Josh")
        spot = self.graph.add_vertex("dog", name="Spot")

        # Check for the label folder
        self.assertEqual(
            sorted(os.listdir(self.graph.vertices_path)),
            sorted(["constraints.json", "dog", "person"]),
        )

        # Check in the label folder for vertex ident folders
        self.assertEqual(
            sorted(
                os.listdir(
                    os.path.join(self.graph.vertices_path, "person")
                )
            ),
            sorted([str(marko.ident), str(josh.ident)]),
        )

        self.assertEqual(
            sorted(
                os.listdir(
                    os.path.join(self.graph.vertices_path, "dog")
                )
            ),
            sorted([str(spot.ident)]),
        )

        # check in the verext folder for the property file and the
        # in/out edges folders - checking only one vertex should be enough.
        self.assertEqual(
            sorted(os.listdir(marko.path)),
            sorted(["properties.json", "in-edges", "out-edges"]),
        )

        # check that the properties file was populated
        self.assertDictEqual(
            json.load(open(os.path.join(str(marko.path), "properties.json"))),
            {"name": "Marko"},
        )

    def test_add_edge(self):
        marko = self.graph.add_vertex("person", name="Marko")
        josh = self.graph.add_vertex("person", name="Josh")
        edge = self.graph.add_edge(marko, "knows", josh, since="school")

        # Check for the label folder
        self.assertEqual(
            sorted(os.listdir(self.graph.edges_path)),
            ["knows"],
        )

        # Check in the label folder for edge ident folders
        self.assertEqual(
            sorted(
                os.listdir(
                    os.path.join(self.graph.edges_path, "knows")
                )
            ),
            sorted([str(edge.ident)]),
        )

        # check in the edge folder has a properties file, and a head and tail
        # directory
        self.assertEqual(
            sorted(
                os.listdir(
                    os.path.join(
                        self.graph.edges_path, "knows", str(edge.ident)
                    )
                )
            ),
            sorted(
                [
                    "properties.json",
                    "head",
                    "tail"
                ]
            ),
        )

        # check that the vertices in the edge folder are symlinks
        mark_link = os.path.join(
            self.graph.edges_path,
            "knows",
            str(edge.ident),
            "head",
            str(marko.ident),
        )

        josh_link = os.path.join(
            self.graph.edges_path,
            "knows",
            str(edge.ident),
            "tail",
            str(josh.ident),
        )

        self.assertEqual(os.path.exists(mark_link), True)
        self.assertEqual(os.path.exists(josh_link), True)
        self.assertEqual(os.path.islink(mark_link), True)
        self.assertEqual(os.path.islink(josh_link), True)

        # check that the properties file was populated
        self.assertEqual(
            json.load(
                open(
                    os.path.join(
                        self.graph.edges_path,
                        "knows",
                        str(edge.ident),
                        "properties.json"
                    )
                )
            ),
            {"since": "school"},
        )

        # check that the edge in the vertex in and out edge folders are
        # symlinked to the edge
        mark_out_edge_link = os.path.join(
            self.graph.vertices_path,
            "person",
            str(marko.ident),
            "out-edges",
            str(edge.ident),
        )

        josh_in_edge_link = os.path.join(
            self.graph.vertices_path,
            "person",
            str(josh.ident),
            "in-edges",
            str(edge.ident),
        )

        self.assertEqual(os.path.islink(mark_out_edge_link), True)
        self.assertEqual(os.path.islink(josh_in_edge_link), True)

    def test_set_property(self):
        marko = self.graph.add_vertex("person", name="Marko")
        self.graph.set_property(marko, surname="Polo")

        self.assertDictEqual(
            json.load(
                open(
                    os.path.join(
                        self.graph.vertices_path,
                        "person",
                        str(marko.ident),
                        "properties.json"
                    )
                )
            ),
            {
                "name": "Marko",
                "surname": "Polo",
            },
        )

    def test_remove_vertex(self):
        marko = self.graph.add_vertex("person", name="Marko")
        josh = self.graph.add_vertex("person", name="Josh")

        self.graph.remove_vertex(marko)

        self.assertEqual(
            sorted(
                os.listdir(
                    os.path.join(self.graph.vertices_path, "person")
                )
            ),
            sorted([str(josh.ident)]),
        )

    def test_remove_edge(self):
        marko = self.graph.add_vertex("person", name="Marko")
        josh = self.graph.add_vertex("person", name="Josh")
        spot = self.graph.add_vertex("dog", name="Spot")

        edge = self.graph.add_edge(marko, "knows", josh)
        edge2 = self.graph.add_edge(marko, "knows", spot)

        self.graph.remove_edge(edge)

        self.assertEqual(
            sorted(
                os.listdir(
                    os.path.join(self.graph.edges_path, "knows")
                )
            ),
            sorted([str(edge2.ident)]),
        )

    def test_add_vertex_constraints(self):
        self.graph.add_vertex_constraint("person", "name")
        self.assertEqual(
            json.load(
                open(
                    os.path.join(
                        self.graph.vertices_path,
                        "constraints.json"
                    ),
                )
            ),
            [
                {
                    "label": "person",
                    "key": "name"
                }
            ],
        )

    def test_path_already_locked(self):
        path = self.graph.path
        self.assertRaises(
            interfaces.DatabasePathLocked,
            PersistentGraph,
            path
        )

    def test_close(self):
        self.graph.close()
        self.assertEqual(
            self.graph._lock.locked,
            False
        )
