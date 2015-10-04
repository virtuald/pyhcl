'''
    Originally tried to use the lexer that comes with ply, but couldn't
    figure out a good way to deal with nested comments. This implementation
    very closely follows the golang lexer implementation.
'''

class LexToken(object):
    def __init__(self, lexer, tok_type, value=None):
        self.type = tok_type
        self.value = value
        self.lineno = lexer.line
        self.lexpos = lexer.pos
    
    def __str__(self):
        return "LexToken(%s,%r,%d,%d)" % (self.type,self.value,self.lineno,self.lexpos)
    
    def __repr__(self):
        return str(self)

class Lexer(object):
    
    def input(self, s):
        self.input = s
        self.pos = -1
        self.col = 0
        self.line = 1
        self.lastNumber = False
    
    def token(self):
        
        while True:
            
            c = self.next()
            if c is None:
                return None
            
            if c.isspace():
                self.lastNumber = False
                continue
            
            if c in "#/":
                self.consumeComment(c)
                continue
            
            if c >= '0' and c <= '9':
                self.lastNumber = True
                self.backup()
                return self.lexNumber()
            
            # This is a hacky way to find 'e' and lex it, but it works
            if self.lastNumber:
                if c in 'eE':
                    next = self.next()
                    if next == '+':
                        return LexToken(self, "EPLUS")
                    elif next == '-':
                        return LexToken(self, "EMINUS")
                    else:
                        self.backup()
                        return LexToken(self, "EPLUS")
            
            self.lastNumber = False
            
            if c == ".":
                return LexToken(self, "PERIOD")
            elif c == "-":
                return LexToken(self, "MINUS")
            elif c == ",":
                return self.lexComma()
            elif c == "=":
                return LexToken(self, "EQUAL")
            elif c == "[":
                return LexToken(self, "LEFTBRACKET")
            elif c == "]":
                return LexToken(self, "RIGHTBRACKET")
            elif c == "{":
                return LexToken(self, "LEFTBRACE")
            elif c == "}":
                return LexToken(self, "RIGHTBRACE")
            elif c == '"':
                return self.lexString()
            elif c == "<":
                return self.lexHeredoc()
            else:
                self.backup()
                return self.lexId()
            
    def consumeComment(self, c):
        single = (c == '#')
        if not single:
            c = self.next()
            if c not in "/*":
                self.backup()
                return self.createErr("comment expected, got %s" % c)
            
            single = (c == "/")
            
        nested = 1
        
        while True:
            c = self.next()
            if c is None:
                # single-line comments can end with EOF
                if single:
                    self.backup()
                    return True
                return self.createErr("end of multi-line comment expected, got EOF")
            
            # Single line comments continue until a newline
            if single:
                if c == "\n":
                    return True
                
            # Multi-line comments continue until a */
            if c == "/":
                c = self.next()
                if c == "*":
                    nested += 1
                else:
                    self.backup()
            
            elif c == "*":
                c = self.next()
                if c == "/":
                    nested -= 1
                else:
                    self.backup()
            
            # If we're done with the comment, return!
            if nested == 0:
                return True
    
    def lexComma(self):

        while True:
            c = self.peek()

            if c.isspace():
                self.next()
                continue

            if c == "]":
                return LexToken(self, "COMMAEND")

            break

        return LexToken(self, "COMMA")

    def lexId(self):
        
        startPos = self.pos+1
        
        while True:
            c = self.next()
            if c is None:
                return self.createErr("EOF found when parsing identifier")
            
            if not c.isalnum() and c not in "_-":
                self.backup()
                break
        
        if startPos >= self.pos+1:
            return self.createErr("Unexpected character '%s'" % c)
         
        value = self.input[startPos:self.pos+1]
        
        if value == 'true':
            return LexToken(self, "BOOL", True)
        
        elif value == 'false':
            return LexToken(self, "BOOL", False)
        
        return LexToken(self, "IDENTIFIER", value)
        
        
    def lexHeredoc(self):
        
        if self.next() != "<":
            return self.createErr("Heredoc must start with <<")
        
        startPos = self.pos
        
        # Now determine the marker
        while True:
            c = self.next()
            if c is None:
                return self.createErr("EOF reached when parsing heredoc")
            
            # Newline signals the end of the marker
            if c == "\n":
                break
            
        marker = self.input[startPos+1:self.pos]
        if marker == "":
            return self.createErr("Heredoc must have a marker, e.g. <<FOO")
        
        check = True
        startPos = self.pos+1
        
        while True:
            c = self.next()
            
            # If we're checking, then check to see if we see the marker
            if check:
                check = False
                
                for i in marker:
                    if i != c:
                        break
                    
                    c = self.next()
                else:
                    break
                
            if c is None:
                return self.createErr("End of heredoc not found")
                
            if c == "\n":
                check = True
                endPos = self.pos
                
        value = self.input[startPos:endPos]
        return LexToken(self, "STRING", value)
            
        
    def lexNumber(self):
        
        startPos = self.pos+1
        gotPeriod = False
        
        while True:
            c = self.next()
            if c is None:
                return self.createErr("EOF in middle of number")
            
            if c == '.':
                if gotPeriod:
                    self.backup()
                    break
                gotPeriod = True
            elif c < '0' or c > '9':
                self.backup()
                break
        
        if not gotPeriod:
            value = int(self.input[startPos:self.pos+1])
            return LexToken(self, "NUMBER", value)
        
        value = float(self.input[startPos:self.pos+1])
        return LexToken(self, "FLOAT", value)
            
        
    def lexString(self):
        
        b = []
        braces = 0
        
        while True:
            c = self.next()
            if c is None:
                return self.createErr("EOF before string closed")
            
            if c == '"' and braces == 0:
                break
            
            # If we hit a newline, then its an error
            if c == '\n':
                return self.createErr("Newline before string closed")

            # If we're escaping a quote, then escape the quote
            if c == '\\':
                n = self.next()
                if n == '"':
                    c = n
                elif n == 'n':
                    c = '\n'
                elif n == '\\':
                    c = n
                else:
                    self.backup()
                
            if braces == 0 and c == "$" and self.peek() == "{":
                braces = 1
                b.append(c)
                c = self.next()   
            elif braces > 0 and c == "{":
                braces += 1
                
            if braces > 0 and c == "}":
                braces -= 1

            b.append(c)
        
        return LexToken(self, "STRING", ''.join(b))
    
    def next(self):
        
        if self.pos+1 >= len(self.input):
            self.w = 0
            return None
        
        self.pos += 1
        self.col += 1
        self.w = 1
        
        r = self.input[self.pos]
        if r == '\n':
            self.line += 1
            self.col = 0
        
        return r
    
    def peek(self):
        c = self.next()
        self.backup()
        return c
    
    def backup(self):
        self.col -= 1
        self.pos -= self.w
        
    def createErr(self, msg):
        raise ValueError("Line %d, column %d: %s" % (self.line, self.col, msg))
