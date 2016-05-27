from behave import given
from ruruki.parsers import cypher_parser


@given("we have a quoted_var grammar expression")
def setup_quoted_var_expression(context):
    """
    Setup quote_unquote_var grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.quoted_var


@given("we have a match pattern grammar expression")
def setup_match_pattern_expression(context):
    """
    Setup match pattern grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.match_pattern


@given("we have a pattern grammar expression")
def setup_pattern_expression(context):
    """
    Setup pattern grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.pattern


@given("we have a clause pattern grammar expression")
def setup_clause_pattern_expression(context):
    """
    Setup clause pattern grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.clause


@given("we have a single_query grammar expression")
def setup_single_query_pattern_expression(context):
    """
    Setup single query pattern  grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.single_query


@given("we have a regular_query grammar expression")
def setup_regular_pattern_expression(context):
    """
    Setup regular pattern  grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.regular_query


@given("we have a query grammar expression")
def setup_query_pattern_expression(context):
    """
    Setup query pattern grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.query


@given("we have a where pattern grammar expression")
def setup_query_pattern_expression(context):
    """
    Setup query pattern grammar expression.

    :param context: Context object share between all the setups.
    :type context: :class:`behave.runner.Context`
    """
    context.expr = cypher_parser.where_pattern
