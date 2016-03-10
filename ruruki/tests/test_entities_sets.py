# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=no-member

import unittest2 as unittest
from ruruki.graphs import IDGenerator
from ruruki.entities import Vertex, EntitySet, Edge
from ruruki.test_utils import base


class TestEntitySet(base.TestBase):
    def setUp(self):
        super(TestEntitySet, self).setUp()
        self.container = EntitySet([self.marko, self.josh, self.peter])

    def test_add(self):
        self.container.add(self.lop)
        self.assertEqual(
            self.container.sorted(key=lambda x: x.ident),
            sorted(
                [self.marko, self.josh, self.peter, self.lop],
                key=lambda x: x.ident,
            )
        )

    def test_add_dup_id(self):
        sue = Vertex("person", name="dup_vertex_id")
        sue.ident = 0
        self.assertRaises(
            KeyError,
            self.container.add,
            sue
        )

    def test_add_same_vertex(self):
        self.container.add(self.marko)
        self.assertEqual(
            self.container.sorted(),
            sorted([self.marko, self.josh, self.peter]),
        )

    def test_get_labels(self):
        self.container.add(self.lop)
        self.assertEqual(
            sorted(self.container.get_labels()),
            sorted(["person", "app"]),
        )

    def test_get_indexes(self):
        self.assertEqual(
            sorted(self.container.get_indexes()),
            sorted(
                [
                    ("person", "age"),
                    ("person", "name"),
                ]
            ),
        )

    def test_update_index(self):
        self.container.update_index(self.marko, surname="Foo")
        self.assertEqual(
            sorted(self.container.get_indexes()),
            sorted(
                [
                    ("person", "age"),
                    ("person", "name"),
                    ("person", "surname"),
                ]
            ),
        )

    def test_remove(self):
        self.container.remove(self.marko)
        self.assertEqual(
            self.container.sorted(),
            sorted([self.josh, self.peter])
        )

    def test_remove_with_unindexed_property(self):
        self.marko.properties["unindexed"] = "say what"
        self.container.remove(self.marko)
        self.assertEqual(
            self.container.sorted(),
            sorted([self.josh, self.peter])
        )

    def test_remove_unknown_entity_id(self):
        sue = Vertex(100, name="sue")
        self.assertRaises(
            KeyError,
            self.container.remove,
            sue,
        )

    def test_contains(self):
        self.assertIn(self.marko, self.container)

    def test_iter(self):
        self.assertEqual(
            self.container.sorted(),
            sorted([self.marko, self.josh, self.peter])
        )

    def test_get(self):
        self.assertEqual(self.container.get(0), self.marko)

    def test_get_no_such_entity_with_id(self):
        self.assertRaises(
            KeyError,
            self.container.get,
            100,
        )

    def test_len(self):
        self.assertEqual(3, len(self.container))

    def test_all(self):
        self.assertEqual(
            sorted(self.container.all(), key=lambda x: x.ident),
            sorted([self.marko, self.josh, self.peter], key=lambda x: x.ident)
        )

    def test_sorted(self):
        self.assertEqual(
            self.container.sorted(),
            sorted([self.marko, self.josh, self.peter])
        )

    def test_sorted_cmp_key(self):
        self.assertEqual(
            self.container.sorted(
                key=lambda x: x.properties["name"]
            ),
            sorted(
                [
                    self.marko,
                    self.josh,
                    self.peter
                ],
                key=lambda x: x.properties["name"],
            )
        )


class FilteringBase(unittest.TestCase):
    def setUp(self):
        id_generator = IDGenerator()
        self.marko = Vertex(
            "Father",
            name="Marko",
            surname="Jones",
            age=30,
        )
        self.john = Vertex(
            "Brother",
            name="John",
            surname="Jones",
            age=30
        )
        self.peter = Vertex(
            "Uncle",
            name="Peter",
            surname="Doe",
            age=20
        )

        # add id's to the unbound vertices
        self.marko.ident = id_generator.get_vertex_id()
        self.john.ident = id_generator.get_vertex_id()
        self.peter.ident = id_generator.get_vertex_id()
        self.container = EntitySet([self.marko, self.john, self.peter])


class TestFiltering(FilteringBase):
    def test_filter_for_labels_with_no_props(self):
        marko = Vertex(
            "person",
            name="Marko",
        )
        josh = Vertex(
            "person",
            name="Marko",
        )
        edge = Edge(marko, "father", josh)
        container = EntitySet()
        container.add(edge)
        self.assertEqual(
            container.filter("father").sorted(),
            sorted([edge])
        )

    def test_filter_for_vertex_with_prop_None(self):
        sue = Vertex(
            "person",
            name="sue",
            age=None,
        )
        self.container.add(sue)
        self.assertEqual(
            self.container.filter(name="Marko", age__gt=0).all(),
            [self.marko],
        )

    def test_filter_for_only_labels(self):
        self.assertEqual(
            self.container.filter("Father").sorted(),
            sorted([self.marko]),
        )

    def test_filter_with_label(self):
        self.assertEqual(
            self.container.filter("Father", name="Marko").sorted(),
            [self.marko],
        )

    def test_filter_without_label(self):
        self.assertEqual(
            self.container.filter(name="Marko").sorted(),
            [self.marko],
        )

    def test_filter_with_label_multi_props(self):
        self.assertEqual(
            self.container.filter("Father", surname="Jones", age=30).sorted(),
            [self.marko],
        )

    def test_filter_without_label_multi_props(self):
        self.assertEqual(
            self.container.filter(surname="Jones", age=30).sorted(),
            sorted([self.marko, self.john]),
        )

    def test_filter_with_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter("Father", surname="Jones", age=31).sorted(),
            [],
        )

    def test_filter_without_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(surname="Jones", age=31).sorted(),
            [],
        )

    def test_no_label_no_kwargs(self):
        self.assertEqual(
            self.container.filter(),
            self.container,
        )

    def test_unknown_prop_key_with_label(self):
        self.assertEqual(
            self.container.filter("Father", job="developer").sorted(),
            [],
        )

    def test_unknown_prop_key_without_label(self):
        self.assertEqual(
            self.container.filter(job="developer").sorted(),
            [],
        )


class TestSetOperations(FilteringBase):
    def test_union(self):
        sue = Vertex(
            "Sister",
            name="Sue"
        )
        union = self.container | EntitySet([sue, self.marko])
        self.assertEqual(
            union.sorted(),  # pylint: disable=no-member
            sorted(
                [
                    self.marko,
                    self.john,
                    self.peter,
                    sue
                ]
            )
        )

    def test_union_filter_for_labels_with_no_props(self):
        id_generator = IDGenerator()
        marko = Vertex(
            "person",
            name="Marko",
        )
        josh = Vertex(
            "person",
            name="Marko",
        )
        edge = Edge(marko, "father", josh)
        edge2 = Edge(josh, "son", marko)

        # attach ID's to the vertices and edges.
        marko.ident = id_generator.get_vertex_id()
        josh.ident = id_generator.get_vertex_id()
        edge.ident = id_generator.get_edge_id()
        edge2.ident = id_generator.get_edge_id()

        container1 = EntitySet()
        container2 = EntitySet()

        container1.add(edge)
        container2.add(edge2)
        container3 = container1 | container2

        self.assertEqual(
            container3.filter("father").sorted(),
            sorted([edge])
        )
        self.assertEqual(
            container3.filter("son").sorted(),
            sorted([edge2])
        )

    def test_union_with_duplicate_id(self):
        union = self.container | EntitySet([self.marko])
        self.assertEqual(
            union.sorted(),  # pylint: disable=no-member
            sorted(
                [
                    self.marko,
                    self.john,
                    self.peter,
                ]
            )
        )

    def test_intersection(self):
        sue = Vertex(
            "Sister",
            name="Sue"
        )
        intersection = self.container & EntitySet([self.marko, sue])
        self.assertEqual(
            intersection.sorted(),  # pylint: disable=no-member
            sorted(
                [
                    self.marko,
                ]
            )
        )

    def test_difference(self):
        sue = Vertex(
            "Sister",
            name="Sue"
        )
        diff = self.container - EntitySet([self.marko, sue])
        self.assertEqual(
            diff.sorted(),  # pylint: disable=no-member
            sorted(
                [
                    self.john,
                    self.peter,
                ]
            )
        )

    def test_symmetric_difference(self):
        sue = Vertex(
            "Sister",
            name="Sue"
        )
        sym_diff = self.container ^ EntitySet([self.marko, sue])
        self.assertEqual(
            sym_diff.sorted(),  # pylint: disable=no-member
            sorted(
                [
                    self.john,
                    self.peter,
                    sue,
                ]
            )
        )


class TestStartsWithFiltering(FilteringBase):
    def test_filter_with_label(self):
        self.assertEqual(
            self.container.filter("Father", name__startswith="M").sorted(),
            [self.marko],
        )

    def test_filter_without_label(self):
        self.assertEqual(
            self.container.filter(name__startswith="M").sorted(),
            [self.marko],
        )

    def test_filter_with_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                name__startswith="M",
                surname="Jones",
            ).sorted(),
            [self.marko],
        )

    def test_filter_without_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                surname__startswith="Jo",
                age=30,
            ).sorted(),
            sorted([self.marko, self.john]),
        )

    def test_filter_with_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                surname__startswith="Jo",
                age=31,
            ).sorted(),
            [],
        )

    def test_filter_without_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                surname__startswith="Jo",
                age=31,
            ).sorted(),
            [],
        )

    def test_incase_filter_with_label(self):
        self.assertEqual(
            self.container.filter("Father", name__istartswith="m").sorted(),
            [self.marko],
        )

    def test_incase_filter_without_label(self):
        self.assertEqual(
            self.container.filter(name__istartswith="m").sorted(),
            [self.marko],
        )

    def test_incase_filter_with_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                name__istartswith="m",
                surname="Jones",
            ).sorted(),
            [self.marko],
        )

    def test_incase_filter_without_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                surname__istartswith="jo",
                age=30,
            ).sorted(),
            sorted([self.marko, self.john]),
        )

    def test_incase_filter_with_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                surname__istartswith="jo",
                age=31,
            ).sorted(),
            [],
        )

    def test_incase_filter_without_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                surname__istartswith="jo",
                age=31,
            ).sorted(),
            [],
        )


class TestEndsWithFiltering(FilteringBase):
    def test_filter_with_label(self):
        self.assertEqual(
            self.container.filter("Father", name__endswith="ko").sorted(),
            [self.marko],
        )

    def test_filter_without_label(self):
        self.assertEqual(
            self.container.filter(name__endswith="ko").sorted(),
            [self.marko],
        )

    def test_filter_with_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                name__endswith="ko",
                surname="Jones",
            ).sorted(),
            [self.marko],
        )

    def test_filter_without_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                surname__endswith="s",
                age=30,
            ).sorted(),
            [self.marko, self.john],
        )

    def test_filter_with_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                surname__endswith="s",
                age=31,
            ).sorted(),
            [],
        )

    def test_filter_without_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                surname__endswith="es",
                age=31,
            ).sorted(),
            [],
        )

    def test_incase_filter_with_label(self):
        self.assertEqual(
            self.container.filter("Father", name__iendswith="ko").sorted(),
            [self.marko],
        )

    def test_incase_filter_without_label(self):
        self.assertEqual(
            self.container.filter(name__iendswith="ko").sorted(),
            [self.marko],
        )

    def test_incase_filter_with_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                name__iendswith="ko",
                surname="Jones",
            ).sorted(),
            [self.marko],
        )

    def test_incase_filter_without_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                surname__iendswith="s",
                age=30,
            ).sorted(),
            sorted([self.marko, self.john]),
        )

    def test_incase_filter_with_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                surname__iendswith="s",
                age=31,
            ).sorted(),
            [],
        )

    def test_incase_filter_without_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                surname__iendswith="es",
                age=31,
            ).sorted(),
            [],
        )


class TestContainsFiltering(FilteringBase):
    def test_filter_with_label(self):
        self.assertEqual(
            self.container.filter("Father", name__contains="k").sorted(),
            [self.marko],
        )

    def test_filter_without_label(self):
        self.assertEqual(
            self.container.filter(name__contains="k").sorted(),
            [self.marko],
        )

    def test_filter_with_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                name__contains="k",
                surname="Jones",
            ).sorted(),
            [self.marko],
        )

    def test_filter_without_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                surname__contains="o",
                age=30,
            ).sorted(),
            sorted([self.marko, self.john]),
        )

    def test_filter_with_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                surname__contains="x",
                age=31,
            ).sorted(),
            [],
        )

    def test_filter_without_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                surname__contains="x",
                age=31,
            ).sorted(),
            [],
        )

    def test_incase_filter_with_label(self):
        self.assertEqual(
            self.container.filter("Father", name__icontains="k").sorted(),
            [self.marko],
        )

    def test_incase_filter_without_label(self):
        self.assertEqual(
            self.container.filter(name__icontains="k").sorted(),
            [self.marko],
        )

    def test_incase_filter_with_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                name__icontains="k",
                surname="Jones",
            ).sorted(),
            [self.marko],
        )

    def test_incase_filter_without_label_multi_props(self):
        self.assertEqual(
            self.container.filter(
                surname__icontains="o",
                age=30,
            ).sorted(),
            sorted([self.marko, self.john]),
        )

    def test_incase_filter_with_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                "Father",
                surname__icontains="x",
                age=31,
            ).sorted(),
            [],
        )

    def test_incase_filter_without_label_not_all_props_match(self):
        self.assertEqual(
            self.container.filter(
                surname__icontains="x",
                age=31,
            ).sorted(),
            [],
        )


class TestLessEqualFiltering(FilteringBase):
    def test_filter_less_or_equal(self):
        self.assertEqual(
            self.container.filter(age__le=30).sorted(),
            sorted([self.marko, self.john, self.peter]),
        )
        self.assertEqual(
            self.container.filter(age__le=23).sorted(),
            sorted([self.peter]),
        )


class TestLessThanFiltering(FilteringBase):
    def test_filter_less_than(self):
        self.assertEqual(
            self.container.filter(age__lt=30).sorted(),
            sorted([self.peter]),
        )


class TestGreaterEqualFiltering(FilteringBase):
    def test_filter_greater_or_equal(self):
        self.assertEqual(
            self.container.filter(age__ge=30).sorted(),
            sorted([self.marko, self.john]),
        )


class TestGreaterThanFiltering(FilteringBase):
    def test_filter_greater_than(self):
        self.assertEqual(
            self.container.filter(age__gt=25).sorted(),
            sorted([self.marko, self.john]),
        )


class TestNotEqualFiltering(FilteringBase):
    def test_filter_not_equal(self):
        self.assertEqual(
            self.container.filter(name__ne="Marko").sorted(),
            sorted([self.john, self.peter]),
        )

    def test_filter_incase_not_equal(self):
        self.assertEqual(
            self.container.filter(name__ine="marko").sorted(),
            sorted([self.john, self.peter]),
        )


class TestEqualFiltering(FilteringBase):
    def test_filter_equal(self):
        self.assertEqual(
            self.container.filter(name__eq="Marko").sorted(),
            sorted([self.marko]),
        )

    def test_filter_incase_equal(self):
        self.assertEqual(
            self.container.filter(name__ieq="marko").sorted(),
            sorted([self.marko]),
        )
