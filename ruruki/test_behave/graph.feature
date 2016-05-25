Feature: Graph features

  Background:
    Given we have a empty graph object

  @load
  Scenario: Load graph data from a dump file
    Given we have a file object with the following dump content
      """
      {
          "constraints": [],
          "edges": [
              {
                  "head_id": 0,
                  "id": 0,
                  "label": "TYPE",
                  "metadata": {},
                  "properties": {},
                  "tail_id": 1
              }
          ],
          "vertices": [
              {
                  "id": 0,
                  "label": "label1",
                  "metadata": {
                      "in_edge_count": 0,
                      "out_edge_count": 1
                  },
                  "properties": {}
              },
              {
                  "id": 1,
                  "label": "label2",
                  "metadata": {
                      "in_edge_count": 1,
                      "out_edge_count": 0
                  },
                  "properties": {}
              }
          ]
      }
      """
    When we load the dump into the database
    Then we expect to have "1" edge
    And the edges have
      | ident | head_ident  | label  | tail_ident | properties |
      | 0     | 0           | TYPE   | 1          | {}         |
    And we expect to have "2" vertices
    And the vertices have
      | ident | label  | properties |
      | 0     | label1 | {}         |
      | 1     | label2 | {}         |
