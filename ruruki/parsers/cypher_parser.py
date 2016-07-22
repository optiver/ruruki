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
var = pp.Word(pp.alphas)("alphas")

# 0123...
nums = pp.Word(pp.nums)("nums").setParseAction(lambda s, l, t: int(t[0]))

# abc...0123...
varnums = pp.Word(pp.alphanums).setResultsName("alphanums")


# =
eq_operation = (
    pp.Word("=", exact=1)("operation").setParseAction(lambda x: "eq")
)


# !=
neq_operation = (
    pp.Word("!=", exact=2)("operation").setParseAction(lambda x: "neq")
)

# <
lt_operation = (
    pp.Word("<", exact=1)("operation").setParseAction(lambda x: "lt")
)


# >
gt_operation = (
    pp.Word(">", exact=1)("operation").setParseAction(lambda x: "gt")
)


#>=
gte_operation = (
    pp.Word(">=", exact=2)("operation").setParseAction(lambda x: "gte")
)


# <=
lte_operation = (
    pp.Word("<=", exact=2)("operation").setParseAction(lambda x: "lte")
)


# +
add_operation = pp.Word("+", exact=1)("operation")


# -
subtract_operation = pp.Word("-", exact=1)("operation")


# *
multiply_operation = pp.Word("*", exact=1)("operation")


# divide
divide_operation = pp.Word("/", exact=1)("operation")


# %
percent_operation = pp.Word("%", exact=1)("operation")


# ^
bitwise_or_operation = pp.Word("^", exact=1)("operation")

# =~
regex_operation = pp.Word("=~", exact=2)("operation")

# with or WITH
with_keyword = pp.CaselessKeyword("WITH")("with_keyword")


# IN or in
in_keyword = pp.CaselessKeyword("IN")("in_keyword")


# IS or is
is_keyword = pp.CaselessKeyword("IS")("is_keyword")


# NOT or not
not_keyword = pp.CaselessKeyword("NOT")("not_keyword")


# NNULL or null
null_keyword = pp.CaselessKeyword("NULL")("null_keyword")


# STARTS or starts
starts_keyword = pp.CaselessKeyword("STARTS")("starts_keyword")


# CONTAINS or contains
contains_keyword = pp.CaselessKeyword("CONTAINS")("contains_keyword")


# ENDS or ends
ends_keyword = pp.CaselessKeyword("ENDS")("ends_keyword")


# STARTS WITH
starts_with = (
    (starts_keyword + with_keyword)("string_matching").
    setParseAction(lambda s: "startswith")
)


# ENDS WITH
ends_with = (
    (ends_keyword + with_keyword)("string_matching").
    setParseAction(lambda e: "endswith")
)

# CONTAINS
contains = (
    contains_keyword("string_matching").
    setParseAction(lambda c: "contains")
)


# IS NOT or is not
is_not = (
    (is_keyword + not_keyword)("string_matching").
    setParseAction(lambda i: "is_not")
)

# IS NULL or is null
is_null = (
    (is_keyword + null_keyword)("type_matching").
    setParseAction(lambda i: "is_null")
)


# IS NOT NULL or is not null
is_not_null = (
    (is_keyword + not_keyword + null_keyword)("type_matching").
    setParseAction(lambda i: "is_not_null")
)

# True or true
true_keyword = (
    pp.CaselessKeyword("TRUE")("type_matching").
    setParseAction(lambda x: True)
)

# False or false
false_keyword = (
    pp.CaselessKeyword("FALSE")("type_matching").
    setParseAction(lambda x: False)
)


# ((C,O,U,N,T), '(', '*', ')')
count = (
    (
        pp.CaselessKeyword("COUNT") +
        pp.Suppress(pp.Word("(", exact=1)) +
        pp.Word("*", exact=1) +
        pp.Suppress(pp.Word(")", exact=1))
    )("function_action").
    setParseAction(lambda c: len)
)

# 'string'
# "string"
# "string, any type of string including commas"
quoted_var = pp.Or(
    [
        pp.QuotedString("'"),
        pp.QuotedString('"'),
    ]
)("alias")


# 'abc123' or "abc123" or abc123 or abc, 123
quote_unquote_var = pp.Or(
    [
        quoted_var,
        varnums("alias"),
    ]
)("alias")

# Single level dict parser, does not support nested dict expressions
# {}
# {'key': 'value'}
# {"key": "value"}
# {'key': value}
# {'key': "Value, value"}
# {'key': 'Value, value'}
# {'key', 'value', 'key', 'value', ....}
dict_literal = (
    (
        pp.Suppress(pp.Literal("{")) +
        pp.ZeroOrMore(
            quote_unquote_var +
            pp.Suppress(pp.Literal(":")) +
            quote_unquote_var +
            pp.Optional(pp.Suppress(pp.Literal(",")))
        ) +
        pp.Suppress(pp.Literal("}"))
    )("dict_literal")
).setParseAction(
    # convert a list into a dictionary
    # eg: ['name', 'Bob'] -> {'name': 'Bob'}
    lambda p: dict(zip(*[iter(p)]*2))
)


# One of more labels :LABEL_A or :LABEL_A:LABEL_B
labels = pp.ZeroOrMore(
    pp.Suppress(":") +
    pp.Group(varnums("label"))
)("labels")




# Open and close markers ()
vertex_open_marker = pp.Word("(", exact=1)("open_marker")
vertex_close_marker = pp.Word(")", exact=1)("close_marker")
edge_open_marker = pp.Word("[", exact=1)("open_marker")
edge_close_marker = pp.Word("]", exact=1)("close_marker")


###########################################
## Expressions for vertices/nodes        ##
###########################################

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
    pp.Suppress(vertex_open_marker) +
    pp.Optional(var("alias")) +
    pp.Optional(labels("labels")) +
    pp.Optional(dict_literal("properties")) +
    pp.Suppress(vertex_close_marker)
).setResultsName("vertex")


###########################################
## Expressions for edges/relationships   ##
###########################################

# *<start int>..<end int>
# *
# *..10
# *1..2
range_literal = pp.Group(
    pp.Suppress(pp.Word("*", exact=1)) +
    pp.Optional(
        pp.Or(
            [
                pp.Word("..", exact=2) + nums("max"),
                nums("min") + pp.Word("..", exact=2) + nums("max"),
            ]
        )
    )
)("range_literal")


# edge label
# :label
# :label|label
edge_label = pp.Forward()
edge_label << (
    labels +
    pp.ZeroOrMore(
        pp.Suppress(pp.Literal("|")) +
        edge_label
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
    pp.Group(
        pp.Suppress(edge_open_marker) +
        pp.Optional(var("alias")) +
        pp.Optional(edge_label) +
        pp.Optional(range_literal) +
        pp.Optional(dict_literal) +
        pp.Suppress(edge_close_marker)
    )
)("edge_body")



# RelationshipPattern =
#   (LeftArrowHead, WS, Dash, WS, [RelationshipDetail], WS, Dash, WS, RightArrowHead) # pylint: disable=line-too-long
#   | (LeftArrowHead, WS, Dash, WS, [RelationshipDetail], WS, Dash)
#   | (Dash, WS, [RelationshipDetail], WS, Dash, WS, RightArrowHead)
#   | (Dash, WS, [RelationshipDetail], WS, Dash)
#   ;
edge = pp.Group(
    pp.Or(
        [
            # <-[]->
            (
                pp.Word("<-", exact=2)("in").setParseAction(lambda: True) +
                pp.Optional(edge_body) +
                pp.Word("->", exact=2)("out").setParseAction(lambda: True)
            ),

            # <-[]-
            (
                pp.Word("<-", exact=2)("in").setParseAction(lambda: True) +
                pp.Optional(edge_body) +
                pp.Word("-", exact=1)("out").setParseAction(lambda: False)
            ),

            # -[]->
            (
                pp.Word("-", exact=1)("in").setParseAction(lambda: False) +
                pp.Optional(edge_body) +
                pp.Word("->", exact=2)("out").setParseAction(lambda: True)
            ),

            # -[]-
            (
                pp.Word("-", exact=1)("in").setParseAction(lambda: True) +
                pp.Optional(edge_body) +
                pp.Word("-", exact=1)("out").setParseAction(lambda: True)
            ),
        ]
    )
)("edge")



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
# m["key"]
property_key_name = pp.Group(
    varnums("alias") +
    pp.Or(
        [
            # .key
            pp.Suppress(pp.Word(".", exact=1)) + varnums("key"),

            # ["key"]
            (
                pp.Suppress(pp.Word("[", exact=1)) +
                quoted_var("key") +
                pp.Suppress(pp.Word("]", exact=1))
            ),
        ]
    )
)("property_key_name")



property_lookup = property_key_name("property_lookup")


###########################################
##              Expressions              ##
###########################################
# PREDICATES
# n.number >= 1 AND n.number <= 10
# 1 <= n.number <= 10
# identifier IS NULL
# NOT exists(n.property) OR n.property = {value}
# n.property STARTS WITH "Tob" OR n.property ENDS WITH "n" OR n.property CONTAINS "goodie"
# n.property IN [{value1}, {value2}]


# n.property <> {value}
# n.property = {value}
# n["property"] = {value}
# n.property =~ "Tob.*"
property_compare = (
    property_lookup("key") +
    pp.Or(
        [
            eq_operation,
            neq_operation,
            lt_operation,
            lte_operation,
            gt_operation,
            gte_operation,
            regex_operation,
        ]
    ) +
    pp.Or(
        [
            quoted_var("value"),
            nums("value")
        ]
    )
)

expression_pattern = pp.Group(pp.Or(
    [
        # exists(n.property)
        (
            pp.CaselessKeyword("exists")("function") +
            pp.Suppress(pp.Word("(", exact=1)) +
            property_lookup +
            pp.Suppress(pp.Word(")", exact=1))
        ),

        # n.property STARTS WITH "Tob"
        # n.property ENDS WITH "ob"
        # n.property CONTAINS "goodie"
        (
            property_lookup +
            (
                starts_with("function") |
                ends_with("function") |
                contains("function")
            ) +
            quoted_var("value")
        ),

        # n:Person
        var + labels,

        # See above
        property_compare,

        # variable IS NULL
        var("variable") + is_null,
    ]
)).setResultsName("expression_pattern", listAllMatches=True)

# n.name = 'Sponge' or n.name = 'Bob'
expression10 = pp.Forward()
expression10 << (
    expression_pattern +
    pp.ZeroOrMore(
        pp.CaselessKeyword("OR") +
        pp.Group(
        expression_pattern
        ).setResultsName("or", listAllMatches=True)
    )
)

# n.name = 'Sponge' or n.name = 'Bob'
expression12 = pp.Forward()
expression12 << pp.Group(
    expression10 +
    pp.ZeroOrMore(
        pp.CaselessKeyword("AND") +
        expression10
    )
).setResultsName("and", listAllMatches=True)

# expression12 = pp.Forward()
# expression12 << expression10 + (
#     pp.ZeroOrMore(
#         pp.Group(
#             pp.CaselessKeyword("AND")("clause") +
#             expression10
#         ).setResultsName("and", listAllMatches=True)
#     )
# )

expression = expression12

###########################################
##              Clauses                  ##
###########################################

# MATCH
# Match
# match
match_clause = pp.CaselessKeyword("MATCH")("clause")


# WHERE
# Where
# where
where_clause = pp.CaselessKeyword("WHERE")("clause")


# AS
# As
# as
as_clause = pp.CaselessKeyword("AS")("clause")


# RETURN
# Return
# return
return_clause = pp.CaselessKeyword("RETURN")("clause")


# WHERE PATTERN
# WHERE m.key = value
# WHERE m.key != value
# WHERE m.key > value
# WHERE m.key >= value
# WHERE m.key < value
# WHERE m.key <= value
# WHERE NOT(n.name = 'apa' AND false)
# Where = (W,H,E,R,E), SP, Expression ;
where_pattern = pp.Group(
    where_clause +
    expression
)("where_pattern")


# MATCH PATTERN
# MATCH (n)-[]-(m)
# MATCH (n)-[]-(m) WHERE n.key = value
# MATCH (n)-[]-(m)<-[]-() WHERE n.key = value
match_pattern = pp.Group(
    match_clause +
    pattern +
    pp.Optional(where_pattern)
)("match_pattern")


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



# ReturnItem = (Expression, SP, (A,S), SP, Variable)| Expression;
return_item = pp.Group(
    pp.Or(
        [
            expression + as_clause + var,
            expression,
        ]
    )
)("return_item")


# ReturnItems = ('*', { WS, ',', WS, ReturnItem })|
#               (ReturnItem, { WS, ',', WS, ReturnItem });
return_items = pp.Group(
    pp.Or(
        [
            pp.Word("*", exact=1) +
            pp.ZeroOrMore(
                pp.Word(",", exact=1) + return_item
            ),

            return_item + pp.ZeroOrMore(
                pp.Word(",", exact=1) + return_item
            ),
        ]
    )
)("return_items")


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
    return_clause + return_body
)("return_pattern")


# only supporting MATCH for now but should also support CREATE in the near
# future
clause = (
    match_pattern
)("clause")


# SingleQuery = Clause, { WS, Clause } ;
single_query = (
    clause +
    pp.ZeroOrMore(clause)
)("single_query")


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
)("regular_query")


# not supporting BulkImportQuery at this stage.
# Query = RegularQuery | BulkImportQuery;
query = (regular_query + return_pattern)("query")


def parse(query_str, expr=query, string_end=True, enable_packrat=True):
    """
    Parse the given query string using the provided grammar expression.

    :param query_str: Query string that you are parsing.
    :type query_str: :class:`str`
    :param expr: Grammar expression used for parsing the query string.
    :type expr: :class:`pyparsing.ParserElement`
    :param string_end: True to parsing the entire query string till the
        very end.
    :type string_end: :class:`bool`
    :param enable_packrat: Packrat is a grammar traversal algorithm. It will
        speed things up nicely. This option is not turned on by default with
        pyparsing.
    :type enable_packrat: :class:`bool`
    :returns: Dictionary of parsing results extracted by each grammar
        expression.
    :rtype: :class:`dict`
    """
    if string_end is True:
        expr = expr + pp.StringEnd()

    if enable_packrat:
        expr.enablePackrat()

    return expr.parseString(query_str).asDict()
