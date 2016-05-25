from behave import given
from ruruki.parsers import cypher_parser


@given("we have a edge body grammar expression")
def setup_edge_body_expression(context):
    """
    Setup edge body grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.edge_body


@given("we have a edge grammar expression")
def setup_ege_expression(context):
    """
    Setup edge grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.edge
