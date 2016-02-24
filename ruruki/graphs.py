"""
Graph implementations
"""
from collections import defaultdict
import json
import logging
import os
import shutil
from tempfile import mkdtemp
from ruruki import interfaces
from ruruki.entities import Vertex, Edge
from ruruki.entities import EntitySet


class IDGenerator(object):
    """
    ID generator and tracker.
    """

    def __init__(self):
        self.vid = 0
        self.eid = 0

    def get_edge_id(self):
        """
        Generate a edge id.

        :returns: Edge id number.
        :rtype: :class:`int`
        """
        ident = self.eid
        self.eid += 1
        return ident

    def get_vertex_id(self):
        """
        Generate a vertex id.

        :returns: Vertex id number.
        :rtype: :class:`int`
        """
        ident = self.vid
        self.vid += 1
        return ident


class Graph(interfaces.IGraph):
    """
    In-memory graph database.

    See :class:`~.IGraph` for doco.
    """

    def __init__(self):
        self._id_tracker = IDGenerator()
        self._vconstraints = defaultdict(dict)
        self._econstraints = defaultdict()
        self.vertices = EntitySet()
        self.edges = EntitySet()

    def load(self, file_handler):
        vertex_id_mapping = {}
        data = json.load(file_handler)

        constraints = data.get("constraints", [])
        for constraint_dict in constraints:
            self.add_vertex_constraint(
                constraint_dict["label"],
                constraint_dict["key"],
            )

        vertices = sorted(data.get("vertices", []), key=lambda x: x["id"])
        for vertex_dict in vertices:
            vertex = self.get_or_create_vertex(
                vertex_dict["label"],
                **vertex_dict["properties"]
            )
            vertex_id_mapping[vertex_dict["id"]] = vertex

        edges = sorted(data.get("edges", []), key=lambda x: x["id"])
        for edge_dict in edges:
            head = vertex_id_mapping[edge_dict["head_id"]]
            tail = vertex_id_mapping[edge_dict["tail_id"]]
            self.get_or_create_edge(
                head,
                edge_dict["label"],
                tail,
                **edge_dict["properties"]
            )

    def dump(self, file_handler):
        data = {
            "vertices": [],
            "edges": [],
            "constraints": [],
        }

        for vertex in self.vertices:
            data["vertices"].append(vertex.as_dict())

        for edge in self.edges:
            data["edges"].append(edge.as_dict())

        for label, key in self.get_vertex_constraints():
            data["constraints"].append(
                {
                    "label": label,
                    "key": key
                }
            )

        json.dump(data, file_handler, indent=4, sort_keys=True)

    def add_vertex_constraint(self, label, key):
        self._vconstraints[label][key] = set()

    def get_vertex_constraints(self):
        constraints = []
        for label in self._vconstraints:
            for key in self._vconstraints[label]:
                constraints.append((label, key))
        return constraints

    def bind_to_graph(self, entity):
        if isinstance(entity, interfaces.IVertex):
            entity.ident = self._id_tracker.get_vertex_id()
        elif isinstance(entity, interfaces.IEdge):
            entity.ident = self._id_tracker.get_edge_id()
        else:
            raise interfaces.UnknownEntityError(
                "Unknown entity {0!r}".format(entity)
            )
        entity.graph = self

    def get_or_create_vertex(self, label=None, **kwargs):
        if not label or not kwargs:
            return None

        # first check constraints.
        if label in self._vconstraints:
            for key, collection in self._vconstraints[label].items():
                if key not in kwargs:
                    continue

                for vertex in collection:
                    if vertex.properties[key] == kwargs[key]:
                        return vertex

        # no matches in constraints, so do a EntitySet filter
        vertices = self.vertices.filter(label, **kwargs).all()
        if len(vertices) > 1:
            raise interfaces.MultipleFoundExpectedOne(
                "Multiple vertices found when one expected."
            )
        elif len(vertices) == 1:
            return vertices[0]

        return self.add_vertex(label, **kwargs)

    def get_or_create_edge(self, head, label, tail, **kwargs):
        if isinstance(head, tuple):
            head = self.get_or_create_vertex(head[0], **head[1])

        if isinstance(tail, tuple):
            tail = self.get_or_create_vertex(tail[0], **tail[1])

        # There can only a single edge between head and tail with a
        # particular label. So there is not point filtering for
        # properties.
        indexed_edge = self._econstraints.get((head, label, tail))
        if indexed_edge:
            return indexed_edge
        return self.add_edge(head, label, tail, **kwargs)

    def add_edge(self, head, label, tail, **kwargs):
        if (head, label, tail) in self._econstraints:
            raise interfaces.ConstraintViolation(
                "Duplicate {0!r} edges between head {1!r} and tail {2!r} "
                "is not allowed".format(
                    label,
                    head,
                    tail
                )
            )
        edge = Edge(head, label, tail, **kwargs)
        self._econstraints[(head, label, tail)] = edge
        self.bind_to_graph(edge)
        self.edges.add(edge)
        head.out_edges.add(edge)
        tail.in_edges.add(edge)
        return edge

    def add_vertex(self, label=None, **kwargs):
        vertex = Vertex(label=label, **kwargs)

        if label in self._vconstraints:
            for key in self._vconstraints[label]:
                if key in kwargs:
                    self._vconstraints[label][key].add(vertex)

        self.bind_to_graph(vertex)
        self.vertices.add(vertex)
        return vertex

    def set_property(self, entity, **kwargs):
        if entity not in self:
            raise interfaces.UnknownEntityError(
                "Unknown entity {0!r}".format(entity)
            )

        if isinstance(entity, interfaces.IVertex):
            key_index = self._vconstraints.get(entity.label, {})
            for key, value in kwargs.items():
                if key not in key_index:
                    continue
                for indexed_entity in key_index[key]:
                    if indexed_entity != entity:
                        if indexed_entity.properties[key] == value:
                            raise interfaces.ConstraintViolation(
                                "Constraint violation with {0}".format(
                                    entity
                                )
                            )
            self.vertices.update_index(entity, **kwargs)

        if isinstance(entity, interfaces.IEdge):
            self.edges.update_index(entity, **kwargs)

        entity._update_properties(kwargs)  # pylint: disable=protected-access

    def get_edge(self, id_num):
        return self.edges.get(id_num)

    def get_vertex(self, id_num):
        return self.vertices.get(id_num)

    def get_edges(self, head=None, label=None, tail=None, **kwargs):
        if head is None and tail is None:
            return self.edges.filter(label, **kwargs)

        container = EntitySet()
        for edge in self.edges.filter(label, **kwargs):
            if head and tail is None:
                if edge.head == head:
                    container.add(edge)
            elif tail and head is None:
                if edge.tail == tail:
                    container.add(edge)
            else:
                if edge.head == head and edge.tail == tail:
                    container.add(edge)
        return container

    def get_vertices(self, label=None, **kwargs):
        return self.vertices.filter(label, **kwargs)

    def remove_edge(self, edge):
        edge.head.remove_edge(edge)
        edge.tail.remove_edge(edge)
        self.edges.remove(edge)

    def remove_vertex(self, vertex):
        if len(vertex.get_both_edges()) > 0:
            raise interfaces.VertexBoundByEdges(
                "Vertex {0!r} is still bound to another vertex "
                "by an edge. First remove all the edges on the vertex and "
                "then remove it again.".format(vertex)
            )
        self.vertices.remove(vertex)

    def close(self):  # pragma: no cover
        # Nothing to do for the close at this stage.
        return

    def __contains__(self, entity):
        is_vertex = isinstance(entity, interfaces.IVertex)
        is_edge = isinstance(entity, interfaces.IEdge)

        if not is_vertex and not is_edge:
            raise TypeError(
                "Unsupported entity type {0}".format(type(entity))
            )

        return entity in self.vertices or entity in self.edges


class PersistentGraph(Graph):
    """
    Persistent Graph database storing data to a file system.

    See :class:`~.IGraph` for doco.

    .. code::

        path
           |_ vertices
           |     |_ constraints.txt (file)
           |     |_ label
           |     |     |_ 0
           |     |        |_ properties.txt (file)
           |     |        |_ in-edges
           |     |        |     |_ 0 -> ../../../../edges/label/0 (symlink)
           |     |        |_ out-edges
           |     |              |_
           |     |
           |     |_ label
           |     |    |_ 1
           |     |         |_ properties.txt (file)
           |     |          |_ in-edges
           |     |          |     |_
           |     |          |_ out-edges
           |     |                |_ 0 -> ../../../../edges/label/0 (symlink)
           |
           |_ edges
                 |_ constraints.txt
                 |_ label
                       |
                       |_0
                         |_ properties.txt (file)
                         |_ ../../../vertices/0 (symlik)
                         |_ ../../../vertices/1 (symlik)


    :param path: Path to ruruki graph data on disk. If :obj:`None`, then
        a temporary path will be created.
    :type path: :class:`str`
    """
    def __init__(self, path=None):
        super(PersistentGraph, self).__init__()
        self.path = path
        if self.path is None:
            self._create_path()

    def _create_path(self):
        self.path = mkdtemp(suffix="-ruruki-db")
        logging.info("Created temporary graph db path %r", self.path)

        # Create the vertices path
        self.vertices_path = os.path.join(self.path, "vertices")
        os.makedirs(self.vertices_path)

        # Create the edges path
        self.edges_path = os.path.join(self.path, "edges")
        os.makedirs(self.edges_path)

        # Create constraint files
        open(os.path.join(self.vertices_path, "constraints.txt"), "w").close()
        open(os.path.join(self.edges_path, "constraints.txt"), "w").close()

    def add_vertex_constraint(self, label, key):
        super(PersistentGraph, self).add_vertex_constraint(label, key)
        constraint_file = os.path.join(self.vertices_path, "constraints.txt")
        with open(constraint_file, "w") as constraint_fh:
            for label, key in self.get_vertex_constraints():
                constraint_fh.write("{}={}\n".format(label, key))

    def add_vertex(self, label=None, **kwargs):
        vertex = super(PersistentGraph, self).add_vertex(label, **kwargs)
        vertex_path = os.path.join(self.vertices_path, label, str(vertex.ident))
        os.makedirs(vertex_path)
        os.makedirs(os.path.join(vertex_path, "in-edges"))
        os.makedirs(os.path.join(vertex_path, "out-edges"))
        vertex.set_property(_path=vertex_path)
        return vertex

    def add_edge(self, head, label, tail, **kwargs):
        edge = super(PersistentGraph, self).add_edge(
            head, label, tail, **kwargs
        )

        edge_path = os.path.join(self.edges_path, label, str(edge.ident))
        os.makedirs(edge_path)
        edge.set_property(_path=edge_path)

        os.symlink(
            head.properties["_path"],
            os.path.join(edge_path, str(head.ident))
        )

        os.symlink(
            tail.properties["_path"],
            os.path.join(edge_path, str(tail.ident))
        )

        os.symlink(
            edge_path,
            os.path.join(
                head.properties["_path"],
                "out-edges",
                str(edge.ident)
            )
        )

        os.symlink(
            edge_path,
            os.path.join(
                tail.properties["_path"],
                "in-edges",
                str(edge.ident)
            )
        )

        return edge

    def set_property(self, entity, **kwargs):
        super(PersistentGraph, self).set_property(entity, **kwargs)

        # Update the properties to the properties file
        properties_file = os.path.join(
            entity.properties["_path"],
            "properties.txt"
        )

        with open(properties_file, "w") as prop_file:
            for key, value in entity.properties.items():
                # we do not want the path metadata in the properties file.
                if key == "_path":
                    continue
                prop_file.write("{}={}\n".format(key, value))

    def remove_edge(self, edge):
        shutil.rmtree(edge.properties["_path"])
        super(PersistentGraph, self).remove_edge(edge)

    def remove_vertex(self, vertex):
        shutil.rmtree(vertex.properties["_path"])
        super(PersistentGraph, self).remove_vertex(vertex)
