from behave import given, register_type
from ruruki.parsers import cypher_parser


def set_expression(text):
    return getattr(cypher_parser, text)

register_type(GrammarParser=set_expression)


@given('we have a "{text:GrammarParser}" grammar expression')
def setup_match_action_expression(context, text):
    """
    Setup add_operation grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = text


@given("we have a match action grammar expression")
def setup_match_action_expression(context):
    """
    Setup match grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.match_action


@given("we have a where action grammar expression")
def setup_where_expression(context):
    """
    Setup where grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.where


@given("we have a as action grammar expression")
def setup_as_action_expression(context):
    """
    Setup as grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.as_action


@given("we have a clause action grammar expression")
def setup_clause_expression(context):
    """
    Setup clause grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.clause


@given("we have a return action grammar expression")
def setup_return_action_expression(context):
    """
    Setup return grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.return_action


@given("we have a expression_atom grammar expression")
def setup_expression_atom_expression(context):
    """
    Setup expression atom grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.expression_atom


@given("we have a expression grammar expression")
def setup_expression_expression(context):
    """
    Setup expression grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.expression


@given("we have a return_item grammar expression")
def setup_return_item_expression(context):
    """
    Setup return item grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.return_item


@given("we have a return_items grammar expression")
def setup_return_items_expression(context):
    """
    Setup return items grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.return_items


@given("we have a return_body grammar expression")
def setup_return_body_expression(context):
    """
    Setup return body grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.return_body


@given("we have a return_pattern grammar expression")
def setup_return_body_expression(context):
    """
    Setup return pattern grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.return_pattern
