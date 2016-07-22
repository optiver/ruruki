import parsley


Parser = parsley.makeGrammar(
    r"""

    # Atom = NumberLiteral
    #      | StringLiteral
    #      | Parameter
    #      | (T,R,U,E)
    #      | (F,A,L,S,E)
    #      | (N,U,L,L)
    #      | ((C,O,U,N,T), '(', '*', ')')
    #      | MapLiteral
    #      | ListComprehension
    #      | ('[', WS, Expression, WS, { ',', WS, Expression, WS }, ']')
    #      | ((F,I,L,T,E,R), WS, '(', WS, FilterExpression, WS, ')')
    #      | ((E,X,T,R,A,C,T), WS, '(', WS, FilterExpression, WS, [WS, '|', Expression], ')')
    #      | ((A,L,L), WS, '(', WS, FilterExpression, WS, ')')
    #      | ((A,N,Y), WS, '(', WS, FilterExpression, WS, ')')
    #      | ((N,O,N,E), WS, '(', WS, FilterExpression, WS, ')')
    #      | ((S,I,N,G,L,E), WS, '(', WS, FilterExpression, WS, ')')
    #      | RelationshipsPattern
    #      | parenthesizedExpression
    #      | FunctionInvocation
    #      | Variable

    # PropertyLookup = WS '.' WS ((PropertyKeyName ('?' | '!')) | PropertyKeyName)

    PropertyLookup = WS '.' WS PropertyKeyName:n -> ["PropertyLookup", n]

    Variable = SymbolicName

    #  StringLiteral = ('"', { ANY - ('"' | '\') | EscapedChar }, '"')
    #                | ("'", { ANY - ("'" | '\') | EscapedChar }, "'")

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

    #PropertyExpression = Atom, { WS, PropertyLookup }-

    NumberLiteral = DoubleLiteral
                  | IntegerLiteral

    Parameter = '{' WS (SymbolicName | DecimalInteger):p WS '}' -> ["Parameter", p]

    PropertyKeyName = SymbolicName

    IntegerLiteral = HexInteger
                   | OctalInteger
                   | DecimalInteger

    OctalDigit = ~('8'|'9') digit

    OctalInteger = '0' <OctalDigit+>:ds -> int(ds, 8)

    HexDigit = digit | A | B | C | D | E | F

    HexInteger = '0' X <HexDigit+>:ds -> int(ds, 16)

    DecimalInteger = ~'0' <digit+>:ds -> int(ds)

    DoubleLiteral = ExponentDecimalReal
                  | RegularDecimalReal

    ExponentDecimalReal = <(DecimalInteger | RegularDecimalReal) E DecimalInteger>:ds -> float(ds)

    RegularDecimalReal = <digit+ '.' digit+>:ds -> float(ds)

    SymbolicName = UnescapedSymbolicName
                 | EscapedSymbolicName

    UnescapedSymbolicName = <letter letterOrDigit*>

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
    {}
)

p = Parser('"This is \\"\\n\\" a test"').StringLiteral()
print p
