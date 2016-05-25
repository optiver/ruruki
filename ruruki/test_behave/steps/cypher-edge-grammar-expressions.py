from behave import given
from ruruki.parsers import cypher_parser


@given("we have a edge body grammar expression")
def setup_edge_body_expression(context):
    context.expr = cypher_parser.edge_body


@given("we have a edge grammar expression")
def setup_ege_expression(context):
    context.expr = cypher_parser.edge
