from enum import Enum

error_msg = "eroare desc"

# https://en.wikipedia.org/wiki/Lexical_analysis#Lexical_token_and_lexical_tokenization
class Token(Enum):
    KEYWORD = 1
    IDENTIFIER = 2
    SEPARATOR = 3
    OPERATOR = 4
    LITERAL = 5
    COMMENT = 6
    WHITESPACE = 7
    ERROR = 8 # folosim pt a semnala erori
    END = 9 # marcam sfarsitul fisierului input

class TokenNode:
    def __init__(self, token : Token,  length : int, word : str):
        self.word = word
        self.token = token
        self.length = length
        self.line = 0 # incrementat in loop-ul principal
        self.start = 0 # adresa primul caracter

# Codul de citit
file = open("code.txt", "r")

# https://en.cppreference.com/w/cpp/keywords.html
keywords = [
    "int",
    "main",
    "string",
    "if",
    "else",
    "return",

    "(", ")",
    "{", "}",
    ",",
    ";",
    "&", "&&",
    "|", "||",
    "%",
    "^",
    "=", "==",
    "+", "++", "+=",
    "-", "--", "-=",
    "*", "*=",
    "/", "/=",
    "\\", "//", "/*", "*/"
    "\"", "\'",
]

DFA = dict()

def init_DFA():
    for kw in keywords:
        d = DFA
        for i in range( len(kw) ):
            node = d.get(kw[i], -1)
            if node == -1:
                d[kw[i]] = dict()

            if i == (len(kw)-1): # marcam ca aici este un keyword valid
                d[kw[i]]["VALID"] = 1
            
            d = d[kw[i]]

# ---- tuple[cuvant, Token, lungime] ----
# Fiecare lexer are o referinta la DFA care este parcursa cu fiecare caracter
def interpret_token_error(start : int) -> TokenNode:
    file.seek(start)
    
    token = Token.ERROR
    length = 0
    word = ""

    read_dot = False # Sa nu citim . de 2 ori

    while c := file.read(1):
        if c.isspace(): break

        word += c
        length += 1

    return TokenNode(token, length, word)

def interpret_token_alphanum(start : int) -> TokenNode:
    file.seek(start)

    token = Token.KEYWORD
    length = 0
    word = ""
    node = DFA

    while c := file.read(1):
        if c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_1234567890":
            break

        word += c
        length += 1

        if node.get(c):
            node = node[c]
        else:
            token = Token.IDENTIFIER
    
    return TokenNode(token, length, word)

def interpret_token_num(start : int) -> TokenNode:
    file.seek(start)
    
    token = Token.LITERAL
    length = 0
    word = ""

    read_dot = False # Sa nu citim . de 2 ori

    while c := file.read(1):
        if c.isspace(): break
        if c == "." and not read_dot: read_dot = True 
        elif c == "." and read_dot:
            print("#### error numar invalid ####")
            return interpret_token_error(start)
        elif c.isalpha():
            print("#### error numar invalid ####")
            return interpret_token_error(start)
        elif not c.isnumeric(): break

        word += c
        length += 1

    return TokenNode(token, length, word)

def interpret_token_single_comment(start : int) -> TokenNode:
    file.seek(start+2) # Ignoram primul caracter "

    token = Token.COMMENT
    length = 2
    word = "//"

    while c := file.read(1):
        if c == '\n': break
        word += c
        length += 1
    
    return TokenNode(token, length, word)

def interpret_token_multi_comment(start : int) -> TokenNode:
    file.seek(start+2) # Ignoram primul caracter "

    token = Token.COMMENT
    length = 2
    word = "/*"
    comment_finished = False

    read_star = False

    while c := file.read(1):
        if c == '*': read_star = True
        elif c == "/" and read_star == True:
            word += "/"
            length += 1
            comment_finished = True
            break

        if read_star and c != "*":
            read_star = False
            length += 1
            word += "*"

        word += c
        length += 1
    
    if not comment_finished:
        print("#### ERROR comment multi-line nefinalizat ####")
        return TokenNode(Token.ERROR, length, word)
    return TokenNode(token, length, word)

def interpret_token_string(start : int) -> TokenNode:
    file.seek(start+1) # Ignoram primul caracter "

    token = Token.LITERAL
    length = 1
    word = "\""

    escaped = False # Tinem minte pentru a nu termina string-ul la un \"

    while c := file.read(1):
        length += 1
        word += c

        if c != '"' and escaped: escaped = False # Evitam cazul "\\"
        elif c == "\\": escaped = True 
        
        if c == '"' and not escaped: break
    
    return TokenNode(token, length, word)

def interpret_token_symbol(start : int) -> TokenNode:
    file.seek(start)

    token = Token.OPERATOR
    length = 0
    word = ""
    node = DFA

    while c := file.read(1):
        if c.isalnum(): break

        if node.get(c):
            node = node[c]
        else:
            break

        word += c
        length += 1
    
    if len(word) == 1 and word in "()[]}{;,.": token = Token.SEPARATOR
    elif word == "//": return interpret_token_single_comment(start)
    elif word == "/*": return interpret_token_multi_comment(start)
    return TokenNode(token, length, word)

def interpret_token(start : int) -> TokenNode:
    file.seek(start)

    c = file.read(1)
    if not c:           return TokenNode(Token.END, 0, "")
    elif c.isspace():   return TokenNode(Token.WHITESPACE, 1, c) # WHITESPACE
    elif c == "\"":     return interpret_token_string(start) # LITERAL (string)
    elif c.isalpha():   return interpret_token_alphanum(start) # KEYWORD / IDENTIFIER
    elif c.isnumeric(): return interpret_token_num(start) # LITERAL (numar)
    else:               return interpret_token_symbol(start) # OPERATOR / SEPARATOR / COMMENT

init_DFA()

i = 0
line = 0
while 1:
    temp : TokenNode = interpret_token(i)
    
    if temp.word == "\n": line += 1
    temp.line = line
    temp.start = i

    if temp.token not in (Token.WHITESPACE, Token.END):
        print(f"\"{temp.word}\", linia {temp.line}, {temp.token}, {temp.length}")
    i += temp.length

    if temp.token == Token.WHITESPACE: continue
    if temp.token == Token.ERROR:
        print("#### ERROR: INVALID TOKEN ####")
        print(error_msg)
    if temp.word == "": exit()