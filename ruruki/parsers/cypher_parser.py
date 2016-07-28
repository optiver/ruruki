#pylint: skip-file
"""
https://s3.amazonaws.com/artifacts.opencypher.org/cypher.ebnf
"""
import parsley
import collections


nodepattern = collections.namedtuple("NodePattern", "alias labels properties")
label = collections.namedtuple("Label", "name")


Parser = parsley.makeGrammar(
    r"""
    Cypher = WS Statement:s (WS ';')? WS -> ["Cypher", s]

    Statement = Query

    Query = RegularQuery

    RegularQuery = SingleQuery:sq (WS Union)*:u -> ["RegularQuery", sq, u]

    SingleQuery = Clause:head (WS Clause)*:tail -> ["SingleQuery", [head] + tail]

    Union = U N I O N SP (A L L)? SingleQuery:sq -> ["Union", sq]

    Clause = Match
           | Unwind
           | Merge
           | Create
           | Set
           | Delete
           | Remove
           | With
           | Return

    # TODO: Not usre if I need to handle optional !!
    Match = (O P T I O N A L SP)? M A T C H WS Pattern:p (WS Where)?:w -> ["Match", p, w]

    Unwind = U N W I N D WS Expression:ex SP A S SP Variable:v -> ["Unwind", ex, v]

    Merge = M E R G E WS PatternPart:head (SP MergeAction)*:tail -> ["Merge", [head] + tail]

    MergeAction = O N SP M A T C H SP Set:s -> ["MergeActionMatch", s]
                | O N SP C R E A T E SP Set:s -> ["MergeActionCreate", s]

    Create = C R E A T E WS Pattern:p -> ["Create", p]

    Set = S E T SP SetItem:head (WS ',' WS SetItem)*:tail -> ["Set", [head] + tail]

    SetItem = PropertyExpression:pex '=' Expression:ex -> ["SetItemPropertyExpression", pex, ex]
            | Variable:v '=' Expression:ex -> ["SetItem", v, ex]
            | Variable:v '+=' Expression:ex -> ["SetItem", v, ex]
            | Variable:v NodeLabels:ex -> ["SetItem", v, ex]

    Delete = (D E T A C H SP)? D E L E T E SP Expression:head (',' WS Expression )*:tail -> ["Delete", [head] + tail]

    Remove = R E M O V E SP RemoveItem:head (WS ',' WS RemoveItem)*:tail -> ["Remove", [head] + tail]

    RemoveItem = Variable:v NodeLabels:nl -> ["RemoveItemVar", v, nl]
                | PropertyExpression:p -> ["RemoveItemPe", p]

    With = W I T H (SP D I S T I N C T)?:d SP ReturnBody:rb (Where)?:w -> ["With", d, rb, w]

    Return = R E T U R N (SP D I S T I N C T)?:d SP ReturnBody:rb -> ["Return", d, rb]

    ReturnBody = ReturnItems:ri (SP Order)?:o (SP Skip)?:s (SP Limit)?:l -> ["ReturnBody", ri, o, s, l]

    ReturnItems = ('*' | ReturnItem):head
                (WS ',' WS ReturnItem )*:tail -> ["ReturnItems", [head] + tail]

    ReturnItem = Expression:ex SP A S SP Variable:v -> ["ReturnItem", ex, v]
                | Expression:ex -> ["ReturnItem", ex, None]

    Order =  O R D E R SP B Y SP SortItem:head (',' WS SortItem)*:tail -> ["Order", [head] + tail]

    Skip =  S K I P SP Expression:ex -> ["Skip", ex]

    Limit =  L I M I T SP Expression:ex -> ["Limit", ex]

    SortItem = Expression:ex (D E S C E N D I N G | D E S C) -> ["sort", ex, "desc"]
             | Expression:ex (A S C E N D I N G | A S C)? -> ["sort", ex, "asc"]

    Where = W H E R E SP Expression:ex -> ["Where", ex]

    Pattern = PatternPart:head (',' WS PatternPart)*:tail -> [head] + tail

    PatternPart = (Variable:v WS '=' WS AnonymousPatternPart:ap) -> ["PatternPart", v, ap]
                | AnonymousPatternPart:ap -> ["PatternPart", None, ap]

    AnonymousPatternPart = PatternElement

    PatternElement = (
                        NodePattern:np
                        (WS PatternElementChain)*:pec
                    ) -> ["PatternElement", np, pec]
                    | '(' PatternElement:pe ')' -> pe

    NodePattern = '(' WS
                 (
                    Variable:v WS -> v
                 )?:v
                 (
                     NodeLabels:nl WS -> nl
                 )?:nl
                 (
                     Properties:p WS -> p
                 )?:p
                ')' -> nodepattern(v, nl, p)

    PatternElementChain = RelationshipPattern:rp WS NodePattern:np -> ["PatternElementChain", rp, np]

    RelationshipPattern = LeftArrowHead?:la WS Dash WS RelationshipDetail?:rd WS Dash WS RightArrowHead?:ra -> ["RelationshipsPattern", la, rd, ra]

    RelationshipDetail = '['
                      Variable?:v
                      '?'?:q
                      RelationshipTypes?:rt
                      ('*' RangeLiteral)?:rl WS
                      Properties?:p
                      ']' -> ["RelationshipDetail", v, q, rt, rl, p]

    Properties = MapLiteral
               | Parameter

    RelationshipTypes = ':' RelTypeName:head (WS '|' ':'? WS RelTypeName)*:tail -> ["RelationshipTypes", head] + tail

    NodeLabels = NodeLabel:head (WS NodeLabel)*:tail -> [head] + tail

    NodeLabel = ':' LabelName:n -> label(n)

    RangeLiteral = (WS IntegerLiteral)?:start WS ('..' WS IntegerLiteral)?:stop WS -> slice(start, stop)

    LabelName = SymbolicName

    RelTypeName = SymbolicName

    Expression = Expression12

    Expression12 = Expression11:ex1 SP O R SP Expression12:ex2 -> ["or", ex1, ex2]
                 | Expression11

    Expression11 = Expression10:ex1 SP X O R SP Expression11:ex2 -> ["xor", ex1, ex2]
                 | Expression10

    Expression10 = Expression9:ex1 SP A N D SP Expression10:ex2 -> ["and", ex1, ex2]
                 | Expression9

    Expression9 = SP N O T SP Expression9:ex -> ["not", ex]
                | Expression8

    Expression8 = Expression7:ex1 WS '='  WS Expression8:ex2 -> ["eq",  ex1, ex2]
                | Expression7:ex1 WS '<>' WS Expression8:ex2 -> ["neq", ex1, ex2]
                | Expression7:ex1 WS '!=' WS Expression8:ex2 -> ["neq", ex1, ex2]
                | Expression7:ex1 WS '<'  WS Expression8:ex2 -> ["lt",  ex1, ex2]
                | Expression7:ex1 WS '>'  WS Expression8:ex2 -> ["gt",  ex1, ex2]
                | Expression7:ex1 WS '<=' WS Expression8:ex2 -> ["lte", ex1, ex2]
                | Expression7:ex1 WS '>=' WS Expression8:ex2 -> ["gte", ex1, ex2]
                | Expression7

    Expression7 = Expression6:ex1 WS '+' WS Expression7:ex2 -> ["add", ex1, ex2]
                | Expression6:ex1 WS '-' WS Expression7:ex2 -> ["sub", ex1, ex2]
                | Expression6

    Expression6 = Expression5:ex1 WS '*' WS Expression6:ex2 -> ["multi", ex1, ex2]
                | Expression5:ex1 WS '/' WS Expression6:ex2 -> ["div",   ex1, ex2]
                | Expression5:ex1 WS '%' WS Expression6:ex2 -> ["mod",   ex1, ex2]
                | Expression5

    Expression5 = Expression4:ex1 WS '^' WS Expression5:ex2 -> ["hat", ex1, ex2]
                | Expression4

    Expression4 = '+' WS Expression4
                | '-' WS Expression4:ex -> ["minus", ex]
                | Expression3

    Expression3 = Expression2:ex1
                  (
                    WS '[' Expression:prop_name ']' -> ["PropertyLookup", prop_name]
                    | WS '[' Expression?:start '..' Expression?:end ']' -> ["slice", start, end]
                    | (
                        WS '=~' -> "regex"
                        | SP I N -> "in"
                        | SP S T A R T S SP W I T H -> "starts_with"
                        | SP E N D S SP W I T H  -> "ends_with"
                        | SP C O N T A I N S  -> "contains"
                    ):operator WS Expression2:ex2 -> [operator, ex2]
                    | SP I S SP N U L L  -> ["is_null"]
                    | SP I S SP N O T SP N U L L -> ["is_not_null"]
                  )+:c -> ["Expression3", ex1, c]
                  | Expression2

    Expression2 = Atom:a (PropertyLookup | NodeLabels)+:c -> ["Expression2", a, c]
                  | Atom

    Atom = NumberLiteral
         | StringLiteral
         | Parameter
         | T R U E -> True
         | F A L S E -> False
         | N U L L -> None
         | CaseExpression
         | C O U N T '(' '*' ')' -> ["count *"]
         | MapLiteral
         | ListComprehension
         | '['
                (
                    WS Expression:head WS
                    (',' WS Expression:item WS -> item
                    )*:tail -> [head] + tail
                    |
                    -> []
                ):ex
            ']' -> ex
         | F I L T E R WS '(' WS FilterExpression:fex WS ')' -> fex
         | E X T R A C T WS '(' WS FilterExpression:fex WS (WS '|' Expression)?:ex ')' -> [fex, ex]
         | A L L WS '(' WS FilterExpression:fex WS ')' -> fex
         | A N Y WS '(' WS FilterExpression:fex WS ')' -> fex
         | N O N E WS '(' WS FilterExpression:fex WS ')' -> fex
         | S I N G L E WS '(' WS FilterExpression:fex WS ')' -> fex
         | RelationshipsPattern
         | parenthesizedExpression
         | FunctionInvocation
         | Variable

    parenthesizedExpression = '(' WS Expression:ex WS ')' -> ex

    RelationshipsPattern = NodePattern:np (WS PatternElementChain)?:pec -> ["RelationshipsPattern", np, pec]

    FilterExpression = IdInColl:i (WS Where)?:w -> ["FilterExpression", i, w]

    IdInColl = Variable:v SP I N SP Expression:ex -> ["IdInColl", v, ex]

    FunctionInvocation = FunctionName:func
                        WS '(' WS
                        (D I S T I N C T WS -> "distinct")?:distinct
                        (
                            Expression:head
                            (
                                ',' WS Expression
                            )*:tail -> [head] + tail
                        | -> []
                        ):args
                        WS ')' -> ["call", func, distinct, args]

    FunctionName = SymbolicName

    ListComprehension = '[' FilterExpression:fex (WS '|' Expression)?:ex ']' -> ["ListComprehension", fex, ex]

    # PropertyLookup = WS '.' WS ((PropertyKeyName ('?' | '!')) | PropertyKeyName)
    PropertyLookup = WS '.' WS PropertyKeyName:n -> ["PropertyLookup", n]

    CaseExpression =
                     C A S E
                     (Expression)?:ex
                     (WS CaseAlternatives)+:cas 
                     (WS E L S E WS Expression)?:el
                     WS E N D
                     -> ["Case", ex, cas, el]

    CaseAlternatives = W H E N WS Expression:ex1 WS T H E N WS Expression:ex2 -> ["CaseAlternatives", ex1, ex2]

    Variable = SymbolicName

    StringLiteral = '"' (~('"'|'\\') anything | EscapedChar)*:cs '"' -> "".join(cs)
                  | "'" (~("'"|'\\') anything | EscapedChar)*:cs "'" -> "".join(cs)

    EscapedChar = '\\'
                ('\\' -> '\\'
                | "'" -> "'"
                | '"' -> '"'
                | N -> '\n'
                | R -> '\r'
                | T -> '\t'
                | '_' -> '_'
                | '%' -> '%'
                )

    NumberLiteral = DoubleLiteral
                  | IntegerLiteral

    MapLiteral = '{' WS
                 (
                    (
                        PropertyKeyName:k WS ':' WS Expression:v -> (k, v)
                    ):head WS
                    (
                        ',' WS PropertyKeyName:k WS ':' WS Expression:v WS -> (k, v)
                    )*:tail -> [head] + tail
                 | -> []):pairs
                '}' -> dict(pairs)

    Parameter = '{' WS (SymbolicName | DecimalInteger):p WS '}' -> ["Parameter", p]

    PropertyExpression = Atom:a (WS PropertyLookup)*:opts -> ["Expression", a, opts]

    PropertyKeyName = SymbolicName

    IntegerLiteral = HexInteger
                   | OctalInteger
                   | DecimalInteger

    OctalDigit = ~('8'|'9') digit

    OctalInteger = '0' <OctalDigit+>:ds -> int(ds, 8)

    HexDigit = digit | A | B | C | D | E | F

    HexInteger = '0' X <HexDigit+>:ds -> int(ds, 16)

    DecimalInteger = <digit+>:ds -> int(ds)

    DoubleLiteral = ExponentDecimalReal
                  | RegularDecimalReal

    ExponentDecimalReal = <(DecimalInteger | RegularDecimalReal) E DecimalInteger>:ds -> float(ds)

    RegularDecimalReal = <digit+ '.' digit+>:ds -> float(ds)

    SymbolicName = UnescapedSymbolicName
                 | EscapedSymbolicName

    UnescapedSymbolicName = <letter ('_' | letterOrDigit)*>

    EscapedSymbolicName = '`' (~'`' anything | "``" -> '`')*:cs '`' -> "".join(cs)

    WS = whitespace*

    SP = whitespace+

    whitespace = ' '
               | '\t'
               | '\n'
               | Comment

    Comment = "/*" (~"*/" anything)* "*/"
            | "//" (~('\r'|'\n') anything)* '\r'? ('\n'|end)

    LeftArrowHead = '<'

    RightArrowHead = '>'

    Dash = '-'

    A = 'A' | 'a'

    B = 'B' | 'b'

    C = 'C' | 'c'

    D = 'D' | 'd'

    E = 'E' | 'e'

    F = 'F' | 'f'

    G = 'G' | 'g'

    H = 'H' | 'h'

    I = 'I' | 'i'

    K = 'K' | 'k'

    L = 'L' | 'l'

    M = 'M' | 'm'

    N = 'N' | 'n'

    O = 'O' | 'o'

    P = 'P' | 'p'

    R = 'R' | 'r'

    S = 'S' | 's'

    T = 'T' | 't'

    U = 'U' | 'u'

    V = 'V' | 'v'

    W = 'W' | 'w'

    X = 'X' | 'x'

    Y = 'Y' | 'y'

    Z = 'Z' | 'z'
    """,
    {
        "nodepattern": nodepattern,
        "label": label,
    }, unwrap=False
)

from pprint import pprint
# import sys
# q = "create (Neo:Crew {name:'Neo'}), (Morpheus:Crew {name: 'Morpheus'})"
q1 = "1 + 2 - 3 + 4"
q = """
MATCH
  (c:Customer {custNo: '1234567890'})-[rco:SUPPORTED_BY]->(o:OrgUnit)<-[roe:MEMBER_OF]-(e:Employee)
WHERE
  COALESCE(rco.validFrom, 0) <= timestamp()
RETURN c as node
"""
# print q
p = Parser(q)
pprint(p.Cypher())
# pprint(
#     Parser(sys.stdin.read()).Cypher()
# )
