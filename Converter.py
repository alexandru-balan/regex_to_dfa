import ply.lex as lex
import networkx as nx
import matplotlib.pyplot as plt

# Tokens
tokens = (
    'OPEN_P',
    'CLOSED_P',
    'OR',
    'STAR',
    'CONCAT',
    'LETTER',
    'LAMBDA'
)

# Rules that define the tokens
t_OPEN_P = r'\('
t_CLOSED_P = r'\)'
t_OR = r'\|'
t_STAR = r'\*'
t_CONCAT = r'\.'
t_LETTER = r'[a-zA-Z]'
t_LAMBDA = r'\$'


# Error rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def _getContent(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()

    return content


class RegexLexer:
    # A lexer to tokenize the content
    lexer = lex.lex()
    # A container containing the tokens
    parts = []

    def __init__(self, filename=None):
        if filename is not None:
            self.filename = filename
            self.content = _getContent(filename)
            self.content = '(' + self.content + ')$'
            self.tokenize()
        else:
            print("The file name was empty")

    def tokenize(self):
        self.lexer.input(self.content)
        while True:
            token = self.lexer.token()
            if not token:
                break
            self.parts.append(token)

    def printTokens(self):
        for part in self.parts:
            print(part)

    def addConcats(self):
        possibleConcat = False
        concatMessage = ''
        index = 0

        for part in self.parts:
            if part.type in ['LETTER', 'LAMBDA']:
                if possibleConcat is True:
                    concatMessage = concatMessage + '.'
                else:
                    possibleConcat = True
            elif part.type in ['STAR', 'CLOSED_P']:
                possibleConcat = True
            elif (part.type == 'OPEN_P') & (self.parts[index - 1].type in ['LETTER', 'STAR']):
                concatMessage = concatMessage + '.'
            else:
                possibleConcat = False
            concatMessage = concatMessage + part.value
            index = index + 1

        self.content = concatMessage
        self.parts.clear()
        self.tokenize()

    def writeAsRPN(self, permanent=False):
        # First we need to have the regex written in reverse polish notation
        operator_stack = []
        last_index = -1
        rpn_regex = ''

        for part in self.parts:
            if part.type in ['LETTER', 'STAR', 'LAMBDA']:
                rpn_regex = rpn_regex + part.value
                continue

            if part.type == 'OPEN_P':
                operator_stack.append(part)
                last_index += 1
                continue

            if part.type == 'CLOSED_P':
                while operator_stack[last_index].type != 'OPEN_P':
                    rpn_regex += operator_stack[last_index].value
                    operator_stack.pop()
                    last_index -= 1
                # Doing one more pop to  extract the open parenthesis
                operator_stack.pop()
                last_index -= 1
                continue

            if part.type in ['OR', 'CONCAT']:
                if last_index >= 0:
                    if operator_stack[last_index].type not in ['OPEN_P', 'CLOSED_P']:
                        rpn_regex += operator_stack[last_index].value
                        operator_stack.pop()
                        operator_stack.append(part)
                    else:
                        operator_stack.append(part)
                        last_index += 1
                else:
                    operator_stack.append(part)
                    last_index += 1
                continue

        # Clearing the stack of any operators that might have remained
        while len(operator_stack) != 0:
            rpn_regex += operator_stack[last_index].value
            operator_stack.pop()

        if permanent is True:
            self.parts.clear()
            self.content = rpn_regex
            self.tokenize()

        return rpn_regex

    def makeAST(self):
        self.writeAsRPN(permanent=True)
        AST = nx.DiGraph()
        node_stack = []
        last_index = -1

        for part in self.parts:
            if part.type in ['LETTER', 'LAMBDA']:
                AST.add_node(part, val=part.value)
                node_stack.append(part)
                last_index += 1
            elif part.type in ['OR', 'CONCAT']:
                AST.add_node(part, val=part.value)
                for i in range(0, 2):
                    AST.add_edge(part, node_stack[last_index])
                    node_stack.pop()
                    last_index -= 1
                node_stack.append(part)
                last_index += 1
            elif part.type == 'STAR':
                AST.add_node(part, val=part.value)
                AST.add_edge(part, node_stack[last_index])
                node_stack.pop()
                node_stack.append(part)

        return AST

    def printAST(self):
        AST = self.makeAST()
        nx.nx_agraph.write_dot(AST, 'test.dot')
        pos = nx.nx_agraph.graphviz_layout(AST, prog='dot')
        nx.draw(AST, pos, node_color='cyan')
        nx.draw_networkx_labels(AST, pos, nx.get_node_attributes(AST, 'val'))

        plt.savefig('ast.png')
        plt.show()


class Converter:
    FirstPos = [[]]
    LastPos = []

    def __init__(self, AST: nx.DiGraph, rpn_tokens: list):
        """
        :param AST (networkx.DiGraph): an abstract syntax tree obtained from RegexLexer.makeAST()
        :param rpn_tokens(ist<ply.lex.LexToken>): RegexLexer.content after running RegexLexer.writeAsRPN(permanent=True)
        """
        self.AST = AST
        self.rpn_tokens = rpn_tokens

    def _makeFirstPos(self):
        """
        This method is used to compute the first_pos list for each token
        :return: nothing
        """
        index = 0
        letter_no = 1
        for token in self.rpn_tokens:
            if token.type in ['LETTER', 'LAMBDA']:
                self.FirstPos[index].append(letter_no)
                letter_no += 1
                index += 1
            elif token.type == 'OR':
                self.FirstPos[index].append(letter_no - 1)
                self.FirstPos[index].append(letter_no - 2)
                index += 1
            elif token.type == 'STAR':
                self.FirstPos[index] = self.FirstPos[index - 1]
            elif token.type == 'CONCAT':
                self.FirstPos[index] = self.FirstPos[index - 2]


if __name__ == '__main__':
    regexlexer = RegexLexer("input.txt")

    # Printing original regular expression
    print("Original regex: " + regexlexer.content + '\n')
    regexlexer.printTokens()

    # Rewrite regex with concatenations
    regexlexer.addConcats()

    # Print regex after rewrite
    print("\nRegex after adding concatenations: " + regexlexer.content + '\n')
    regexlexer.printTokens()

    print("\nRegex written in reverse polish notation: " + regexlexer.writeAsRPN() + '\n')
