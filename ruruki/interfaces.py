"""
Database interfaces.
"""
import abc
from collections import MutableSet
from collections import namedtuple


class VertexTuple(namedtuple("VertexTuple", ["label", "properties"])):
    """
    A Vertex tuple is a vertex representation which can be converted into
    a :class:`IVertex`

    :param label: Vertex label.
    :type label: :class:`str` or :obj:`None`
    :param properties: Vertex properties.
    :type properties: :class:`dict`
    """
    __slots__ = ()


# Exceptions
class RurukiException(Exception):
    """
    Ruruki base exception.
    """

class LockException(RurukiException):
    """
    Base lock exception class.
    """


class AcquireError(LockException):
    """
    Raised if there was a problem acquiring a lock.
    """


class ReleaseError(LockException):
    """
    Raised if there was a problem releasing a lock.
    """


class EntityException(RurukiException):
    """
    Base container exception class.
    """


class EntitySetException(EntityException):
    """
    Base container exception class.
    """


class EntityUpdateError(EntityException):
    """
    Raised if the entity failed to update its property.
    """


class DumplicateConstraintError(EntitySetException):
    """
    Raise if you are trying to add a constraint that already exists.
    """


class DatabaseException(RurukiException):
    """
    Database Exception.
    """


class DatabasePathLocked(DatabaseException):
    """
    Raised the path used by a persistent graph is already locked/owned
    by another persistent graph instance.
    """


class UnknownEntityError(DatabaseException):
    """
    Raised if the entity is unknown to the database.
    """


class ConstraintViolation(DatabaseException):
    """
    Raise if a constraint violation is found.
    """


class MultipleFoundExpectedOne(DatabaseException):
    """
    Raised when calling :meth:`.get_or_create_vertex`
    or :meth:`.get_or_create_edge` and multiple entities are found.
    """


class VertexError(DatabaseException):
    """
    Generic vertex exception.
    """


class EntityIDError(DatabaseException):
    """
    Raised when there is some sort of issue regarding the identity number
    of the entity.
    """

class VertexBoundByEdges(VertexError):
    """
    Raised when you are trying to remove a vertex that will is bound to
    another vertex via a edge.
    """


# Interfaces
class IGraph(object):
    """
    Interface for a property graph database.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self, file_handler):
        """
        Load and import data into the database. Data should be in a JSON
        format.

        .. note::

            Id's are not retained and are regenerated. This allows you to
            load multiple dumps into the same graph.

        :param file_handler: A file-like object that, when read,
            produces JSON data describing a graph.
            The JSON data should be compatible with that produced by
            :meth:`~.IGraph.dump`.
        :param file_handler: :class:`file`
        """

    @abc.abstractmethod
    def dump(self, file_handler):
        """
        Export the database to a file handler.

        :param file_handler: A writable file-like object; a description of
            this graph will be written to this file encoded as JSON data
            that can be read back later with :meth:`~.IGraph.load`.
        :param file_handler: :class:`file`
        """

    @abc.abstractmethod
    def bind_to_graph(self, entity):
        """
        Bind an entity to the graph and generate and set a unique id on the
        entity.

        :param entity: Entity that you are binding to the graph.
        :type entity: :class:`~.IEntity`
        :raises UnknownEntityError: Is raised if the entity is not a instance
            if a :class:`~.IVertex` or :class:`~.IEdge`.
        """

    @abc.abstractmethod
    def add_vertex_constraint(self, label, key):
        """
        Add a constraint to ensure uniqueness for a particular label and
        property key.

        :param label: Vertex label which the constraint is meant for.
        :type label: :class:`str`
        :param key: Vertex property key used to ensure uniqueness.
        :type key: :class:`str`
        """

    @abc.abstractmethod
    def get_vertex_constraints(self):
        """
        Return all the known vertex constraints.

        :return: Distinct label and key pairs to
            :meth:`~.IGraph.add_vertex_constraint`.
        :rtype: Iterable of
            :class:`tuple` of label :class:`str`, key :class:`str`
        """

    @abc.abstractmethod
    def get_or_create_edge(self, head, label, tail, **kwargs):
        """
        Get or create a unique directed edge.

        .. note::

            If you wish to add in a unique undirected edge, you should add a
            directed edge in each direction.

            If ``head`` or ``tail`` is a :class:`tuple`, then
            :meth:`~.get_or_create_vertex` will always be called to create
            the vertex.


        :param head: Head vertex.
        :type head: :class:`~.IVertex` or :class:`tuple` of
            label :class:`str` and properties :class:`dict`
        :param label: Edge label.
        :type label: :class:`str`
        :param tail: Tail vertex.
        :type tail: :class:`~.IVertex` or :class:`tuple` of
            label :class:`str` and properties :class:`dict`
        :param kwargs: Property key and values to set on the new created edge.
        :type kwargs: :class:`str`, value.
        :returns: Added edge.
        :rtype: :class:`~.IEdge`
        """

    @abc.abstractmethod
    def get_or_create_vertex(self, label=None, **kwargs):
        """
        Get or create a unique vertex.

        .. note::

            Constraints will always be applied first when searching for
            vertices.

        :param label: Vertex label.
        :type label: :class:`str` or :obj:`None`
        :param kwargs: Property key and values to set on the new created
            vertex.
        :type kwargs: :class:`str`, value.
        :returns: Added vertex.
        :rtype: :class:`~.IVertex`
        """

    @abc.abstractmethod
    def append_edge(self, edge):
        """
        Append the edge to the graph.

        .. note::

            The edge that you are appending to the graph should have
            :py:attr:`~.IEntity.ident` set to :obj:`None`, so that the
            :class:`~.IGraph` can manage what the identity number should be.

        :param edge: Edge that should be appended to the graph.
        :type edge: :class:`~.IEdge`
        :raises ConstraintViolation: Raised if you are trying to create a
            duplicate edge between head and tail.
        :raises EntityIDError: If the edge already has a identity number set.
        :raises DatabaseError: If the edge already is already bound to
            anther :class:`~.IGraph`.
        :returns: The edge after it has been appended to the graph.
        :rtype: :class:`~.IEdge`
        """

    @abc.abstractmethod
    def append_vertex(self, vertex):
        """
        Append the vertex to the graph.

        .. note::

            The vertex that you are appending to the graph should have
            :py:attr:`~.IEntity.ident` set to :obj:`None`, so that the
            :class:`~.IGraph` can manage what the identity number should be.

        :param vertex: Vertex that should be appended to the graph.
        :type vertex: :class:`~.IVertex`
        :raises ConstraintViolation: Raised if you are appending a new vertex
            that violates a constraint.
        :raises EntityIDError: If the vertex already has a identity number set.
        :raises DatabaseError: If the vertex already is already bound to
            anther :class:`~.IGraph`.
        :returns: The vertex after it has been appended to the graph.
        :rtype: :class:`~.IVertex`
        """

    @abc.abstractmethod
    def add_edge(self, head, label, tail, **kwargs):
        """
        Add an directed edge to the graph.

        .. note::

            If you wish to add in a undirected edge, you should add a
            directed edge in each direction.

        :param head: Head vertex.
        :type head: :class:`~.IVertex`
        :param label: Edge label.
        :type label: :class:`str`
        :param tail: Tail vertex.
        :type tail: :class:`~.IVertex`
        :param kwargs: Property key and values to set on the new created edge.
        :type kwargs: :class:`str`, value.
        :raises ConstraintViolation: Raised if you are trying to create a
            duplicate edge between head and tail.
        :returns: Added edge.
        :rtype: :class:`~.IEdge`
        """

    @abc.abstractmethod
    def add_vertex(self, label=None, **kwargs):
        """
        Create a new vertex, add it to the graph, and return the newly
        created vertex.

        :param label: Vertex label.
        :type label: :class:`str` or :obj:`None`
        :param kwargs: Property key and values to set on the new created
            vertex.
        :type kwargs: :class:`str`, value.
        :raises ConstraintViolation: Raised if you are adding a new vertex
            that violates a constraint.
        :returns: Added vertex.
        :rtype: :class:`~.IVertex`
        """

    @abc.abstractmethod
    def set_property(self, entity, **kwargs):
        """
        Set or update the entities property key and values.

        :param kwargs: Property key and values to set on the new created
            vertex.
        :type kwargs: :class:`str`, value.
        :raises ConstraintViolation: A constraint violation is raised when
            you are updating the properties of a entity and you already have
            a entity with the constrained property value.
        :raises UnknownEntityError: If you are trying to update a property
            on a :class:`~.IEntity` that is not known in the database.
        :raises TypeError: If the entity that you are trying to update is
            not supported by the database. Property updates only support
            :class:`~.Ivertex` and :class:`~.IEdge`.
        """

    @abc.abstractmethod
    def get_edge(self, id_num):
        """
        Return the edge referenced by the provided object identifier.

        :param id_num: Edge identity number.
        :type id_num: :class:`int`
        :returns: Added edge.
        :rtype: :class:`~.IEdge`
        """

    @abc.abstractmethod
    def get_edges(self, head=None, label=None, tail=None, **kwargs):
        """
        Return an iterable of all the edges in the graph that have a
        particular key/value property.

        .. note::

            See :meth:`.IEntitySet.filter` for filtering options.

        :param head: Head vertex of the edge. If :obj:`None` then
            heads will be ignored.
        :type head: :class:`~.IVertex`
        :param label: Edge label. If :obj:`None`
            then all edges will be checked for key and value.
        :type label: :class:`str` or :obj:`None`
        :param tail: Tail vertex of the edge. If :obj:`None` then
            tails will be ignored.
        :type tail: :class:`~.IVertex`
        :param kwargs: Property key and value.
        :type kwargs: :class:`str` and value.
        :returns: :class:`~.IEdge` that matched the filter criteria.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def get_vertex(self, id_num):
        """
        Return the vertex referenced by the provided object identifier.

        :param id_num: Vertex identity number.
        :type id_num: :class:`int`
        :returns: Vertex that has the identity number.
        :rtype: :class:`~.IVertex`
        """

    @abc.abstractmethod
    def get_vertices(self, label=None, **kwargs):
        """
        Return all the vertices in the graph that have a particular
        key/value property.

        .. note::

            See :meth:`.IEntitySet.filter` for filtering options.

        :param label: Vertice label. If :obj:`None`
            then all vertices will be checked for key and value.
        :param label: :class:`str` or :obj:`None`
        :param kwargs: Property key and value.
        :type kwargs: :class:`str` and value.
        :returns: :class:`~.IVertex` that matched the filter criteria.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def remove_edge(self, edge):
        """
        Remove the provided edge from the graph.

        .. note::

            Removing a edge does **not** remove the head or tail vertices,
            but only the edge between them.

        :param edge: Remove a edge/relationship.
        :type edge: :class:`~.IEdge`
        """

    @abc.abstractmethod
    def remove_vertex(self, vertex):
        """
        Remove the provided vertex from the graph.

        :param vertex: Remove a vertex/node.
        :type vertex: :class:`~.IVertex`
        :raises VertexBoundByEdges: Raised if you are trying to remove
            a vertex that is still bound or attached to another vertex
            via edge.
        """

    @abc.abstractmethod
    def close(self):
        """
        Close the instance.
        """


class IEntity(object):
    """
    Base interface for a vertex/node and edge/relationship.

    .. note::

        Identity numbers are :obj:`None` by default. They are set
        by the :meth:`~.IGraph.bind_to_graph` when they are bound to the
        a graph. If using :class:`~.IEntity` and :class:`~.IEntitySet` without
        a bound graph, you will need to manually set the `ident` yourself.

        :class:`~.IDGenerator` can help you with assigning id's to vertices
        and edges.
    """
    __slots__ = []
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def is_bound(self):
        """
        Return True if the entity is bound to a graph.

        :returns: True is the entity is bound to a :class:`~.IGraph`
        :rtype: :class:`bool`
        """

    @abc.abstractmethod
    def remove_property(self, key):
        """
        Un-assigns a property key with its value.

        :param key: Key that you are removing.
        :type key: :class:`str`
        """

    @abc.abstractmethod
    def set_property(self, **kwargs):
        """
        Assign or update a property.

        :param kwargs: Key and value pairs.
        :type kwargs: key :class:`str` and value.
        """

    @abc.abstractmethod
    def as_dict(self):
        """
        Return the entity as a dictionary representation.

        :returns: The entity as a dictionary representation.
        :rtype: :class:`dict`
        """


class IVertex(IEntity):
    """
    Interface for a vertex/node.
    """
    __slots__ = []

    @abc.abstractmethod
    def add_in_edge(self, vertex, label=None, **kwargs):
        """
        Add and create an incoming edge between the two vertices.

        :param vertex: Edge the vertex is attached to.
        :type vertex: :class:`~.IVertex`
        :param label: Label for the edge being created.
        :type label: :class:`str`
        :param kwargs: Key and values for the edges properties.
        :type kwargs: :class:`str` and value
        """

    @abc.abstractmethod
    def add_out_edge(self, vertex, label=None, **kwargs):
        """
        Add and create an outgoing edge between the two vertices.

        :param vertex: Edge the vertex is attached to.
        :type vertex: :class:`~.IVertex`
        :param label: Label for the edge being created.
        :type label: :class:`str`
        :param kwargs: Edges property key and value pairs.
        :type kwargs: key :class:`str` and value.
        """

    @abc.abstractmethod
    def remove_edge(self, edge):
        """
        Remove a :class:`~.IEdge` from
        the vertex if it exists.

        :param edge: Edge that you are removing from the vertex.
        :type edge: :class:`~.IEdge`
        :raises KeyError: KeyError is raised if you are trying to remove
            an edge that is not found or does not exist.
        """

    @abc.abstractmethod
    def get_in_edges(self, label=None, **kwargs):
        """
        Return all the ``in`` edges to the vertex.

        :param label: Edge label.
            If :obj:`None`, all edges will be returned.
        :type label: :class:`str`
        :param kwargs: Edges property key and value pairs.
        :type kwargs: key :class:`str` and value.
        :returns: New :class:`~.IEntitySet` with filtered entities.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def get_out_edges(self, label=None, **kwargs):
        """
        Return all the ``out`` edges to the vertex.

        :param label: Edge label.
            If :obj:`None`, all edges will be returned.
        :type label: :class:`str`
        :param kwargs: Edge property key and value pairs.
        :type kwargs: key :class:`str` and value.
        :returns: New :class:`~.IEntitySet` with filtered entities.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def out_edge_count(self):
        """
        Return the total number of out edges.

        :returns: Total number of ``out`` edges.
        :rtype: :class:`int`
        """

    @abc.abstractmethod
    def in_edge_count(self):
        """
        Return the total number of in edges.

        :returns: Total number of ``in`` edges.
        :rtype: :class:`int`
        """

    @abc.abstractmethod
    def get_both_edges(self, label=None, **kwargs):
        """
        Return both ``in`` and ``out`` edges to the vertex.

        :param label: Edge label.
            If :obj:`None`, all edges will be returned.
        :type label: :class:`str`
        :param kwargs: Edge property key and value pairs.
        :type kwargs: key :class:`str` and value.
        :returns: New :class:`~.IEntitySet` with filtered entities.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def get_in_vertices(self, label=None, **kwargs):
        """
        Return the ``in`` vertices adjacent to the vertex according to the
        edge.

        :param label: Vertices label.
            If :obj:`None`, all edges will be returned.
        :type label: :class:`str`
        :param kwargs: Vertices property key and value pairs.
        :type kwargs: key :class:`str` and value.
        :returns: New :class:`~.IEntitySet` with filtered entities.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def get_out_vertices(self, label=None, **kwargs):
        """
        Return the ``out`` vertices adjacent to the vertex according to the
        edge.

        :param label: Vertices label.
            If :obj:`None`, all edges will be returned.
        :type label: :class:`str`
        :param kwargs: Vertices property key and value pairs.
        :type kwargs: key :class:`str` and value.
        :returns: New :class:`~.IEntitySet` with filtered entities.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def get_both_vertices(self, label=None, **kwargs):
        """
        Return the ``in`` and ``out`` vertices adjacent to the vertex
        according to the edges.

        :param label: Vertices label.
            If :obj:`None`, all edges will be returned.
        :type label: :class:`str`
        :param kwargs: Vertices property key and value pair.
        :type kwargs: key :class:`str` and value.
        :returns: New :class:`~.IEntitySet` with filtered entities.
        :rtype: :class:`~.IEntitySet`
        """


class IEdge(IEntity):
    """
    Interface for a edge/relationship.
    """
    __slots__ = []

    @abc.abstractmethod
    def get_in_vertex(self):
        """
        Return the ``in/head`` vertex.

        :returns: ``In`` vertex.
        :rtype: :class:`~.IVertex`
        """

    @abc.abstractmethod
    def get_out_vertex(self):
        """
        Return the ``out/tail`` vertex.

        :returns: ``Out`` vertex.
        :rtype: :class:`~.IVertex`
        """


class IEntitySet(MutableSet):
    """
    Interface for a entity containers.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.entities = set()

    def __len__(self):
        return len(self.entities)

    def __contains__(self, entity):
        return entity in self.entities

    def __iter__(self):
        return self.entities.__iter__()

    def add(self, entity):
        """
        Add a unique entity to the set.

        :param entity: Unique entity being added to the set.
        :type entity: :class:`~.IEntity`
        :raises KeyError: KeyError is raised if the entity being added
            to the set has a :attr:`~.Entity.ident` conflict with an existing
            :class:`~.IEntity`
        """
        self.entities.add(entity)

    def discard(self, entity):
        """
        Remove a entity from the current set.

        :param entity: Entity to be removed from the set.
        :type entity: :class:`~.IEntity`
        :raises KeyError: KeyError is raised if the entity being discared
            does not exists in the set.
        """
        self.entities.discard(entity)

    def remove(self, entity):
        """
        Like :meth:`.discard`, remove a entity from the current set.

        :param entity: Entity to be removed from the set.
        :type entity: :class:`~.IEntity`
        :raises KeyError: KeyError is raised if the entity being removed
            does not exists in the set.
        """
        self.discard(entity)

    @abc.abstractmethod
    def get_indexes(self):
        """
        Return all the index labels and properties.

        :returns: All the index label and property keys.
        :rtype: Iterable of :class:`tuple` of :class:`str`, :class:`str`
        """

    @abc.abstractmethod
    def get_labels(self):
        """
        Return labels known to the entity set.

        :returns: All the the labels known to the entity set.
        :rtype: Iterable of :class:`str`
        """

    @abc.abstractmethod
    def get(self, ident):
        """
        Return the :class:`.IEntity` that has the identification number
        supplied by parameter `ident`

        :param ident: Identification number.
        :type ident: :class:`int`
        :raises KeyError: Raised if there are no :class:`.IEntity` that
            has the given identification number supplied by parameter `ident`.
        :returns: The :class:`.IEntity` that has the identification number
            supplied by parameter `indent`
        :rtype: Iterable of :class:`str`
        """

    @abc.abstractmethod
    def update_index(self, entity, **kwargs):
        """
        Update the index with the new property keys.

        :param entity: Entity with a set of properties that need to be
            indexed.
        :type entity: :class:`~.IEntity`
        :param kwargs: Property key and values to set on the new created
            vertex.
        :type kwargs: :class:`str`, value.
        """

    @abc.abstractmethod
    def filter(self, label=None, **kwargs):
        """
        Filter for all entities that match the given label and properties
        returning a new
        :class:`~.IEntitySet`

        .. note::

            Keywords should be made of a property name
            (as passed to the :meth:`~.IGraph.add_vertex` or
            :meth:`~.IGraph.add_edge` methods)
            followed by one of these suffixes, to control how the given
            value is matched against the :class:`~.IEntity`'s values for
            that property.

            * __contains
            * __icontains
            * __startswith
            * __istartswith
            * __endswith
            * __iendswith
            * __le
            * __lt
            * __ge
            * __gt
            * __eq
            * __ieq
            * __ne
            * __ine

        :param label: Filter for entities that have a particular label. If
            :obj:`None`, all entities are returned.
        :type label: :class:`str`
        :param kwargs: Property key and value.
        :type kwargs: key=value
        :returns: New :class:`~.IEntitySet` with the entities that
            matched the filter criteria.
        :rtype: :class:`~.IEntitySet`
        """

    @abc.abstractmethod
    def all(self, label=None, **kwargs):
        """
        Return all the items in the container as a list.

        :param label: Filter for entities that have a particular label. If
            :obj:`None`, all entities are returned.
        :type label: :class:`str`
        :param kwargs: Property key and value.
        :type kwargs: key=value
        :returns: All the items in the container.
        :rtype: :class:`list` containing :class:`~.IEntity`
        """

    @abc.abstractmethod
    def sorted(self, key=None, reverse=False):
        """
        Sort and return all items in the container.

        :param key: Key specifies a function of one argument that is used to
            extract a comparison key from each list element. The default
            is to compare the elements directly.
        :type key: callable
        :param reverse: If set to True, then the list elements are sorted as
            if each comparison were reverted.
        :type reverse: :class:`bool`
        :returns: All the items in the container.
        :rtype: :class:`list` containing :class:`~.IEntity`
        """

    def __str__(self):
        return "<{0}> items: {1}".format(
            self.__class__.__name__, self.__len__()
        )

    def __repr__(self):  # pragma: no cover
        return self.__str__()


class ILock(object):
    """
    Interface for locking.
    """
    ___metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def acquire(self):
        """
        Acquire a lock.

        :raises AcquireError: If a lock failed to be acquired.
        """

    @abc.abstractmethod
    def release(self):
        """
        Release the lock.

        :raises ReleaseError: If the lock was unable to be released.
        """
