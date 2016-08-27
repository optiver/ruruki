from assertpy import assert_that
from behave import when, given, then
from ruruki.graphs import Graph

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


@given("we have a empty graph object")
def setup_empty_graph(context):
    """
    Setup a empty graph object and attach it to the context object for later.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.graph = Graph()


@given(u'we have a file object with the following dump content')
def create_dump_file_obj(context):
    """
    Create a file object containting the dumpt text specified in the
    step scenario and attach it to the context object for later use.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.dump_file = StringIO(context.text)


@when(u'we load the dump into the database')
def load_graph_dump_into_the_graph_obj(context):
    """
    Load the dump file into the graph object.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.graph.load(context.dump_file)


@then(u'we expect to have "{count}" edge')
def check_edge_count(context, count):
    """
    Check the edge count in the graph object.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    :param count: Expected edge count.
    :type count: :class:`int`
    """
    assert_that(context.graph.edges).is_length(int(count))


@then(u'the edges have')
def check_edge(context):
    """
    Check the edge has the correct data.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    for row in context.table:
        edge = context.graph.get_edge(int(row["ident"]))
        head = edge.head
        tail = edge.tail

        assert_that(edge.label).is_equal_to(row["label"])
        assert_that(edge.properties).is_equal_to(eval(row["properties"]))

        assert_that(head.ident).is_equal_to(int(row["head_ident"]))
        assert_that(tail.ident).is_equal_to(int(row["tail_ident"]))


@then(u'we expect to have "{count}" vertices')
def check_vertices_count(context, count):
    """
    Check the vertices count in the graph object.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    :param count: Expected vertex count.
    :type count: :class:`int`
    """
    assert_that(context.graph.vertices).is_length(int(count))


@then(u'the vertices have')
def check_edge(context):
    """
    Check the vertex has the correct data.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    for row in context.table:
        vertex = context.graph.get_vertex(int(row["ident"]))
        assert_that(vertex.ident).is_equal_to(int(row["ident"]))
        assert_that(vertex.label).is_equal_to(row["label"])
        assert_that(vertex.properties).is_equal_to(eval(row["properties"]))
