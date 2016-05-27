# Due to the nature of the pyparsing grammar expressions, linting is not
# really valid, so we are disbling it for most things.
# pylint: disable=invalid-name,expression-not-assigned
"""
Grammar expressions.

See https://s3.amazonaws.com/artifacts.opencypher.org/cypher.ebnf
"""
import pyparsing as pp


###########################################
##  COMMON PYPARSING GRAMMAR EXPRESSIONS ##
###########################################

# abc...
var = pp.Word(pp.alphas)

# 0123...
nums = pp.Word(pp.nums)

# abc...0123...
varnums = pp.Word(pp.alphanums)


# =
eq_operation = (
    pp.Word("=", exact=1).
    setResultsName("operation").
    setParseAction(lambda x: "eq")
)


# !=
neq_operation = (
    pp.Word("!=", exact=2).
    setResultsName("operation").
    setParseAction(lambda x: "neq")
)

# <
lt_operation = (
    pp.Word("<", exact=1).
    setResultsName("operation").
    setParseAction(lambda x: "lt")
)


# >
gt_operation = (
    pp.Word(">", exact=1).
    setResultsName("operation").
    setParseAction(lambda x: "gt")
)


#>=
gte_operation = (
    pp.Word(">=", exact=2).
    setResultsName("operation").
    setParseAction(lambda x: "gte")
)


# <=
lte_operation = (
    pp.Word("<=", exact=2).
    setResultsName("operation").
    setParseAction(lambda x: "lte")
)

# 'string'
# "string"
# "string, any type of string including commas"
quoted_var = pp.Or(
    [
        pp.QuotedString("'"),
        pp.QuotedString('"'),
    ]
)

# 'abc123' or "abc123" or abc123 or abc, 123
quote_unquote_var = pp.Or(
    [
        quoted_var,
        varnums,
    ]
)

# Single level dict parser, does not support nested dict expressions
# {}
# {'key': 'value'}
# {"key": "value"}
# {'key': value}
# {'key': "Value, value"}
# {'key': 'Value, value'}
# {'key', 'value', 'key', 'value', ....}
dict_literal = (
    pp.Suppress(pp.Literal("{")) +
    pp.ZeroOrMore(
        quote_unquote_var +
        pp.Suppress(pp.Literal(":")) +
        quote_unquote_var +
        pp.Optional(pp.Suppress(pp.Literal(",")))
    ) +
    pp.Suppress(pp.Literal("}"))
).setParseAction(
    # convert a list into a dictionary
    # eg: ['name', 'Bob'] -> {'name': 'Bob'}
    lambda p: dict(zip(*[iter(p)]*2))
)


# One of more labels :LABEL_A or :LABEL_A:LABEL_B
labels = pp.ZeroOrMore(
    pp.Suppress(":") +
    varnums
)


###########################################
## Expressions for vertices/nodes        ##
###########################################


# Open and close markers ()
vertex_open_marker = pp.Suppress(pp.Literal("("))
vertex_close_marker = pp.Suppress(pp.Literal(")"))


# Full vertex expression
# ()
# (var)
# (:label) or multi (:label1:label2) and so on
# ({'key': value})
# (var:label)
# (var {'key': value})
# (:label {'key': value})
# (var:label {'key': value})
vertex = pp.Group(
    vertex_open_marker +
    pp.Optional(var("alias")) +
    pp.Optional(labels("labels")) +
    pp.Optional(dict_literal("properties")) +
    vertex_close_marker
).setResultsName("vertex")


###########################################
## Expressions for edges/relationships   ##
###########################################


# Open and close markers []
edge_open_marker = pp.Suppress(pp.Literal("["))
edge_close_marker = pp.Suppress(pp.Literal("]"))


# *<start int>..<end int>
# *
# *..10
# *1..2
range_literal = (
    (
        pp.Suppress(pp.Literal("*")) ^
        pp.Suppress(pp.Literal("*")) +
        nums.setParseAction(lambda t: int(t[0]))
    ) +
    pp.Optional(nums.setParseAction(lambda t: int(t[0]))) +
    pp.Suppress(pp.Word(".", exact=2)) +
    nums.setParseAction(lambda t: int(t[0]))
)


# edge label
# :label
# :label|label
edge_label = (
    pp.Suppress(pp.Literal(":")) +
    var +
    pp.ZeroOrMore(
        pp.Suppress(pp.Literal("|")) +
        var
    )
)


# In edge direction: <- or -
edge_head = (
    pp.Optional(
        pp.Word("<", exact=1).setParseAction(lambda e: True)("in")
    ) +
    pp.Word("-", exact=1)
)

# Out edge direction: -> or -
edge_tail = (
    pp.Word("-", exact=1) +
    pp.Optional(
        pp.Word(">", exact=1).setParseAction(lambda e: True)("out")
    )
)

# []
# [e]
# [:label] or multiple [:label1|label2]
# [*1..2]
# [{'key': value}]
# [e:label]
# [e *1..2]
# [e:label *]
# [e:label *1..2]
# [e:label *1..2 {'key': value}]
# [:label *]
# [:label *1..2]
# [:label {'key': value}]
# [*1..2 {'key': value}]
edge_body = (
    edge_open_marker +
    pp.Optional(var("alias")) +
    pp.Optional(edge_label("labels")) +
    pp.Optional(range_literal("range")) +
    pp.Optional(dict_literal("properties")) +
    edge_close_marker
)


# <-[]->
# <-[]-
# -[]->
# -[]-
edge = pp.Group(
    edge_head +
    pp.Optional(edge_body) +
    edge_tail
).setResultsName("edge")



# (n:Person)
# (n:Person),(m:Movie)
# (n:Person:Swedish)
# (n:Person {'name': 'Bob'})
# (n)-->(m)
# (n)--(m)
# (n:Person)-->(m)
# (n)<-[:KNOWS]-(m)
# (n)-[r]->(m)
# (n)-[*1..5]->(m)
# (n)-[:KNOWS]->(m:Person {'name': 'Bob'})
pattern = pp.Forward()
pattern << (
    vertex.setResultsName("vertices", listAllMatches=True) +
    pp.Optional(
        edge.setResultsName("edges", listAllMatches=True) +
        pattern
    )
) + pp.Optional(pp.Suppress(",") + pattern)


# m.key
property_key_name = (
    varnums.setResultsName("alias") +
    pp.Suppress(pp.Literal(".")) +
    varnums.setResultsName("key")
)


property_lookup = property_key_name


###########################################
##              Expressions              ##
###########################################

expression_atom = (
    var.setResultsName("alias")
)


# var
# var1, var2 [, var]
expression = (
    expression_atom
)


###########################################
##              Clauses                  ##
###########################################

# MATCH
# Match
# match
match_action = (
    pp.CaselessKeyword("MATCH").
    setResultsName("action").
    setParseAction(lambda t: "match")
)


# WHERE
# Where
# where
where = (
    pp.CaselessKeyword("WHERE").
    setResultsName("action").
    setParseAction(lambda t: "where")
)


# WHERE PATTERN
# WHERE m.key = value
# WHERE m.key != value
# WHERE m.key > value
# WHERE m.key >= value
# WHERE m.key < value
# WHERE m.key <= value
where_pattern = (
    where +
    property_lookup +
    pp.Or(
        [
            eq_operation,
            neq_operation,
            lt_operation,
            lte_operation,
            gt_operation,
            gte_operation,
        ]
    ) +
    quote_unquote_var.setResultsName("value")
)


# MATCH PATTERN
# MATCH (n)-[]-(m)
# MATCH (n)-[]-(m) WHERE n.key = value
# MATCH (n)-[]-(m)<-[]-() WHERE n.key = value
match_pattern = (
    match_action +
    pattern +
    pp.Optional(pp.Group(where_pattern).setResultsName("where_action"))

)


# DISTINCT
# Distinct
# distinct
# distinct_action = (
#     pp.CaselessKeyword("DISTINCT").
#     setResultsName("action").
#     setParseAction(lambda t: "distinct")
# )


# UNION
# Union
# union
# union_action = (
#     pp.CaselessKeyword("UNION").
#     setResultsName("action").
#     setParseAction(lambda t: "union")
# )


# AS
# As
# as
as_action = (
    pp.CaselessKeyword("AS").
    setResultsName("action").
    setParseAction(lambda t: "as")
)

# RETURN
# Return
# return
return_action = (
    pp.CaselessKeyword("RETURN").
    setResultsName("action").
    setParseAction(lambda t: "return")
)


# ReturnItem = (Expression, SP, (A,S), SP, Variable)| Expression;
return_item = pp.Group(
    expression + as_action + var.setResultsName("as_alias") |
    expression
).setResultsName("return_item_grouped", listAllMatches=True)


# ReturnItems = ('*', { WS, ',', WS, ReturnItem })|
#               (ReturnItem, { WS, ',', WS, ReturnItem });
return_items = (
    pp.Literal("*") + pp.ZeroOrMore(pp.Literal(",") + return_item) |
    return_item + pp.ZeroOrMore(pp.Literal(",") + return_item)
)


# ReturnBody = ReturnItems, [SP, Order], [SP, Skip], [SP, Limit] ;
return_body = (
    return_items # +
    # pp,Optional(
    #     order_action | skip_action | limit_action
    # )
)


# Return = ((R,E,T,U,R,N), SP, (D,I,S,T,I,N,C,T), SP, ReturnBody)|
#          ((R,E,T,U,R,N), SP, ReturnBody);
return_pattern = (
    return_action + return_body
)


# only supporting MATCH for now but should also support CREATE in the near
# future
clause = (
    match_pattern
)


# SingleQuery = Clause, { WS, Clause } ;
single_query = (
    clause +
    pp.ZeroOrMore(clause)
)


# not supporting Unions at this stage
# Union = ((U,N,I,O,N), SP, (A,L,L), SingleQuery) | ((U,N,I,O,N), SingleQuery)
# union = (
#     union_action, pp.CaselessKeyword("ALL") + single_query |
#     union_action + single_query
# )


# RegularQuery = SingleQuery, { WS, Union } ;
regular_query = (
    single_query
    # + pp.ZeroOrMore(union)
)


# not supporting BulkImportQuery at this stage.
# Query = RegularQuery | BulkImportQuery;
query = regular_query + return_pattern


def parse(query_str, expr=query, string_end=True):
    """
    Parse the given query string using the provided grammar expression.

    :param query_str: Query string that you are parsing.
    :type query_str: :class:`str`
    :param expr: Grammar expression used for parsing the query string.
    :type expr: :class:`pyparsing.ParserElement`
    :param string_end: True to parsing the entire query string till the
        very end.
    :type string_end: :class:`bool`
    :returns: Dictionary of parsing results extracted by each grammar
        expression.
    :rtype: :class:`dict`
    """
    if string_end is True:
        expr = expr + pp.StringEnd()
    return expr.parseString(query_str).asDict()
