"""
Entities
"""
from ruruki import interfaces


class Entity(interfaces.IEntity):
    """
    Base class for containing the common methods used for the other
    entities like vertices and edges.

    .. note::

        See :class:`~.IEntity` for doco.

    .. note::

        The properties can be accessed as if they are attributes
        directly by prepending ``prop__`` to the key.

        .. code-block:: python

            >>> e = Entity("Entity", name="Example")
            >>> e.prop__name
            'Example'

    :param label: :class:`.IEntity` label.
    :type ident: :class:`str` or :obj:`None`
    :param kwargs: Additional properties for the :class:`.IEntity`.
    :type kwargs: :class:`str`=value or :class:`dict`
    """
    __slots__ = ["ident", "label", "properties", "graph"]

    def __init__(self, label=None, **kwargs):
        self.graph = None
        self.ident = None
        self.label = label
        self.properties = kwargs

    def is_bound(self):
        return self.graph is not None

    def remove_property(self, key):
        if key in self.properties:
            del self.properties[key]

    def _update_properties(self, kwargs):
        self.properties.update(kwargs)

    def set_property(self, **kwargs):
        if not kwargs:
            raise interfaces.EntityUpdateError(
                "Can not update with no key and values."
            )

        if self.is_bound():
            self.graph.set_property(self, **kwargs)
        self._update_properties(kwargs)

    def as_dict(self):
        return {
            "metadata": {
            },
            "id": self.ident,
            "label": self.label,
            "properties": self.properties,
        }

    def __getattribute__(self, name):
        if name.startswith("prop__"):
            _, key = name.split("prop__", 1)
            try:
                return self.properties[key]
            except KeyError:
                pass
        return super(Entity, self).__getattribute__(name)

    def __str__(self):
        return "<{0}> {1}".format(
            self.__class__.__name__, self.ident
        )

    def __repr__(self):  # pragma: no cover
        return "<{0}> ident: {1}, label: {2}, properties: {3}".format(
            self.__class__.__name__, self.ident, self.label, self.properties
        )


class Vertex(interfaces.IVertex, Entity):
    """
    Vertex/Node is the representation of a entity. It can be anything
    and contains properties for additional information.

    .. note::

        See :class:`~.IVertex` for doco.

    .. note::

        The properties can be accessed as if they are attributes
        directly by prepending ``prop__`` to the key.

        .. code-block:: python

            >>> v = Vertex("Person", name="Foo")
            >>> v.prop__name
            'Foo'

    :param label: :class:`.IEntity` label.
    :type ident: :class:`str` or :obj:`None`
    :param kwargs: Additional properties for the :class:`.IEntity`.
    :type kwargs: :class:`str`=value or :class:`dict`
    """
    __slots__ = ["in_edges", "out_edges"]

    def __init__(self, label=None, **kwargs):
        super(Vertex, self).__init__(label=label, **kwargs)
        self.in_edges = EntitySet()
        self.out_edges = EntitySet()

    def in_edge_count(self):
        return len(self.in_edges)

    def out_edge_count(self):
        return len(self.out_edges)

    def add_in_edge(self, vertex, label=None, **kwargs):
        # if the vertex is bound to a graph, then let the graph
        # handle the edge creation.
        if self.is_bound():
            return self.graph.add_edge(vertex, label, self, **kwargs)

        edge = Edge(vertex, label, self, **kwargs)
        self.in_edges.add(edge)
        return edge

    def add_out_edge(self, vertex, label, **kwargs):
        # if the vertex is bound to a graph, then let the graph
        # handle the edge creation.
        if self.is_bound():
            return self.graph.add_edge(self, label, vertex, **kwargs)

        edge = Edge(self, label, vertex, **kwargs)
        self.out_edges.add(edge)
        return edge

    def remove_edge(self, edge):
        head = edge.head
        tail = edge.tail
        if head == self:
            self.out_edges.remove(edge)
        elif tail == self:
            self.in_edges.remove(edge)
        else:
            raise interfaces.VertexError(
                "Unknown edge to this vertex: {}".format(edge)
            )

    def get_in_edges(self, label=None, **kwargs):
        return self.in_edges.filter(label, **kwargs)

    def get_out_edges(self, label=None, **kwargs):
        return self.out_edges.filter(label, **kwargs)

    def get_both_edges(self, label=None, **kwargs):
        edges = self.in_edges | self.out_edges
        return edges.filter(label, **kwargs)  # pylint: disable=no-member

    def get_in_vertices(self, label=None, **kwargs):
        vertices = [
            each.get_in_vertex() for each in self.get_in_edges()
        ]
        return EntitySet(vertices).filter(label, **kwargs)

    def get_out_vertices(self, label=None, **kwargs):
        vertices = [
            each.get_out_vertex() for each in self.get_out_edges()
        ]
        return EntitySet(vertices).filter(label, **kwargs)

    def get_both_vertices(self, label=None, **kwargs):
        in_set = self.get_in_vertices(label=label, **kwargs)
        out_set = self.get_out_vertices(label=label, **kwargs)
        return in_set | out_set

    def as_dict(self):
        return {
            "metadata": {
                "in_edge_count": self.in_edge_count(),
                "out_edge_count": self.out_edge_count(),
            },
            "id": self.ident,
            "label": self.label,
            "properties": self.properties,
        }


class PersistentVertex(Vertex):
    """
    Persistent Vertex behaves exactly the same as a :class:`~.Vertex` but has
    an additional path attribute which is the disk location.
    """
    __slots__ = ["path"]

    def __init__(self, *args, **kwargs):
        super(PersistentVertex, self).__init__(*args, **kwargs)
        self.path = None


class Edge(interfaces.IEdge, Entity):
    """
    Edge/Relationship is the representation of a relationship between two
    entities. A edge has properties for additional information.

    .. note::

        See :class:`~.IEdge` for doco.

    .. note::

        The properties can be accessed as if they are attributes
        directly by prepending ``prop__`` to the key.

        .. code-block:: python

            >>> v1 = Vertex("Person", name="Foo")
            >>> v2 = Vertex("Person", name="Bar")
            >>> e = Edge(v1, "knows", v2, since="school")
            >>> e.prop__since
            'school'

    :param head: Head :class:`.IVertex` of the edge.
    :type head: :class:`.IVertex`
    :param label: :class:`.IEntity` label.
    :type ident: :class:`str` or :obj:`None`
    :param tail: Tail :class:`.IVertex` of the edge.
    :type tail: :class:`.IVertex`
    :param kwargs: Additional properties for the :class:`.IEntity`.
    :type kwargs: :class:`str`=value or :class:`dict`
    """
    __slots__ = ["head", "tail"]

    def __init__(self, head, label, tail, **kwargs):
        super(Edge, self).__init__(label=label, **kwargs)
        self.head = head
        self.tail = tail

    def get_in_vertex(self):
        return self.head

    def get_out_vertex(self):
        return self.tail

    def as_dict(self):
        return {
            "metadata": {},
            "id": self.ident,
            "label": self.label,
            "head_id": self.head.ident,
            "tail_id": self.tail.ident,
            "properties": self.properties,
        }

    def __str__(self):  # pragma: no cover
        return "<{0}> ident: {1} [{3}-{2}-{4}]".format(
            self.__class__.__name__, self.ident, self.label,
            self.head.ident, self.tail.ident
        )

    def __repr__(self):  # pragma: no cover
        return (
            "<{0}> ident: {1}, label: {2}, properties: "
            "{3} [{4}-{2}-{5}]".format(
                self.__class__.__name__, self.ident, self.label,
                self.properties, self.head.ident, self.tail.ident
            )
        )


class PersistentEdge(Edge):
    """
    Persistent Edge behaves exactly the same as a :class:`~.Edge` but has an
    additional path attribute which is the disk location.
    """
    __slots__ = ["path"]

    def __init__(self, *args, **kwargs):
        super(PersistentEdge, self).__init__(*args, **kwargs)
        self.path = None


def _split_key_into_noun_verb(key):
    """
    Internal helper function that takes the key and splits it into the
    noun and verb, and returns the noun and verb.

    .. note::

        Example of a key with the special operator.

        key: name__contains
        return: name, contains

    :param key: Key that you are splitting into the noun and verb. The key
        should end with __<operator>
    :type key: :class:`str`
    :returns: Key name and the operator.
    :rtype: :class:`tuple` (:class:`str`, :class:`str` or :obj:`None`)
    """
    split = key.rsplit("__", 1)
    if len(split) == 2:
        return split[0], split[1]
    return key, None


def _contains(prop_value, cmp_value, ignore_case=False):
    """
    Helper function that take two arguments and checks if :param cmp_value:
    is in :param prop_value:.

    :param prop_value: Property value that you are checking.
    :type prop_value: :class:`str`
    :param cmp_value: Value that you are checking if it is in the property
        value.
    :type cmp_value: :class:`str`
    :param ignore_case: True to run using incase sensitive.
    :type ignore_case: :class:`bool`
    :returns: True if :param cmp_value: is in :param prop_value:
    :rtype: class:`bool`
    """
    if ignore_case is True:
        prop_value = prop_value.lower()
        cmp_value = cmp_value.lower()
    return cmp_value in prop_value


def _startswith(prop_value, cmp_value, ignore_case=False):
    """
    Helper function that take two arguments and checks if :param prop_value:
    startswith :param cmp_value:

    :param prop_value: Property value that you are checking.
    :type prop_value: :class:`str`
    :param cmp_value: Value that you are checking if it is in the property
        value startswith.
    :type cmp_value: :class:`str`
    :param ignore_case: True to run using incase sensitive.
    :type ignore_case: :class:`bool`
    :returns: True if :param prop_value: startswith :param cmp_value:
    :rtype: class:`bool`
    """
    if ignore_case is True:
        prop_value = prop_value.lower()
        cmp_value = cmp_value.lower()
    return prop_value.startswith(cmp_value)


def _endswith(prop_value, cmp_value, ignore_case=False):
    """
    Helper function that take two arguments and checks if :param prop_value:
    endswith :param cmp_value:

    :param prop_value: Property value that you are checking.
    :type prop_value: :class:`str`
    :param cmp_value: Value that you are checking if it is in the property
        value endswith.
    :type cmp_value: :class:`str`
    :param ignore_case: True to run using incase sensitive.
    :type ignore_case: :class:`bool`
    :returns: True if :param prop_value: endswith :param cmp_value:
    :rtype: class:`bool`
    """
    if ignore_case is True:
        prop_value = prop_value.lower()
        cmp_value = cmp_value.lower()
    return prop_value.endswith(cmp_value)


def _eq(prop_value, cmp_value, ignore_case=False):
    """
    Helper function that take two arguments and checks if :param prop_value:
    equals :param cmp_value:

    :param prop_value: Property value that you are checking.
    :type prop_value: :class:`str`
    :param cmp_value: Value that you are checking if they are equal.
    :type cmp_value: :class:`str`
    :param ignore_case: True to run using incase sensitive.
    :type ignore_case: :class:`bool`
    :returns: True if :param prop_value: and :param cmp_value: are
        equal.
    :rtype: class:`bool`
    """
    if ignore_case is True:
        prop_value = prop_value.lower()
        cmp_value = cmp_value.lower()
    return cmp_value == prop_value


def _ne(prop_value, cmp_value, ignore_case=False):
    """
    Helper function that take two arguments and checks if :param prop_value:
    is not equal to :param cmp_value:

    :param prop_value: Property value that you are checking.
    :type prop_value: :class:`str`
    :param cmp_value: Value that you are checking if they are not equal.
    :type cmp_value: :class:`str`
    :param ignore_case: True to run using incase sensitive.
    :type ignore_case: :class:`bool`
    :returns: True if :param prop_value: and :param cmp_value: are
        not equal.
    :rtype: class:`bool`
    """
    if ignore_case is True:
        prop_value = prop_value.lower()
        cmp_value = cmp_value.lower()
    return cmp_value != prop_value


OPERATORS = {
    "contains": _contains,
    "icontains": _contains,  # require to be called with ignore_case
    "startswith": _startswith,
    "istartswith": _startswith,  # require to be called with ignore_case
    "endswith": _endswith,
    "iendswith": _endswith,  # require to be called with ignore_case
    "le": lambda prop_value, value, ignore_case: value >= prop_value,
    "lt": lambda prop_value, value, ignore_case: value > prop_value,
    "ge": lambda prop_value, value, ignore_case: value <= prop_value,
    "gt": lambda prop_value, value, ignore_case: value < prop_value,
    "eq": _eq,
    "ieq": _eq,  # require to be called with ignore_case
    "ne": _ne,
    "ine": _ne,  # require to be called with ignore_case
}


class EntitySet(interfaces.IEntitySet):
    """
    EntitySet used for storing, filtering, and iterating over
    :class:`~.IEntity` objects.

    .. note::

        See :class:`~.IEntitySet` for documenation.

    :param entities: Entities being added to the set.
    :type entities: Iterable of :class:`.IEntity`
    """
    def __init__(self, entities=None):
        super(EntitySet, self).__init__()
        self._prop_reference = {}
        self._id_reference = {}

        if entities is not None:
            for entity in entities:
                self.add(entity)

    def all(self, label=None, **kwargs):
        return list(self.filter(label, **kwargs))

    def sorted(self, key=None, reverse=False):
        return sorted(self, key=key, reverse=reverse)

    def get_labels(self):
        return self._prop_reference.keys()

    def get_indexes(self):
        for label in self._prop_reference.iterkeys():
            for key in self._prop_reference[label].iterkeys():
                if not key.startswith("_all"):
                    yield label, key

    def get(self, ident):
        entity = self._id_reference.get(ident)
        if entity is None:
            raise KeyError("No such id {0!r} exists.".format(ident))
        return entity

    def update_index(self, entity, **kwargs):
        collection = self._prop_reference.setdefault(
            entity.label,
            {"_all": set()},
        )

        collection["_all"].add(entity)
        # Add in a indexed property reference.
        for key in kwargs:
            collection.setdefault(key, set()).add(entity)

    def add(self, entity):
        if entity.ident in self._id_reference:
            if entity != self._id_reference[entity.ident]:
                raise KeyError(
                    "Conflict: {0} (current) <-> {1} (conflict)".format(
                        self._id_reference[entity.ident], entity
                    )
                )

        # Add in a reference for fast id search.
        self._id_reference[entity.ident] = entity
        self.update_index(entity, **entity.properties)

        super(EntitySet, self).add(entity)

    def remove(self, entity):
        if entity.ident in self._id_reference:
            del self._id_reference[entity.ident]
        else:
            raise KeyError("No such id {0!r} exists.".format(entity.ident))

        collection = self._prop_reference[entity.label]
        for key in entity.properties.iterkeys():
            if key in collection:
                collection[key].discard(entity)

        super(EntitySet, self).remove(entity)

    def filter(self, label=None, **kwargs):  # pylint: disable=too-many-locals,too-many-branches
        if label is None and not kwargs:
            return self

        if label and not kwargs:
            if label in self._prop_reference:
                return EntitySet(entities=self._prop_reference[label]["_all"])

        keys_values = kwargs.items()
        get_func = OPERATORS.get
        noun_verb_cache = {
            key: _split_key_into_noun_verb(key)
            for key, value in keys_values
        }

        elements = set()
        if label is None:
            elements = set(self._id_reference.values())
        elif label in self._prop_reference:
            for key, value in keys_values:
                key, verb = noun_verb_cache[key]
                if key not in self._prop_reference[label]:
                    return EntitySet()
                elements = elements | self._prop_reference[label][key]

        container = EntitySet()
        for entity in elements:
            mismatch = False
            for key, value in keys_values:
                key, verb = noun_verb_cache[key]
                icase = verb[0] == "i" if verb else False
                func = get_func(verb)
                if key not in entity.properties:
                    mismatch = True
                    break
                prop_value = entity.properties[key]
                if prop_value is None:
                    mismatch = True
                    break
                if not func:
                    if prop_value != value:
                        mismatch = True
                        break
                elif not func(prop_value, value, icase):
                    mismatch = True
                    break

            if not mismatch:
                container.add(entity)

        return container
