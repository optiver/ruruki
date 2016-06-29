"""
Graph implementations
"""
from collections import defaultdict
import json
import logging
import os
import shutil
from ruruki import interfaces
from ruruki.locks import DirectoryLock
from ruruki.entities import Vertex, Edge, PersistentVertex, PersistentEdge
from ruruki.entities import EntitySet


def _search_for_edge_ids(path):
    """
    Internal helper function to search for edges identity numbers
    based in the directories and the head and tail vertices identity
    numbers.

    :param path: Edges Path to find number directories.
    :type path: :class:`str`
    :return: Yields the integer number, head id, label, tail id and the
        properties file path if found.
    :rtype: Iterator of :class:`tuple`
        (
            :class:`int`, :class:`int`, :class:`str`,
            :class:`int`, :class:`str` or :obj:`None`
        )
    """
    for label in os.listdir(path):

        label_path = os.path.join(path, label)

        # skip over files because we are only looking for directories.
        if os.path.isfile(label_path):
            continue

        # run over all the edge id's that we can find
        # and loading the properties if found.
        for each in os.listdir(label_path):
            try:
                ident = int(each)
            except ValueError:
                logging.error(
                    "%r is not a expected edge id number, skipping edge import",
                    each
                )
                continue

            propfile = os.path.join(
                label_path,
                each,
                "properties.json"
            )

            try:
                head_id = int(
                    os.listdir(
                        os.path.join(
                            label_path,
                            each,
                            "head"
                        )
                    )[0]
                )
            except ValueError:
                logging.error(
                    "%r is not a expected head id number, skipping edge import",
                    each
                )
                continue

            try:
                tail_id = int(
                    os.listdir(
                        os.path.join(
                            label_path,
                            each,
                            "tail"
                        )
                    )[0]
                )
            except ValueError:
                logging.error(
                    "%r is not a expected tail id number, skipping edge import",
                    each
                )
                continue

            yield (
                ident,
                head_id,
                label,
                tail_id,
                propfile if os.path.isfile(propfile) else None
            )


def _search_for_vertex_id(path):
    """
    Internal helper function to search for vertices identity numbers
    based in the directories.

    :param path: Vertice path to find number directories.
    :type path: :class:`str`
    :return: Yields the integer number, label and the properties file path
        if found.
    :rtype: Iterator of :class:`tuple`
        (:class:`int`, :class:`str`, :class:`str` or :obj:`None`)
    """
    for label in os.listdir(path):
        label_path = os.path.join(path, label)

        # skip over files because we are only looking for directories.
        if os.path.isfile(label_path):
            continue

        # run over all the vertice id's that we can find
        # and loading the properties if found.
        for each in os.listdir(label_path):
            try:
                ident = int(each)
            except ValueError:
                logging.error(
                    "%r is not a expected vertex id number, skipping",
                    each
                )
                continue

            propfile = os.path.join(
                label_path,
                str(ident),
                "properties.json"
            )

            yield ident, label, propfile if os.path.isfile(propfile) else None


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
        self._vclass = Vertex
        self._eclass = Edge
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
        if not label and not kwargs:
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
        vertices = self.vertices.filter(label, **kwargs)
        if len(vertices) > 1:
            raise interfaces.MultipleFoundExpectedOne(
                "Multiple vertices found when one expected."
            )
        elif len(vertices) == 1:
            return vertices.all()[0]

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

    def append_edge(self, edge):
        head = edge.head
        tail = edge.tail

        self.append_vertex(head)
        self.append_vertex(tail)

        if edge.graph is not None and edge.graph is not self:
            raise interfaces.DatabaseException(
                "Can not append edge {} which is already bound to "
                "anther graph instance.".format(edge)
            )

        if edge in self:
            return edge

        if edge.ident is not None:
            raise interfaces.EntityIDError(
                "Edge {} already has it identity number set.".format(edge)
            )

        self._edge_constraint_violated(edge)
        self._econstraints[(head, edge.label, tail)] = edge
        self.bind_to_graph(edge)
        self.edges.add(edge)
        head.out_edges.add(edge)
        tail.in_edges.add(edge)
        return edge

    def append_vertex(self, vertex):
        if vertex.graph is not None and vertex.graph is not self:
            raise interfaces.DatabaseException(
                "Can not append vertex {} which is already bound to "
                "anther graph instance.".format(vertex)
            )

        if vertex in self:
            return vertex

        if vertex.ident is not None:
            raise interfaces.EntityIDError(
                "Vertex {} already has it identity number set.".format(vertex)
            )


        self._vertex_constraint_violated(vertex)
        if vertex.label in self._vconstraints:
            for key in self._vconstraints[vertex.label]:
                if key in vertex.properties:
                    self._vconstraints[vertex.label][key].add(vertex)

        self.bind_to_graph(vertex)
        self.vertices.add(vertex)
        return vertex

    def add_edge(self, head, label, tail, **kwargs):
        edge = self._eclass(head, label, tail, **kwargs)
        return self.append_edge(edge)

    def add_vertex(self, label=None, **kwargs):
        vertex = self._vclass(label=label, **kwargs)
        return self.append_vertex(vertex)

    def _vertex_constraint_violated(self, vertex, **kwargs):
        """
        Check if the given vertex violates any of the constraints.

        :param vertex: vertex that you are checking for constraint violations.
        :type vertex: :class:`~.IVertex`
        :param kwargs: Additional properties.
        :type kwargs: :class:`dict`
        :raises ConstraintViolation: Raised if you a constraint violation has
            been found.
        """
        key_index = self._vconstraints.get(vertex.label, {})

        # first check the entity properties for constraint violations
        # Then check any additional properties for constraint violations.
        # Additional properties are for cases like `.set_property`
        for props in [vertex.properties, kwargs]:
            for key, value in props.items():
                if key not in key_index:
                    continue

                for indexed_entity in key_index[key]:
                    if indexed_entity != vertex:
                        if indexed_entity.properties[key] == value:
                            raise interfaces.ConstraintViolation(
                                "{!r} violated constraint {!r}".format(
                                    vertex, key
                                )
                            )

    # todo: add in property constraint violation checks for edges
    def _edge_constraint_violated(self, edge):
        """
        Check if the given edge violates any of the constraints.

        :param edge: Edge that you are checking for constraint violations.
        :type edge: :class:`~.IEdge`
        :raises ConstraintViolation: Raised if you a constraint violation has
            been found.
        """
        if (edge.head, edge.label, edge.tail) in self._econstraints:
            raise interfaces.ConstraintViolation(
                "Duplicate {0!r} edges between head {1!r} and tail {2!r} "
                "is not allowed".format(
                    edge.label,
                    edge.head,
                    edge.tail,
                )
            )

    def set_property(self, entity, **kwargs):
        if entity not in self:
            raise interfaces.UnknownEntityError(
                "Unknown entity {0!r}".format(entity)
            )

        if isinstance(entity, interfaces.IVertex):
            self._vertex_constraint_violated(entity, **kwargs)
            self.vertices.update_index(entity, **kwargs)

        if isinstance(entity, interfaces.IEdge):
            # edge property constraints are not supported at this stage.
            # todo: enable once edge property constraints are added.
            # self._edge_constraint_violated(entity)
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

    .. note::

        Verices and Edges ID's are retained when the path is loaded.

    .. warning::

        Use this persistent graph if performance is not important.
        There is a performance hit due to the extra disk I/O overhead
        when doing many writing/updating operations.

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
                         |   |_ 0 -> ../../../vertices/0 (symlink)
                         |_ tail
                             |_ 1 -> ../../../vertices/1 (symlink)

    :param path: Path to ruruki graph data on disk.
    :param auto_create: If True, then missing ``vertices`` or ``edges``
        directories will be created.
    :type auto_create: :class:`bool`
    :type path: :class:`str`
    :raises DatabasePathLocked: If the path is already locked by another
        persistence graph instance.
    """
    def __init__(self, path, auto_create=True):
        super(PersistentGraph, self).__init__()
        self._vclass = PersistentVertex
        self._eclass = PersistentEdge

        self._lock = DirectoryLock(path)
        try:
            self._lock.acquire()
        except interfaces.AcquireError:
            logging.exception(
                "Path %r is already owned by another graph.",
                path
            )
            raise interfaces.DatabasePathLocked(
                "Path {0!r} is already locked by anotherr persistent graph "
                "instance.".format(path)
            )

        self.path = path
        self.vertices_path = os.path.join(self.path, "vertices")
        self.edges_path = os.path.join(self.path, "edges")
        self.vertices_constraints_path = os.path.join(
            self.vertices_path, "constraints.json"
        )

        if auto_create is True:
            self._auto_create()

        self._load_from_path()

    def _auto_create(self):
        """
        Check that ``vertices`` and ``edges`` directories exists, and if
        not create them and all the other required files and folders.
        """
        status = [
            os.path.exists(self.vertices_path),
            os.path.exists(self.edges_path),
        ]

        if not all(status):
            self._create_vertex_skel(self.path)
            self._create_edge_skel(self.path)

    def _load_from_path(self):
        """
        Scan through the given database path and load/import up all the
        relevant vertices, vertices constraints, and edges.
        """
        logging.info("Loading graph data from %r", self.path)
        self._load_vconstraints_from_path(self.vertices_constraints_path)
        self._load_vertices_from_path(self.vertices_path)
        self._load_edges_from_path(self.edges_path)
        logging.info("Completed %r graph import", self.path)

    def _load_vconstraints_from_path(self, path):
        """
        Open, parse and load the vertices constraints.

        :param path: Vertices constraints file to open, parse and import.
        :type path: :class:`str`
        """
        logging.info("Loading vertices constraints %r", path)
        with open(path) as vconstraints_fh:
            for each in json.load(vconstraints_fh):
                self.add_vertex_constraint(each["label"], each["key"])

    def _load_vertices_from_path(self, path):
        """
        Scan through the given path and load/import all the vertices.

        .. code::

            path
               |_ vertices
                    |_ constraints.json (file)
                    |_ labelA
                    |     |_ 0
                    |        |_ properties.json (file)
                    |
                    |_ labelB
                         |_ 1
                            |_ properties.json (file)

        :param path: Vertices Path to walk and import.
        :type path: :class:`str`
        """
        logging.info("Loading vertices from %r", path)
        sorted_to_import = sorted(
            _search_for_vertex_id(path),
            key=lambda x: x[0]
        )

        for ident, label, prop_file in sorted_to_import:
            properties = json.load(open(prop_file)) if prop_file else {}

            # reset the id to the id being loaded.
            self._id_tracker.vid = ident
            vertex = super(PersistentGraph, self).add_vertex(
                label, **properties
            )
            # due to pylint bug https://github.com/PyCQA/pylint/issues/379, we
            # need to disable assigning-non-slot errors
            vertex.path = os.path.join(path, label, str(ident))  # pylint: disable=assigning-non-slot

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
                            |   |_ 0 -> ../../../vertices/0 (symlink)
                            |_ tail
                                |_ 1 -> ../../../vertices/1 (symlink)

        :param path: Edges Path to walk and import.
        :type path: :class:`str`
        :raises KeyError: If the head or tail of the edge being
            imported is unknown.
        """
        logging.info("Loading edges from %r", path)
        sorted_to_import = sorted(
            _search_for_edge_ids(path),
            key=lambda x: x[0]
        )

        for ident, head_id, label, tail_id, prop_file in sorted_to_import:
            properties = json.load(open(prop_file)) if prop_file else {}
            head = self.get_vertex(head_id)
            tail = self.get_vertex(tail_id)

            # reset the id to the id being loaded.
            self._id_tracker.eid = ident
            edge = super(PersistentGraph, self).add_edge(
                head,
                label,
                tail,
                **properties
            )

            # due to pylint bug https://github.com/PyCQA/pylint/issues/379, we
            # need to disable assigning-non-slot errors
            edge.path = os.path.join(path, label, str(ident))  # pylint: disable=assigning-non-slot

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
            constraint_fh.write("[]")

    def _create_edge_skel(self, path):
        """
        Create a edge skeleton path.

        :param path: Path to create the edge skeleton structure in.
        :type path: :class:`str`
        """
        self.edges_path = os.path.join(path, "edges")
        os.makedirs(self.edges_path)

    def add_vertex_constraint(self, label, key):
        super(PersistentGraph, self).add_vertex_constraint(label, key)
        with open(self.vertices_constraints_path, "w") as constraint_fh:
            data = []
            for label, key in self.get_vertex_constraints():
                data.append({"label": label, "key": key})
            json.dump(data, constraint_fh, indent=4)

    def add_vertex(self, label=None, **kwargs):
        vertex = super(PersistentGraph, self).add_vertex(label, **kwargs)
        # due to pylint bug https://github.com/PyCQA/pylint/issues/379, we
        # need to disable assigning-non-slot errors
        vertex.path = os.path.join(self.vertices_path, label, str(vertex.ident))  # pylint: disable=assigning-non-slot
        os.makedirs(vertex.path)
        os.makedirs(os.path.join(vertex.path, "in-edges"))
        os.makedirs(os.path.join(vertex.path, "out-edges"))

        with open(os.path.join(vertex.path, "properties.json"), "w") as fh:
            json.dump(vertex.properties, fh)

        return vertex

    def add_edge(self, head, label, tail, **kwargs):
        edge = super(PersistentGraph, self).add_edge(
            head, label, tail, **kwargs
        )

        # due to pylint bug https://github.com/PyCQA/pylint/issues/379, we
        # need to disable assigning-non-slot errors
        edge.path = os.path.join(self.edges_path, label, str(edge.ident))  # pylint: disable=assigning-non-slot
        head_path = os.path.join(edge.path, "head")
        tail_path = os.path.join(edge.path, "tail")

        os.makedirs(edge.path)
        os.makedirs(head_path)
        os.makedirs(tail_path)

        with open(os.path.join(edge.path, "properties.json"), "w") as fh:
            json.dump(edge.properties, fh)

        os.symlink(head.path, os.path.join(head_path, str(head.ident)))
        os.symlink(tail.path, os.path.join(tail_path, str(tail.ident)))

        os.symlink(
            edge.path,
            os.path.join(
                head.path,
                "out-edges",
                str(edge.ident)
            )
        )

        os.symlink(
            edge.path,
            os.path.join(
                tail.path,
                "in-edges",
                str(edge.ident)
            )
        )

        return edge

    def set_property(self, entity, **kwargs):
        super(PersistentGraph, self).set_property(entity, **kwargs)

        # Update the properties to the properties file
        properties_file = os.path.join(
            entity.path,
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
        super(PersistentGraph, self).remove_edge(edge)
        shutil.rmtree(edge.path)

    def remove_vertex(self, vertex):
        super(PersistentGraph, self).remove_vertex(vertex)
        shutil.rmtree(vertex.path)

    def close(self):
        self._lock.release()
