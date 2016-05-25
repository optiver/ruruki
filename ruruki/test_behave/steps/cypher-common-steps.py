from assertpy import assert_that
from behave import then, when
from ruruki.parsers import cypher_parser



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
