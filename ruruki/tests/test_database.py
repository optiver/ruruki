# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements

import json
import os
import unittest2
from ruruki import create_graph
from ruruki import interfaces
from ruruki.graphs import PersistentGraph
from ruruki.entities import Entity, Edge, Vertex
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
        graph = create_graph()
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
        graph = create_graph()
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


class TestPersistentGraph(unittest2.TestCase):
    def setUp(self):
        self.graph = PersistentGraph()

    def test_create_persistent_graph_with_no_path(self):
        self.assertEqual(
            sorted(os.listdir(self.graph.path)),
            sorted(["edges", "vertices"]),
        )

        # check for the constraints files
        self.assertEqual(
            sorted(os.listdir(self.graph.vertices_path)),
            sorted(["constraints.txt"]),
        )

        self.assertEqual(
            sorted(os.listdir(self.graph.edges_path)),
            sorted(["constraints.txt"]),
        )

    def test_create_persistent_graph_with_path(self):
        graph = PersistentGraph("/some/path")
        self.assertEqual(graph.path, "/some/path")

    def test_add_vertex(self):
        marko = self.graph.add_vertex("person", name="Marko")
        josh = self.graph.add_vertex("person", name="Josh")
        spot = self.graph.add_vertex("dog", name="Spot")

        # Check for the label folder
        self.assertEqual(
            sorted(os.listdir(self.graph.vertices_path)),
            sorted(["constraints.txt", "dog", "person"]),
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
            sorted(
                os.listdir(
                    os.path.join(
                        self.graph.vertices_path, "person", str(marko.ident)
                    )
                )
            ),
            sorted(["properties.txt", "in-edges", "out-edges"]),
        )

        # check that the properties file was populated
        self.assertEqual(
            open(
                os.path.join(
                    self.graph.vertices_path,
                    "person",
                    str(marko.ident),
                    "properties.txt"
                )
            ).readlines(),
            ["name=Marko\n"]
        )

    def test_add_edge(self):
        marko = self.graph.add_vertex("person", name="Marko")
        josh = self.graph.add_vertex("person", name="Josh")
        edge = self.graph.add_edge(marko, "knows", josh, since="school")

        # Check for the label folder
        self.assertEqual(
            sorted(os.listdir(self.graph.edges_path)),
            sorted(["constraints.txt", "knows"]),
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

        # check in the edge folder for the property file and the
        # vertices symlinks
        self.assertEqual(
            sorted(
                os.listdir(
                    os.path.join(
                        self.graph.edges_path, "knows", str(edge.ident)
                    )
                )
            ),
            sorted(["properties.txt", str(marko.ident), str(josh.ident)]),
        )

        # check that the vertices in the edge folder are symlinks
        mark_link = os.path.join(
            self.graph.edges_path, "knows", str(edge.ident), str(marko.ident)
        )
        josh_link = os.path.join(
            self.graph.edges_path, "knows", str(edge.ident), str(marko.ident)
        )

        self.assertEqual(os.path.islink(mark_link), True)
        self.assertEqual(os.path.islink(josh_link), True)

        # check that the properties file was populated
        self.assertEqual(
            open(
                os.path.join(
                    self.graph.edges_path,
                    "knows",
                    str(edge.ident),
                    "properties.txt"
                )
            ).readlines(),
            ["since=school\n"]
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

        self.assertEqual(
            sorted(
                open(
                    os.path.join(
                        self.graph.vertices_path,
                        "person",
                        str(marko.ident),
                        "properties.txt"
                    )
                ).readlines()
            ),
            sorted(
                [
                    "name=Marko\n",
                    "surname=Polo\n",
                ]
            ),
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
            open(
                os.path.join(
                    self.graph.vertices_path,
                    "constraints.txt"
                ),
            ).read(),
            "person=name\n",
        )
