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
property_key_name = pp.Group(
    varnums("alias") +
    pp.Suppress(pp.Literal(".")) +
    varnums("key")
)("property_key_name")


property_lookup = property_key_name("property_lookup")


###########################################
##              Expressions              ##
###########################################
expression = pp.Forward()

# Atom = NumberLiteral
#      | StringLiteral
#      | Parameter  --> not done
#      | (T,R,U,E)
#      | (F,A,L,S,E)
#      | (N,U,L,L)
#      | CaseExpression  --> not done
#      | ((C,O,U,N,T), '(', '*', ')')
#      | MapLiteral
#      | ListComprehension  --> not done
#      | ('[', WS, Expression, WS, { ',', WS, Expression, WS }, ']')
#      | ((F,I,L,T,E,R), WS, '(', WS, FilterExpression, WS, ')')  --> not done
#      | ((E,X,T,R,A,C,T), WS, '(', WS, FilterExpression, WS, [WS, '|', Expression], ')')  --> not done
#      | Reduce  --> not done
#      | ((A,L,L), WS, '(', WS, FilterExpression, WS, ')') --> not done
#      | ((A,N,Y), WS, '(', WS, FilterExpression, WS, ')') --> not done
#      | ((N,O,N,E), WS, '(', WS, FilterExpression, WS, ')') --> not done
#      | ((S,I,N,G,L,E), WS, '(', WS, FilterExpression, WS, ')') --> not done
#      | ShortestPathPattern --> not done
#      | RelationshipsPattern --> not done
#      | parenthesizedExpression --> not done
#      | FunctionInvocation --> not done
#      | Variable
#      ;
expression_atom = pp.Or(
    [
        # NULL
        null_keyword("null"),

        # TRUE
        true_keyword,

        # FALSE
        false_keyword,

        # COUNT (*)
        count,

        # 1234
        nums,

        # abcd
        var,

        # {'key': 'value'}
        dict_literal("dict"),

        # [expr]
        # [expr, expr]
        (
            pp.Word("[", exact=1) +
            expression +
            pp.ZeroOrMore(
                pp.Word(",", exact=1) + expression
            ) +
            pp.Word("]", exact=1)
        )
    ]
)


# Expression2 = Atom, { PropertyLookup | NodeLabels } ;
expression2 = (
    expression_atom + pp.ZeroOrMore(
        pp.Or(
            [
                property_lookup,
                labels,
            ]
        )
    )
)

# Expression3 = Expression2, {
#   (WS, '[', Expression, ']') |
#   (WS, '[', [Expression], '..', [Expression], ']') |
#   (((WS, '=~') | (SP, (I,N)) | (SP, (S,T,A,R,T,S), SP, (W,I,T,H)) | (SP, (E,N,D,S), SP, (W,I,T,H)) | (SP, (C,O,N,T,A,I,N,S))), WS, Expression2) |
#   (SP, (I,S), SP, (N,U,L,L)) |
#   (SP, (I,S), SP, (N,O,T), SP, (N,U,L,L))
#} ;
expression3 = (
    expression2 +
    pp.ZeroOrMore(
        pp.Or(
            [
                #   (WS, '[', Expression, ']') |
                pp.Word("[", exact=1) + expression + pp.Word("]", exact=1),

                #   (WS, '[', [Expression], '..', [Expression], ']') |
                (
                    pp.Word("[", exact=1) +
                    (
                        pp.Optional(expression) +
                        pp.Word("..", exact=2) +
                        pp.Optional(expression)
                    ) +
                    pp.Word("]", exact=1)
                ),

                #   (((WS, '=~') | (SP, (I,N)) | (SP, (S,T,A,R,T,S), SP, (W,I,T,H)) | (SP, (E,N,D,S), SP, (W,I,T,H)) | (SP, (C,O,N,T,A,I,N,S))), WS, Expression2) |
                (
                    pp.Or(
                        [
                            regex_operation,
                            in_keyword,
                            starts_with,
                            ends_with,
                            contains,
                        ]
                    ) + expression2
                ),

                #   (SP, (I,S), SP, (N,U,L,L)) |
                is_null,

                #   (SP, (I,S), SP, (N,O,T), SP, (N,U,L,L))
                is_not_null,
            ]
        )
    )
)

# Expression4 = { ('+' | '-'), WS }, Expression3 ;
expression4 = (
    pp.ZeroOrMore(
        pp.Or(
            [
                add_operation,
                subtract_operation,
            ]
        )
    ) + expression3
)

# Expression5 = Expression4, { WS, '^', WS, Expression4 } ;
expression5 = (
    expression4 + pp.ZeroOrMore(bitwise_or_operation + expression4)
)

# Expression6 = Expression5, { (WS, '*', WS, Expression5) | (WS, '/', WS, Expression5) | (WS, '%', WS, Expression5) } ;
expression6 = (
    expression5 + pp.ZeroOrMore(
        pp.Or(
            [
                multiply_operation + expression5,
                divide_operation + expression5,
                percent_operation + expression5,
            ]
        )
    )
)

# Expression7 = Expression6, { (WS, '+', WS, Expression6) | (WS, '-', WS, Expression6) } ;
expression7 = (
    expression6 + pp.ZeroOrMore(
        pp.Or(
            [
                add_operation + expression6,
                subtract_operation + expression6,
            ]
        )
    )
)

# PartialComparisonExpression = ('=', WS, Expression7)
#                             | ('<>', WS, Expression7)
#                             | ('!=', WS, Expression7)
#                             | ('<', WS, Expression7)
#                             | ('>', WS, Expression7)
#                             | ('<=', WS, Expression7)
#                             | ('>=', WS, Expression7)
#                             ;
partial_comparison_expression = (
    pp.Or(
        [
            eq_operation + expression7,
            neq_operation + expression7,
            lt_operation + expression7,
            lte_operation + expression7,
            gt_operation + expression7,
            gte_operation + expression7,
        ]
    )
)


# Expression8 = Expression7, { WS, PartialComparisonExpression } ;
expression8 = (
    expression7 + pp.ZeroOrMore(partial_comparison_expression)
)


# Expression9 = { SP, (N,O,T), SP }, Expression8 ;
expression9 = (pp.ZeroOrMore(pp.CaselessKeyword("NOT")) + expression8)


# Expression10 = Expression9, { SP, (A,N,D), SP, Expression9 } ;
expression10 = (
    expression9 + pp.ZeroOrMore(
        pp.CaselessKeyword("AND") + expression9
    )
)


# Expression11 = Expression10, { SP, (X,O,R), SP, Expression10 } ;
expression11 = (
    expression10 + pp.ZeroOrMore(
        pp.CaselessKeyword("XOR") + expression10
    )
)


# Expression12 = Expression11, { SP, (O,R), SP, Expression11 } ;
expression12 = (
    expression11 + pp.ZeroOrMore(
        pp.CaselessKeyword("OR") + expression11
    )
)


# Expression = Expression12 ;
expression << expression12  # pylint: disable=pointless-statement


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
where_pattern = pp.Group(
    where_clause +
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
    quote_unquote_var("value")
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



# TODO:
# This is a hack till I figure out the serious performance issues with the
# above. return_item should be using expression and not expression_atom.

# ReturnItem = (Expression, SP, (A,S), SP, Variable)| Expression;
return_item = pp.Group(
    pp.Or(
        [
            expression_atom + as_clause + var,
            expression_atom,
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
