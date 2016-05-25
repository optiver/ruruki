from behave import given
from ruruki.parsers import cypher_parser


@given("we have a vertex grammar expression")
def setup_vertex_expression(context):
    """
    Setup vertex grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.vertex
