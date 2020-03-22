# Converter from REGEX to DFA

## 1. Requirements:
- graphviz
- python3 (I used 3.8)
- pkg-config (or pkgconf on Arch based distributions)
- pip

### To install the requirements:
1. **Before cloning the repo**
   - On debian-based distros: `sudo apt install python3 python3-dev graphviz libraphviz-dev pkg-config python3-pip`
   - On arch-based distros: `sudo pacman -S python graphviz pkgconf python-pip`

2. **Clone the repo:** `git clone git@github.com:alexandru-balan/regex_to_dfa.git`

3. **After the repo was cloned:**
   - Navigate to repo directory: `cd regex_to_dfa`
   - Install dependencies: `pip install -r requirements.txt`
  
## 2. Runing the program

In order to run the program you need to provide a regular expression (correct regular expression) in the `input.txt` file

**The alphabet recognised by the program is:**
- letters [a-zA-Z]
- '$' -- this is used to symbolise lambda
- paranthesis: '()'
- '*' -- the Kleene star
- '|' -- the 'OR' symbol

After writing your regular expresion you can run `python Converter.py`. This will output some info about the original regular expression, the tokens found etc. It will also output to terminal things like the the FirstPos, LastPos and FollowPos collections before converting the regex.

There are also two *pictures* that the program produces, *ast.png* and *dfa.png*. One of the Abstract Syntax Tree (AST) of the regex and another one of the resulting DFA.
