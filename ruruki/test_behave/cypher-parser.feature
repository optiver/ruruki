Feature: Parser Grammer acceptance

  Feature for testing that the parser can parse a Cypher query strings.

    @variable
    Scenario Outline: Check the variable parsing expression
        Given we have a quoted_var grammar expression
        When we parse the string  <query> through the expression parseString
        Then the result converted into a list should be  <result>

        Examples: query string
          | query        | result         |
          | 'Bob Jane'   | ["Bob Jane"]   |
          | "Bob Jane"   | ["Bob Jane"]   |
          | 'Bob, Jane'  | ["Bob, Jane"]  |
          | "Bob, Jane"  | ["Bob, Jane"]  |

    @patterns @vertex
    Scenario Outline: Parse a simple node/vertex string
        Given we have a vertex grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
          | query                             | result                                                                                  |
          | ()                                | {"vertex": []}                                                                          |
          | (node)                            | {"vertex": {'alias': 'node'}}                                                           |
          | (:PERSON)                         | {"vertex": {'labels': ['PERSON']}}                                                      |
          | (:PERSON:FRIEND)                  | {"vertex": {'labels': ['PERSON', 'FRIEND']}}                                            |
          | ({'name': 'Bob'})                 | {"vertex": {'properties': {'name': 'Bob'}}}                                             |
          | ({name: 'Bob'})                   | {"vertex": {'properties': {'name': 'Bob'}}}                                             |
          | ({'name': 'Bob', 'age': 21})      | {"vertex": {'properties': {'name': 'Bob', 'age': '21'}}}                                |
          | ({'name': 'Bob', 'surname': 'Foo', 'age': 21})  | {"vertex": {'properties': {'name': 'Bob', 'surname': 'Foo', 'age': '21'}}}|
          | (node:PERSON)                     | {"vertex": {'alias': 'node', 'labels': ['PERSON']}}                                     |
          | (:PERSON {'name': 'Bob'})         | {"vertex": {'labels': ['PERSON'], 'properties': {'name': 'Bob'}}}                       |
          | (node:PERSON {'name': 'Bob'})     | {"vertex": {'alias': 'node', 'labels': ['PERSON'], 'properties': {'name': 'Bob'}}}      |

    @patterns @edge_body
    Scenario Outline: Parse a simple relationship/edge body string
        Given we have a edge body grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
          | query                              | result                                                                                  |
          | []                                 | {}                                                                                      |
          | [r]                                | {"alias": "r"}                                                                          |
          | [:label]                           | {"labels": ["label"]}                                                                   |
          | [r:label]                          | {"alias": "r", "labels": ["label"]}                                                     |
          | [*1..5]                            | {"range": [1, 5]}                                                                       |
          | [r *1..5]                          | {"alias": "r", "range": [1, 5]}                                                         |
          | [*1..5]                            | {"range": [1, 5]}                                                                       |
          | [r:label *1..5]                    | {"alias": "r", "labels": ["label"], "range": [1, 5]}                                    |
          | [{'since': 'School'}]              | {"properties": {'since': 'School'}}                                                     |
          | [{'since': 'School', 'years': 2}]  | {"properties": {'since': 'School', 'years': '2'}}                                       |
          | [r {'since': 'School'}]            | {"alias": "r", "properties": {'since': 'School'}}                                       |
          | [:label {'since': 'School'}]       | {"labels": ["label"], "properties": {'since': 'School'}}                                |
          | [r:label {'since': 'School'}]      | {"alias": "r", "labels": ["label"], "properties": {'since': 'School'}}                  |
          | [r:label {'since': 'School, blah'}]| {"alias": "r", "labels": ["label"], "properties": {'since': 'School, blah'}}            |
          | [r:label *1..2 {'since': 'School'}]| {"alias": "r", "labels": ["label"], "properties": {'since': 'School'}, "range": [1, 2]} |
          | [*1..2 {'since': 'School'}]        | {"properties": {'since': 'School'}, "range": [1, 2]}                                    |

    @patterns @edge
    Scenario Outline: Parse a simple relationship/edge string
        Given we have a edge grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
          | query  | result                              |
          | --     | {"edge": ["-", "-"]}                |
          | -[]-   | {"edge": ["-", "-"]}                |
          | <-[]-> | {"edge": {"in": True, "out": True}} |
          | <-[]-  | {"edge": {"in": True}}              |
          | -[]->  | {"edge": {"out": True}}             |

    @patterns
    Scenario Outline: Parse simple pattern strings base on examples on http://neo4j.com/docs/stable/cypher-refcard/
        Given we have a pattern grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
          | query                                 | result         |
          | (n:Person)                            | {"vertices": [{"alias": "n", "labels": ["Person"]}]} |
          | (n:Person),(m:Movie)                  | {"vertices": [{"alias": "n", "labels": ["Person"]}, {"alias": "m", "labels": ["Movie"]}]} |
          | (n:Person:Swedish)                    | {"vertices": [{"alias": "n", "labels": ["Person", "Swedish"]}]} |
          | (n:Person {'name': 'Bob'})            | {"vertices": [{"alias": "n", "labels": ["Person"], 'properties': {'name': 'Bob'}}]} |
          | (n)-->(m)                             | {"vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [{"out": True}]} |
          | (n)--(m)                              | {"vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [["-", "-"]]} |
          | (n:Person)-->(m)                      | {"vertices": [{"alias": "n", "labels": ["Person"]}, {"alias": "m"}], "edges": [{"out": True}]} |
          | (n)<-[:KNOWS]-(m)                     | {"vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [{"in": True, "labels": ["KNOWS"]}]} |
          | (n)-[r]->(m)                          | {"vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [{"out": True, "alias": "r"}]} |
          | (n)-[*1..5]->(m)                      | {"vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [{"out": True, "range": [1, 5]}]} |
          # | (n)-[*]->(m)                          | {}             |
          | (n)-[:KNOWS]->(m:Person {'name': 'Bob'}) | {"vertices": [{"alias": "n"}, {"alias": "m", "labels": ["Person"], "properties": {'name': 'Bob'}}], "edges": [{"labels": ["KNOWS"], "out": True}]} |

    @match_clause @clause_action
    Scenario Outline: Parse simple match clause
        Given we have a match action grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query  | result                |
            | MATCH  | {"action": "match"}   |
            | Match  | {"action": "match"}   |
            | match  | {"action": "match"}   |

    @as_clause @clause_action
    Scenario Outline: Parse simple "as" clauses
        Given we have a as action grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query  | result          |
            | AS  | {"action": "as"}   |
            | As  | {"action": "as"}   |
            | as  | {"action": "as"}   |

    @where @clause_action
    Scenario Outline: Parse simple where clauses
        Given we have a where action grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query  | result                 |
            | WHERE  | {"action": "where"}    |
            | Where  | {"action": "where"}    |
            | where  | {"action": "where"}    |

    @pattern @where_pattern
    Scenario Outline: Parse simple where_pattern clauses
        Given we have a where pattern grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query               | result                                                                              |
            | WHERE m.name = 'Bob'| {"action": "where", "alias": "m", "operation": "eq", "key": "name", "value": "Bob"} |
            | WHERE m.name = Bob  | {"action": "where", "alias": "m", "operation": "eq", "key": "name", "value": "Bob"} |
            | WHERE m.age > 32    | {"action": "where", "alias": "m", "operation": "gt", "key": "age", "value": "32"}   |
            | WHERE m.age < 32    | {"action": "where", "alias": "m", "operation": "lt", "key": "age", "value": "32"}   |
            | WHERE m.age >= 32   | {"action": "where", "alias": "m", "operation": "gte", "key": "age", "value": "32"}  |
            | WHERE m.age <= 32   | {"action": "where", "alias": "m", "operation": "lte", "key": "age", "value": "32"}  |

    @clause @clause_action
    Scenario Outline: Parse simple clause
        Given we have a clause action grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query            | result                                                                       |
            | MATCH (n)        | {"action": "match", "vertices": [{"alias": "n"}]}                            |
            | MATCH (n)-[]-()  | {"action": "match", "edges": [["-", "-"]], "vertices": [{"alias": "n"}, []]} |

    @expression @expression_atom
    Scenario Outline: Parse simple expression atom
        Given we have a expression_atom grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query     | result           |
            | var       | {"alias": "var"} |

    @expression
    Scenario Outline: Parse simple expression
        Given we have a expression grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query     | result           |
            | var       | {"alias": "var"} |

    @return @return_action
    Scenario Outline: Parse simple return clauses
        Given we have a return action grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query      | result               |
            | RETURN     | {"action": "return"} |
            | Return     | {"action": "return"} |
            | return     | {"action": "return"} |

    @return @return_item
    Scenario Outline: Parse simple return_item
        Given we have a return_item grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query      | result                                                                        |
            | node as n  | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}]} |
            | node       | {"return_item_grouped": [{"alias": "node"}]}                                  |

    @return @return_items
    Scenario Outline: Parse simple return_items
        Given we have a return_items grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query                   | result                                                                                                                              |
            | node as n               | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}]}                                                       |
            | node as n, vertex as v  | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}, {"action": "as", "alias": "vertex", "as_alias": "v"}]} |
            | node                    | {"return_item_grouped": [{"alias": "node"}]}                                                                                        |
            | node, vertex            | {"return_item_grouped": [{"alias": "node"}, {"alias": "vertex"}]}                                                                   |
            | *                       | {}                                                                                                                                  |
            | *, node as n            | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}]}                                                       |
            | *, node as n, v         | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}, {"alias": "v"}]}                                       |

    @return @return_body
    Scenario Outline: Parse simple return_body
        Given we have a return_body grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query                   | result                                                                                                                              |
            | node as n               | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}]}                                                       |
            | node as n, vertex as v  | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}, {"action": "as", "alias": "vertex", "as_alias": "v"}]} |
            | node                    | {"return_item_grouped": [{"alias": "node"}]}                                                                                        |
            | node, vertex            | {"return_item_grouped": [{"alias": "node"}, {"alias": "vertex"}]}                                                                   |
            | *                       | {}                                                                                                                                  |
            | *, node as n            | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}]}                                                       |
            | *, node as n, v         | {"return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}, {"alias": "v"}]}                                       |
            # |  Need to still add in the order, limit, ect.. |

    @patterns @match_pattern
    Scenario Outline: Parse simple match clause patterns
        Given we have a match pattern grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query                           | result                                                                                                                                                |
            | MATCH (n)                       | {"action": "match", "vertices": [{"alias": "n"}]}                                                                                                     |
            | MATCH (n),(m)                   | {"action": "match", "vertices": [{"alias": "n"}, {"alias": "m"}]}                                                                                     |
            | MATCH (n)-[:knows]->(m)         | {"action": "match", "vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [{"labels": ["knows"], "out": True}]}                                      |
            | MATCH (n) WHERE n.name = 'Bob'  | {"action": "match", "vertices": [{"alias": "n"}], "where_action": {"action": "where", "alias": "n", "operation": "eq", "key": "name", "value": "Bob"}}|
            | MATCH (n) WHERE n.age >= 32     | {"action": "match", "vertices": [{"alias": "n"}], "where_action": {"action": "where", "alias": "n", "operation": "gte", "key": "age", "value": "32"}} |
            | MATCH (n) WHERE n.age > 32      | {"action": "match", "vertices": [{"alias": "n"}], "where_action": {"action": "where", "alias": "n", "operation": "gt", "key": "age", "value": "32"}}  |
            | MATCH (n) WHERE n.age <= 32     | {"action": "match", "vertices": [{"alias": "n"}], "where_action": {"action": "where", "alias": "n", "operation": "lte", "key": "age", "value": "32"}} |
            | MATCH (n) WHERE n.age < 32      | {"action": "match", "vertices": [{"alias": "n"}], "where_action": {"action": "where", "alias": "n", "operation": "lt", "key": "age", "value": "32"}}  |
            | MATCH (n)-[:knows]->(m) WHERE n.age = 32   | {"action": "match", "where_action": {"action": "where", "alias": "n", "operation": "eq", "key": "age", "value": "32"}, "vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [{"labels": ["knows"], "out": True}]}   |

    @patterns @clause
        Scenario Outline: Parse simple clause patterns
                Clauses supported are MATCH patterns and soon CREATE
        Given we have a clause pattern grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query                   | result                                                                                                           |
            | MATCH (n)               | {"action": "match", "vertices": [{"alias": "n"}]}                                                                |
            | MATCH (n),(m)           | {"action": "match", "vertices": [{"alias": "n"}, {"alias": "m"}]}                                                |
            | MATCH (n)-[:knows]->(m) | {"action": "match", "vertices": [{"alias": "n"}, {"alias": "m"}], "edges": [{"labels": ["knows"], "out": True}]} |

    @patterns @return_pattern
    Scenario Outline: Parse simple return pattern
        Given we have a return_pattern grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query                         | result                                                                                                                                                 |
            | RETURN node as n              | {"action": "return", "return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}]}                                                      |
            | RETURN node as n, v           | {"action": "return", "return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}, {"alias": "v"}]}                                      |
            | RETURN node as n, vertex as v | {"action": "return", "return_item_grouped": [{"action": "as", "alias": "node", "as_alias": "n"}, {"action": "as", "alias": "vertex", "as_alias": "v"}]}|
            # | Still need to do the distinct |

    @query @single_query
    Scenario Outline: Parse single query pattern
                Only supporting MATCH, and soon CREATE
        Given we have a single_query grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query               | result                                                            |
            | MATCH (n)           | {"action": "match", "vertices": [{"alias": "n"}]}                 |
            | MATCH (n) MATCH (m) | {"action": "match", "vertices": [{"alias": "n"}, {"alias": "m"}]} |

    @query @regular_query
    Scenario Outline: Parse regular query pattern
        Given we have a regular_query grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query               | result                                                            |
            | MATCH (n)           | {"action": "match", "vertices": [{"alias": "n"}]}                 |
            | MATCH (n) MATCH (m) | {"action": "match", "vertices": [{"alias": "n"}, {"alias": "m"}]} |

    @query
    Scenario Outline: Parse query pattern
        Given we have a query grammar expression
        When we parse the string <query> through the parse function
        Then it should transform the parsing result into <result>

        Examples: query string
            | query                                | result                                                                                                                                         |
            | MATCH (n) RETURN n                   | {"action": "return", "return_item_grouped": [{"alias": "n"}], "vertices": [{"alias": "n"}]}                                                    |
            | MATCH (n) MATCH (m) RETURN n, m      | {"action": "return", "return_item_grouped": [{"alias": "n"}, {"alias": "m"}], "vertices": [{"alias": "n"}, {"alias": "m"}]}                    |
            | MATCH (n) MATCH (m) RETURN n as node | {"action": "return", "return_item_grouped": [{"action": "as", "alias": "n", "as_alias": "node"}], "vertices": [{"alias": "n"}, {"alias": "m"}]}|
