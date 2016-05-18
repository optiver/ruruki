from behave import given
from ruruki.parsers import cypher_parser


@given("we have a vertex grammar expression")
def setup_vertex_expression(context):
    context.expr = cypher_parser.vertex
