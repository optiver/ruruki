import ast
from assertpy import assert_that
from behave import then, when, given, register_type
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


@when("we parse the string {query} through the parse function")
def parse_the_query_string(context, query):
    """
    Parse the given query string.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    :param query: Query string to parse.
    :type query: :class:`str`
    """
    context.result = cypher_parser.parse(query, expr=context.expr)


@when("we parse the given query pattern string through the parse function")
def parse_the_query_string_from_parseString(context):
    """
    Parse the given query string.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.result = cypher_parser.parse(context.text, expr=context.expr)


@then("it should transform the parsing result into dictionary result")
def validate_result(context):
    """
    Validate the parsed result.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    result = ast.literal_eval(context.text)
    assert_that(
        context.result
    ).is_equal_to(result)


@then("it should transform the parsing result into {result}")
def validate_result(context, result):
    """
    Validate the parsed result.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    :param result: Query parsed result.
    :type result: :class:`dict`
    """
    result = eval(result)
    assert_that(
        context.result
    ).is_equal_to(result)
