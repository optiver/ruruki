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
           |     |    |_ 1
           |     |         |_ properties.json (file)
           |     |          |_ in-edges
           |     |          |     |_
           |     |          |_ out-edges
           |     |                |_ 0 -> ../../../../edges/label/0 (symlink)
           |
           |_ edges
                 |_ label
                       |
                       |_0
                         |_ properties.json (file)
                         |_ head
                         |   |_ ../../../vertices/0 (symlik)
                         |_ tail
                             |_ ../../../vertices/1 (symlik)


    :param path: Path to ruruki graph data on disk. If :obj:`None`, then
        a temporary path will be created, else passing in an empty ``path``
        will result in the creation of the graph data in the provided path.
    :type path: :class:`str`
    :raises EnvironmentError: If parameter `path` is missing the required
        files and directories to import.
    """
    def __init__(self, path=None):
        super(PersistentGraph, self).__init__()
        self.vertices_path = None
        self.edges_path = None
        self.vertices_constraints_path = None
        self.path = path
        if path is not None:
            self._load_from_path(path)
        else:
            self._create_path()

    def _load_from_path(self, path):
        """
        Scan through the given database path and load/import up all the
        relevant vertices, vertices constraints, and edges.

        :param path: Path to import.
        :type path: :class:`str`
        :raises EnvironmentError: If the path is missing or if the path
            does not contain the required vertices and edges folders.
        """
        def check_path_exists(path):
            """
            Simple internal helper function for checking the existence of
            a path.

            :param path: Path to check if it exists.
            :type path: :class:`str`
            :raises EnvironmentError: Is raised if the path does not exists.
            """
            if not os.path.exists(path):
                raise EnvironmentError(
                    "Could not find the directory {0!r}".format(path)
                )

        self.path = path
        check_path_exists(path)

        # check if there is are the required ``vertices`` and ``edges``
        # folders, else create the skeletons.
        if not os.listdir(self.path):
            self._create_vertex_skel(self.path)
            self._create_edge_skel(self.path)

        # set the vertex path and check that it exists.
        self.vertices_path = os.path.join(self.path, "vertices")
        check_path_exists(self.vertices_path)

        # set the edge path and check that it exists.
        self.edges_path = os.path.join(self.path, "edges")
        check_path_exists(self.edges_path)

        # check and the load the vertices constraints
        self.vertices_constraints_path = os.path.join(
            self.vertices_path, "constraints.json"
        )
        check_path_exists(path)

        # load all the constraint, vertices, and edges
        self._load_vconstraints_from_path(self.vertices_constraints_path)
        self._load_vertices_from_path(self.vertices_path)
        self._load_edges_from_path(self.edges_path)

    def _load_vconstraints_from_path(self, path):
        """
        Open, parse and load the vertices constraints.

        :param path: Vertices constraints file to open, parse and import.
        :type path: :class:`str`
        """
        with open(path) as vconstraints_fh:
            for label, key in json.load(vconstraints_fh).items():
                self.add_vertex_constraint(label, key)

    def _load_vertices_from_path(self, path):
        """
        Scan through the given path and load/import all the vertices.

        .. code::

            path
               |_ vertices
                    |_ constraints.json (file)
                    |_ label
                    |     |_ 0
                    |        |_ properties.json (file)
                    |
                    |_ label
                         |_ 1
                            |_ properties.json (file)

        :param path: Vertices Path to walk and import.
        :type path: :class:`str`
        """
        # walk the path loading vertices that are found.
        for label in os.listdir(path):

            label_path = os.path.join(path, label)

            # skip over files because we are only looking for directories.
            if os.path.isfile(label_path):
                continue

            # run over all the vertice id's that we can find
            # and loading the properties if found.
            for dirname in sorted(os.listdir(label_path)):
                properties = {}
                properties_filename = os.path.join(
                    label_path,
                    dirname,
                    "properties.json"
                )

                if os.path.exists(properties_filename):
                    with open(properties_filename) as properties_filehandle:
                        properties = json.load(properties_filehandle)

                # reset the id to the id being loaded.
                self._id_tracker.vid = int(dirname)
                super(PersistentGraph, self).add_vertex(label, **properties)

    def _load_edges_from_path(self, path):
        """
        Scan through the given path and load/import all the edges.

        .. code::

            path
               |_ edges
                     |_ label
                          |_0
                            |_ properties.json (file)
                            |_ head
                            |   |_ ../../../vertices/0 (symlik)
                            |_ tail
                                |_ ../../../vertices/1 (symlik)

        :param path: Edges Path to walk and import.
        :type path: :class:`str`
        :raises KeyError: If the head or tail of the edge being
            imported is unknown.
        """
        # walk the path loading edges that are found.
        for label in os.listdir(path):

            label_path = os.path.join(path, label)

            # skip over files because we are only looking for directories.
            if os.path.isfile(label_path):
                continue

            # run over all the edge id's that we can find
            # and loading the properties if found.
            for dirname in sorted(os.listdir(label_path)):
                properties = {}
                properties_filename = os.path.join(
                    label_path,
                    dirname,
                    "properties.json"
                )

                properties = {}
                if os.path.exists(properties_filename):
                    with open(properties_filename) as properties_filehandle:
                        properties = json.load(properties_filehandle)

                head_id = os.listdir(
                    os.path.join(
                        label_path,
                        dirname,
                        "head"
                    )
                )[0]

                head = self.get_vertex(int(head_id))

                tail_id = os.listdir(
                    os.path.join(
                        label_path,
                        dirname,
                        "tail"
                    )
                )[0]

                tail = self.get_vertex(int(tail_id))

                # reset the id to the id being loaded.
                self._id_tracker.eid = int(dirname)
                super(PersistentGraph, self).add_edge(
                    head,
                    label,
                    tail,
                    **properties
                )

    def _create_vertex_skel(self, path):
        """
        Create a vertex skeleton path.

        :param path: Path to create the vertex skeleton structure in.
        :type path: :class:`str`
        """
        self.vertices_path = os.path.join(path, "vertices")
        os.makedirs(self.vertices_path)

        self.vertices_constraints_path = os.path.join(
            self.vertices_path, "constraints.json"
        )
        with open(self.vertices_constraints_path, "w") as constraint_fh:
            constraint_fh.write("{}")

    def _create_edge_skel(self, path):
        """
        Create a edge skeleton path.

        :param path: Path to create the edge skeleton structure in.
        :type path: :class:`str`
        """
        self.edges_path = os.path.join(path, "edges")
        os.makedirs(self.edges_path)

    def _create_path(self):
        """
        Create a complete database skeleton path.
        """
        self.path = mkdtemp(suffix="-ruruki-db")
        logging.info("Created temporary graph db path %r", self.path)
        self._create_vertex_skel(self.path)
        self._create_edge_skel(self.path)

    def add_vertex_constraint(self, label, key):
        super(PersistentGraph, self).add_vertex_constraint(label, key)
        with open(self.vertices_constraints_path, "w") as constraint_fh:
            json.dump(
                self.get_vertex_constraints(),
                constraint_fh,
                indent=4,
            )

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
        head_path = os.path.join(edge_path, "head")
        tail_path = os.path.join(edge_path, "tail")

        os.makedirs(edge_path)
        os.makedirs(head_path)
        os.makedirs(tail_path)

        edge.set_property(_path=edge_path)

        os.symlink(
            head.properties["_path"],
            os.path.join(head_path, str(head.ident))
        )

        os.symlink(
            tail.properties["_path"],
            os.path.join(tail_path, str(tail.ident))
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
            "properties.json"
        )

        with open(properties_file, "w") as prop_file:
            json.dump(
                dict(
                    (k, v)
                    for k, v in entity.properties.items()
                    if k != "_path"
                ),
                prop_file,
                indent=4
            )

    def remove_edge(self, edge):
        shutil.rmtree(edge.properties["_path"])
        super(PersistentGraph, self).remove_edge(edge)

    def remove_vertex(self, vertex):
        shutil.rmtree(vertex.properties["_path"])
        super(PersistentGraph, self).remove_vertex(vertex)
