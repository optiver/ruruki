Feature: Parser Grammar acceptance

  Feature for testing that the parser can parse a Cypher query strings.

  @common @operators
  Scenario Outline: Test simple grammar expression
    Given we have a "<expr>" grammar expression
    When we parse the string <query> through the parse function
    Then it should transform the parsing result into <result>

      Examples: Run the query string through the expression
        | expr                 | query     | result                    |
        | var                  | abc       | {"alphas": "abc"}         |
        | nums                 | 123       | {"nums": 123}             |
        | varnums              | abc123    | {"alphanums": "abc123"}   |
        | eq_operation         | =         | {"operation": "eq"}       |
        | neq_operation        | !=        | {"operation": "neq"}      |
        | lt_operation         | <         | {"operation": "lt"}       |
        | lte_operation        | <=        | {"operation": "lte"}      |
        | gt_operation         | >         | {"operation": "gt"}       |
        | gte_operation        | >=        | {"operation": "gte"}      |
        | add_operation        | +         | {"operation": "+"}        |
        | subtract_operation   | -         | {"operation": "-"}        |
        | multiply_operation   | *         | {"operation": "*"}        |
        | divide_operation     | /         | {"operation": "/"}        |
        | percent_operation    | %         | {"operation": "%"}        |
        | bitwise_or_operation | ^         | {"operation": "^"}        |
        | regex_operation      | =~        | {"operation": "=~"}       |
        | with_keyword         | WITH      | {"with_keyword": "WITH"}       |
        | with_keyword         | with      | {"with_keyword": "WITH"}       |
        | in_keyword           | IN        | {"in_keyword": "IN"}         |
        | in_keyword           | in        | {"in_keyword": "IN"}         |
        | is_keyword           | IS        | {"is_keyword": "IS"}         |
        | is_keyword           | is        | {"is_keyword": "IS"}         |
        | not_keyword          | NOT       | {"not_keyword": "NOT"}        |
        | not_keyword          | not       | {"not_keyword": "NOT"}        |
        | null_keyword         | NULL      | {"null_keyword": "NULL"}       |
        | null_keyword         | null      | {"null_keyword": "NULL"}       |
        | starts_keyword       | STARTS    | {"starts_keyword": "STARTS"}     |
        | starts_keyword       | starts    | {"starts_keyword": "STARTS"}     |
        | ends_keyword         | ENDS      | {"ends_keyword": "ENDS"}       |
        | ends_keyword         | ends      | {"ends_keyword": "ENDS"}       |
        | contains_keyword     | CONTAINS  | {"contains_keyword": "CONTAINS"}   |
        | contains_keyword     | contains  | {"contains_keyword": "CONTAINS"}   |
        | starts_with          | STARTS WITH  | {"string_matching": "startswith"}   |
        | ends_with            | ENDS WITH | {"string_matching": "endswith"}   |
        | contains             | CONTAINS  | {"string_matching": "contains"}   |
        | is_not               | IS NOT    | {"string_matching": "is_not"}   |
        | is_null              | IS NULL   | {"type_matching": "is_null"}   |
        | is_not_null          | IS NOT NULL | {"type_matching": "is_not_null"}   |
        | true_keyword         | TRUE      | {"type_matching": True}   |
        | false_keyword        | FALSE     | {"type_matching": False}   |
        | count                | COUNT (*) | {"function_action": len}   |
        | quoted_var           | 'a'       | {"alias": "a"}   |
        | quoted_var           | "a"       | {"alias": "a"}   |
        | quoted_var           | "a, b"    | {"alias": "a, b"}   |
        | quote_unquote_var    | "a"       | {"alias": "a"}   |
        | quote_unquote_var    | 'a'       | {"alias": "a"}   |
        | quote_unquote_var    | a         | {"alias": "a"}   |
        | dict_literal         | {'name': 'Bob'} | {"dict_literal": {"name": "Bob"}}   |
        | dict_literal         | {name: 'Bob'} | {"dict_literal": {"name": "Bob"}}   |
        | dict_literal         | {name: 'Bob_Sap'} | {"dict_literal": {"name": "Bob_Sap"}}   |
        | dict_literal         | {name: 'Bob, Sap'} | {"dict_literal": {"name": "Bob, Sap"}}   |
        | dict_literal         | {name: 'Bob', surname: 'Sap'} | {"dict_literal": {"name": "Bob", "surname": "Sap"}}   |
        | range_literal        | * | {"range_literal": []}   |
        | range_literal        | *..10 | {"range_literal": {"max": 10}}   |
        | range_literal        | *1..10 | {"range_literal": {"min": 1, "max": 10}}   |
        | labels               | :Label1 | {"labels": [{"label": "Label1"}]}   |
        | labels               | :Label1:Label2 | {"labels": [{"label": "Label1"}, {"label": "Label2"}]}   |
        | vertex_open_marker   | ( | {"open_marker": "("}   |
        | vertex_close_marker  | ) | {"close_marker": ")"}  |
        | edge_open_marker     | [ | {"open_marker": "["}   |
        | edge_close_marker    | ] | {"close_marker": "]"}   |
        | edge_label           | :Label1:Label2 | {"labels": [{"label": "Label1"}, {"label": "Label2"}]}   |
        | property_key_name    | n.name | {"property_key_name": {"alias": "n", "key": "name"}}   |
        | property_key_name    | n["name"] | {"property_key_name": {"alias": "n", "key": "name"}}   |
        | property_lookup      | n.name | {"property_lookup": {"alias": "n", "key": "name"}}  |

  @clause
  Scenario Outline: Test simple grammar expression
    Given we have a "<expr>" grammar expression
    When we parse the string <query> through the parse function
    Then it should transform the parsing result into <result>

      Examples: query string
      | expr          | query   | result  |
      | match_clause  | MATCH   | {"clause": "MATCH"}  |
      | match_clause  | match   | {"clause": "MATCH"}  |
      | where_clause  | WHERE   | {"clause": "WHERE"}  |
      | where_clause  | where   | {"clause": "WHERE"}  |
      | as_clause     | AS      | {"clause": "AS"}     |
      | as_clause     | as      | {"clause": "AS"}     |
      | return_clause | RETURN  | {"clause": "RETURN"} |
      | return_clause | return  | {"clause": "RETURN"} |
