from lox.tokens import Token, TokenType, KEYWORDS


class Scanner(object):
    def __init__(self, source, verbose=False):
        self.verbose = verbose
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []

    def _is_at_end(self):
        return self.current >= len(self.source)

    def scan_tokens(self):
        while not self._is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def _advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def match(self, expected):
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _peek(self):
        return '\0' if self._is_at_end() else self.source[self.current]

    def _peek_next(self):
        index = self.current + 1
        return self.source[index] if index < len(self.source) else '\0'

    def scan_token(self):
        c = self._advance()
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                # comments go the end of the line
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in ' \r\t':
            # ignore whitespace
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string()
        elif self._is_digit(c):
            self.number()
        elif self._is_alpha(c):
            self.identifier()
        else:
            print("ERROR!! Unexpected character: '{}'".format(c))

    def string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                # multiline string!
                self.line += 1
            self._advance()

        if self._is_at_end():
            # unterminated string!
            print("ERROR! unterminated string!")
            return

        # move past close of string
        self._advance()
        text = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, text)

    def _is_digit(self, c):
        return c >= '0' and c <= '9'

    def _is_alpha(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def _is_alphanumeric(self, c):
        return self._is_digit(c) or self._is_alpha(c)

    def number(self):
        while self._is_digit(self._peek()):
            self._advance()
        if self._peek() == '.' and self._is_digit(self._peek_next()):
            self._advance()
        while self._is_digit(self._peek()):
            self._advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def identifier(self):
        while self._is_alphanumeric(self._peek()):
            self._advance()

        text = self.source[self.start:self.current]
        if text in KEYWORDS:
            # lox-defined keyword
            self.add_token(KEYWORDS[text])
        else:
            # user-defined keyword
            self.add_token(TokenType.IDENTIFIER)
