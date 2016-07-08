Feature: Parser Pattern Grammar acceptance

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      ()
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertex": []
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertex": {"alias": "n"}
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (:label)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertex": {"labels": [{"label": "label"}]}
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (:labelA:labelB)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertex": {
          "labels": [
            {"label": "labelA"},
            {"label": "labelB"}
          ]
        }
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      ({'name': "Bob"})
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertex": {
          "properties": {"name": "Bob"}
        }
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      ({'name': "Bob, Sap"})
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertex": {
          "properties": {"name": "Bob, Sap"}
        }
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      ({'name': "Bob", "surname": "Sap"})
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertex": {
          "properties": {
             "name": "Bob",
             "surname": "Sap"
          }
        }
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n:Person {'name': "Bob, Sap"})
      """
    Then it should transform the parsing result into dictionary result
      """
      {
      "vertex": {
          "alias": "n",
          "labels": [
            {"label": "Person"}
          ],
          "properties": {"name": "Bob, Sap"}
        }
      }
      """

  @patterns @vertex
  Scenario: Parse a vertex pattern query string
    Given we have a "vertex" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (:Person {'name': "Bob, Sap"})
      """
    Then it should transform the parsing result into dictionary result
      """
      {
      "vertex": {
          "labels": [
            {"label": "Person"}
          ],
          "properties": {"name": "Bob, Sap"}
        }
      }
      """

  @patterns @edge
  Scenario: Parse a edge pattern query string
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      --
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
          'in': True, 'out': True
        }
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[]-
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': True, 'out': True,
        'edge_body': []
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      <-[]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': True, 'out': True,
        'edge_body': []
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      <-[]-
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': True, 'out': False,
        'edge_body': []
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': []
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[r]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': {"alias": "r"}
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[r:KNOWS]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': {
          "alias": "r",
          "labels": [{"label": "KNOWS"}]
        }
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[*2..5]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': {
          "range_literal": {"min": 2, "max": 5}
        }
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[r *2..5]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': {
          "alias": "r",
          "range_literal": {"min": 2, "max": 5}
        }
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[r:KNOWS *2..5]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': {
          "alias": "r",
          "range_literal": {"min": 2, "max": 5},
          "labels": [{"label": "KNOWS"}]
        }
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[{"weight": 1}]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': {
          "dict_literal": {
            "weight": "1"
          }
        }
      },
    }
    """

  @patterns @edge
  Scenario: Parse a edge pattern query string
      Here we are including the edge_body in the test.
    Given we have a "edge" grammar expression
    When we parse the given query pattern string through the parse function
      """
      -[r:KNOWS *1..2 {"weight": 1}]->
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'edge': {
        'in': False, 'out': True,
        'edge_body': {
          "alias": "r",
          "labels": [{"label": "KNOWS"}],
          "range_literal": {"min": 1, "max": 2},
          "dict_literal": {
            "weight": "1"
          }
        }
      },
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name = 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': 'eq',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob'
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name != 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': 'neq',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob'
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name < 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': 'lt',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob'
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name <= 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': 'lte',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob'
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name > 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': 'gt',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob'
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name >= 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': 'gte',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob'
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name =~ 'Bob\d+'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': '=~',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob\d+'
    }
    """

  @patterns @property_compare
  Scenario: Parse a property compare pattern query string
    Given we have a "property_compare" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n["name"] = 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      'operation': 'eq',
      'key': {
        'alias': 'n',
        'key': 'name'
      },
      'value': 'Bob'
    }
    """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.name = 'Bob'
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'operation': 'eq',
        'key': {
          'alias': 'n',
          'key': 'name'
        },
        'value': 'Bob'
      }
      """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n:Person
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'alphas': 'n',
        'labels': [
          {'label': 'Person'}
        ]
      }
      """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      exists(n.name)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'function': 'exists',
        'property_lookup': {
          'alias': 'n',
          'key': 'name'
        }
      }
      """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.property STARTS WITH "Tob"
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'function': 'startswith',
        'property_lookup': {
          'alias': 'n',
          'key': 'property'
          },
        'value': 'Tob'
      }
      """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.property ENDS WITH "ob"
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'function': 'endswith',
        'property_lookup': {
          'alias': 'n',
          'key': 'property'
          },
        'value': 'ob'
      }
      """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      n.property CONTAINS "goodie"
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'function': 'contains',
        'property_lookup': {
          'alias': 'n',
          'key': 'property'
          },
        'value': 'goodie'
      }
      """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      someVariable IS NULL
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'type_matching': 'is_null',
        'variable': 'someVariable',
      }
      """

  @patterns @expression
  Scenario: Parse a where pattern query string
    Given we have a "expression" grammar expression
    When we parse the given query pattern string through the parse function
      """
      someVariable IS NULL or n.property == "Bob" or n.name == "Jen"
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'clause': 'OR',
        'value': 'Bob',
        'type_matching': 'is_null',
        'key': {
          'alias': 'n',
          'key': 'property'
        },
        'variable': 'someVariable',
        'operation': 'neq'
      }
      """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE NOT(n.name = 'apa' AND false)
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n.name <> 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE exists(n.name)
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n.number >= 1 AND n.number <= 10
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE 1 <= n.number <= 10
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n:PERSON
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

#   @patterns @where
#   Scenario: Parse a where pattern query string
#     Given we have a "where_pattern" grammar expression
#     When we parse the given query pattern string through the parse function
#       """
#       WHERE identifier IS NULL
#       """
#     Then it should transform the parsing result into dictionary result
#     """
#     {
#       NOT IMPLEMENTED
#     }
#     """
  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE NOT exists(n.name) OR n.name = 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n.name = 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n["name"] = 'Bob'
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n.name STARTS WITH "B" OR
            n.name ENDS WITH "b" OR
            n.name CONTAINS "o"
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n.name =~ "Bob.*"
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns @where
  Scenario: Parse a where pattern query string
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE n.name IN ['Bob', 'Jane']
      """
    Then it should transform the parsing result into dictionary result
    """
    {
      NOT IMPLEMENTED
    }
    """

  @patterns
  Scenario: Parse a single node/vertex pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n:Person)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertices": [
          {
            "alias": "n",
            "labels": [{"label": "Person"}]
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a multiple node/vertex pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n:Person),(m:Movie)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertices": [
          {
            "alias": "n",
            "labels": [{"label": "Person"}]
          },
          {
            "alias": "m",
            "labels": [{"label": "Movie"}]
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a single node/vertex with multiple label pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n:Person:Swedish)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertices": [
          {
            "alias": "n",
            "labels": [
              {"label": "Person"},
              {"label": "Swedish"}
            ]
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node/vertex with a property query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n:Person {'name': 'Bob'})
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "vertices": [
          {
            "alias": "n",
            "labels": [{"label": "Person"}],
            "properties": {"name": "Bob"}
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node outbound connection to another node pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)-->(m)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "edges": [
          {"in": False, "out": True}
        ],
        "vertices": [
          {
            "alias": "n"
          },
          {
            "alias": "m"
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node connected to another node pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)--(m)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "edges": [
          {"in": True, "out": True}
        ],
        "vertices": [
          {
            "alias": "n"
          },
          {
            "alias": "m"
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a person labeled node connected to another node pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n:Person)-->(m)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "edges": [
          {"in": False, "out": True}
        ],
        "vertices": [
          {
            "alias": "n",
            "labels": [{"label": "Person"}]
          },
          {
            "alias": "m"
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node with inbound connection from another node with labeled edges pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)<-[:KNOWS]-(m)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
      "edges": [
          {
              "in": True,
              "out": False,
              "edge_body": {
                "labels": [{"label": "KNOWS"}]
              }
          }
        ],
        "vertices": [
          {
            "alias": "n"
          },
          {
            "alias": "m"
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node with outbound connection to another node with alias edge pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)-[r]->(m)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
      "edges": [
          {
              "in": False,
              "out": True,
              "edge_body": {
                "alias": "r",
              }
          }
        ],
        "vertices": [
          {
            "alias": "n"
          },
          {
            "alias": "m"
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node with outbound connection to another node with 1 to 5 edge hops pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)-[*1..5]->(m)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "edges": [
          {
              "in": False,
              "out": True,
              "edge_body": {
                "range_literal": {"max": 5, "min": 1},
              }
          }
        ],
        "vertices": [
          {
            "alias": "n"
          },
          {
            "alias": "m"
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node with outbound connection to another node with unlimited edge hops pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)-[*]->(m)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "edges": [
          {
              "in": False,
              "out": True,
              "edge_body": {
                "range_literal": [],
              }
          }
        ],
        "vertices": [
          {
            "alias": "n"
          },
          {
            "alias": "m"
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a node with labeled outbound connection to another node that has properties pattern query string
    Given we have a "pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      (n)-[:KNOWS]->(m:Person {'name': 'Bob'})
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "edges": [
          {
              "in": False,
              "out": True,
              "edge_body": {
                "labels": [{"label": "KNOWS"}]
              }
          }
        ],
        "vertices": [
          {
            "alias": "n"
          },
          {
            "alias": "m",
            "labels": [{"label": "Person"}],
            "properties": {"name": "Bob"}
          }
        ]
      }
      """

  @patterns
  Scenario: Parse a where pattern
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE m.name = 'Bob'
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "where_pattern": {
          'clause': 'WHERE',
          'operation': 'eq',
          'property_lookup': {
            'alias': u'm',
            'key': u'name'
          },
          'value': u'Bob',
          'alias': u'Bob'
        }
      }
      """

  @patterns
  Scenario: Parse a where pattern
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE m.age > 32
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "where_pattern": {
          'clause': 'WHERE',
          'operation': 'gt',
          'property_lookup': {
            'alias': u'm',
            'key': u'age'
          },
          'value': u'32',
          'alias': u'32'
        }
      }
      """

  @patterns
  Scenario: Parse a where pattern
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE m.age >= 32
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "where_pattern": {
          'clause': 'WHERE',
          'operation': 'gte',
          'property_lookup': {
            'alias': u'm',
            'key': u'age'
          },
          'value': u'32',
          'alias': u'32'
        }
      }
      """

  @patterns
  Scenario: Parse a where pattern
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE m.age < 32
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "where_pattern": {
          'clause': 'WHERE',
          'operation': 'lt',
          'property_lookup': {
            'alias': u'm',
            'key': u'age'
          },
          'value': u'32',
          'alias': u'32'
        }
      }
      """

  @patterns
  Scenario: Parse a where pattern
    Given we have a "where_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      WHERE m.age <= 32
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "where_pattern": {
          'clause': 'WHERE',
          'operation': 'lte',
          'property_lookup': {
            'alias': u'm',
            'key': u'age'
          },
          'value': u'32',
          'alias': u'32'
        }
      }
      """

  @patterns
  Scenario: Parse a match pattern
    Given we have a "match_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      MATCH (n)
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "match_pattern": {
        'clause': 'MATCH',
        'vertices': [{'alias': u'n'}]
        }
      }
      """

  @patterns
  Scenario: Parse a match pattern
    Given we have a "match_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      MATCH (n)-[]-()
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        "match_pattern": {
        'clause': 'MATCH',
        'edges': [{'out': True, 'in': True, 'edge_body': []}],
        'vertices': [{'alias': u'n'}, []]
        }
      }
      """

  @patterns
  Scenario: Parse a match pattern
    Given we have a "match_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      MATCH (n)-[]-(m) WHERE n.key = value
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'match_pattern': {
          'clause': 'MATCH',
          'edges': [
            {'out': True, 'in': True, 'edge_body': []}
          ],
          'vertices': [
            {'alias': u'n'},
            {'alias': u'm'}
          ],
          'where_pattern': {
            'clause': 'WHERE',
            'operation': 'eq',
            'property_lookup': {
              'alias': u'n',
              'key': u'key'
            },
            'value': u'value',
            'alias': u'value'
          }
        }
      }
      """

  @patterns
  Scenario: Parse a match pattern
    Given we have a "match_pattern" grammar expression
    When we parse the given query pattern string through the parse function
      """
      MATCH (n)-[]-(m)<-[]-() WHERE n.key = value
      """
    Then it should transform the parsing result into dictionary result
      """
      {
        'match_pattern': {
          'clause': 'MATCH',
          'edges': [
            {'out': True, 'in': True, 'edge_body': []},
            {'out': False, 'in': True, 'edge_body': []}
          ],
          'vertices': [
            {'alias': u'n'},
            {'alias': u'm'},
            []
          ],
          'where_pattern': {
            'clause': 'WHERE',
            'operation': 'eq',
            'property_lookup': {
              'alias': u'n',
              'key': u'key'
            },
            'value': u'value',
            'alias': u'value'
          }
        }
      }
      """
