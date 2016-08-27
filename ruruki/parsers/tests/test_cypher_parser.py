#pylint: skip-file
from ruruki.parsers import cypher_parser
from ruruki.test_utils import base



class TestCypherEval(base.TestBase):
    def eval_query(self, query_string, expected_value):
        ast = cypher_parser.Parser(query_string).Cypher()
        value = cypher_parser.cypher_eval(
            ast, {"__entityset__": self.graph.vertices}
        )
        self.assertEqual(
            expected_value, value
        )

    def eval_expression(self, query_string, expected_value, context={}):
        ast = cypher_parser.Parser(query_string).Expression()
        value = cypher_parser.cypher_eval(ast, context)
        self.assertEqual(
            expected_value, value
        )

    def test_literal_number(self):
        self.eval_expression("1234", 1234)

    def test_literal_string(self):
        self.eval_expression("'abc'", "abc")

    def test_variable(self):
        self.eval_expression("abc", 42, {"abc": 42})

    def test_literal_true(self):
        self.eval_expression("TRUE", True)

    def test_literal_false(self):
        self.eval_expression("FALSE", False)

    def test_literal_null(self):
        self.eval_expression("NULL", None)

    def test_expression4(self):
        self.eval_expression("+4", 4)

    def test_expression4_minus(self):
        self.eval_expression("-4", -4)

    def test_expression5(self):
        self.eval_expression("2^3", 8)

    def test_expression6_multi(self):
        self.eval_expression("2*4", 8)

    def test_expression6_div(self):
        self.eval_expression("8/4", 2)

    def test_expression6_mod(self):
        self.eval_expression("7%4", 3)

    def test_expression6_a_times_b(self):
        self.eval_expression("a*b", 8, {"a": 2, "b": 4})

    def test_expression7_add(self):
        self.eval_expression("2+4", 6)

    def test_expression7_minus(self):
        self.eval_expression("8-4", 4)

    def test_expression8_eq(self):
        self.eval_expression("8=8", True)
        self.eval_expression("8=7", False)

    def test_expression8_neq(self):
        self.eval_expression("8<>7", True)
        self.eval_expression("8<>8", False)
        self.eval_expression("8!=7", True)
        self.eval_expression("8!=8", False)

    def test_expression8_lt(self):
        self.eval_expression("8<7", False)
        self.eval_expression("4<8", True)
        self.eval_expression("8<8", False)

    def test_expression8_gt(self):
        self.eval_expression("8>4", True)
        self.eval_expression("4>8", False)
        self.eval_expression("8>8", False)

    def test_expression8_lte(self):
        self.eval_expression("8<=4", False)
        self.eval_expression("4<=8", True)
        self.eval_expression("8<=8", True)

    def test_expression8_gte(self):
        self.eval_expression("8>=4", True)
        self.eval_expression("4>=8", False)
        self.eval_expression("8>=8", True)

    def test_expression9(self):
        self.eval_expression("NOT TRUE", False)

    def test_expression10_and(self):
        self.eval_expression("TRUE and TRUE", True)
        self.eval_expression("TRUE and FALSE", False)
        self.eval_expression("FALSE and TRUE", False)
        self.eval_expression("FALSE and FALSE", False)

    def test_expression11_xor(self):
        self.eval_expression("TRUE xor TRUE", False)
        self.eval_expression("TRUE xor FALSE", True)
        self.eval_expression("FALSE xor TRUE", True)
        self.eval_expression("FALSE xor FALSE", False)

    def test_expression12_or(self):
        self.eval_expression("TRUE or TRUE", True)
        self.eval_expression("TRUE or FALSE", True)
        self.eval_expression("FALSE or TRUE", True)
        self.eval_expression("FALSE or FALSE", False)

    def test_list(self):
        self.eval_expression("[1, 2, 3]", [1, 2, 3])

    def test_case(self):
        q = "CASE x WHEN 1 THEN 'hello' WHEN 2 THEN 'bye' ELSE 'what?' END"
        self.eval_expression(q, "hello", {"x": 1})
        self.eval_expression(q, "bye", {"x": 2})
        self.eval_expression(q, "what?", {"x": 3})

    def test_simplest_query(self):
        self.eval_query("RETURN 1 + 2 as a;", {"a": 3})

    # def test_simple_match_query(self):
    #     self.eval_query("MATCH (a) RETURN a;", self.graph.vertices)
