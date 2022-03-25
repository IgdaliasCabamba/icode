import re
import keyword
import textwrap
import sys

#EXCEPTIONS = """BaseException||FileNotFoundError""" # add more exceptions

SINGLETONS = frozenset(['False', 'None', 'True'])
KEYWORDS = frozenset(keyword.kwlist + ['print', 'async']) - SINGLETONS
WHITESPACE = frozenset(' \t')

DEBUG_STATUS_REGEX = re.compile("([_a-z-A-Z-0-9]*.py)\\(([0-9]*)\\)<([_a-z-A-Z-0-9]*)>")
DEBUG_RETURN_REGEX = re.compile("(->) (.*)")
DEBUG_CONTEXT_REGEX = re.compile("(Pdb)")
DEBUG_EXCEPTION_REGEX = re.compile("(FileNotFoundError)(:)(.*)")

INDENT_REGEX = re.compile(r'([ \t]*)')
EXTRANEOUS_WHITESPACE_REGEX = re.compile(r'[\[({] | [\]}),;]| :(?!=)')
WHITESPACE_AFTER_COMMA_REGEX = re.compile(r'[,;:]\s*(?:  |\t)')
KEYWORD_REGEX = re.compile(r'(\s*)\b(?:%s)\b(\s*)' % r'|'.join(KEYWORDS))
MATCH_CASE_REGEX = re.compile(r'^\s*\b(?:match|case)(\s*)(?=.*\:)')
OPERATOR_REGEX = re.compile(r'(?:[^,\s])(\s*)(?:[-+*/|!<=>%&^]+)(\s*)')
LAMBDA_REGEX = re.compile(r'\blambda\b')
STARTSWITH_DEF_REGEX = re.compile(r'^(async\s+def|def)\b')
STARTSWITH_TOP_LEVEL_REGEX = re.compile(r'^(async\s+def\s+|def\s+|class\s+|@)')
STARTSWITH_INDENT_STATEMENT_REGEX = re.compile(
    r'^\s*({0})\b'.format('|'.join(s.replace(' ', r'\s+') for s in (
        'def', 'async def',
        'for', 'async for',
        'if', 'elif', 'else',
        'try', 'except', 'finally',
        'with', 'async with',
        'class',
        'while',
    )))
)
COMPARE_NEGATIVE_REGEX = re.compile(r'\b(?<!is\s)(not)\s+[^][)(}{ ]+\s+'
                                    r'(in|is)\s')
RAISE_COMMA_REGEX = re.compile(r'raise\s+\w+\s*,')
RERAISE_COMMA_REGEX = re.compile(r'raise\s+\w+\s*,.*,\s*\w+\s*$')

isidentifier = str.isidentifier

def tabs_or_spaces(physical_line, indent_char) -> None:
    indent = INDENT_REGEX.match(physical_line).group(1)
    for offset, char in enumerate(indent):
        if char != indent_char:
            return offset, "E101 indentation contains mixed spaces and tabs"

def tabs_obsolete(physical_line) -> None:
    indent = INDENT_REGEX.match(physical_line).group(1)
    if '\t' in indent:
        return indent.index('\t'), "W191 indentation contains tabs"

def trailing_whitespace(physical_line) -> None:
    physical_line = physical_line.rstrip('\n')
    physical_line = physical_line.rstrip('\r')
    physical_line = physical_line.rstrip('\x0c')
    stripped = physical_line.rstrip(' \t\v')
    if physical_line != stripped:
        if stripped:
            return len(stripped), "W291 trailing whitespace"
        else:
            return 0, "W293 blank line contains whitespace"

def trailing_blank_lines(physical_line, lines, line_number, total_lines) -> None:
    if line_number == total_lines:
        stripped_last_line = physical_line.rstrip('\r\n')
        if physical_line and not stripped_last_line:
            return 0, "W391 blank line at end of file"
        if stripped_last_line == physical_line:
            return len(lines[-1]), "W292 no newline at end of file"

def maximum_line_length(physical_line, max_line_length, multiline, line_number, noqa) -> None:

    line = physical_line.rstrip()
    length = len(line)
    if length > max_line_length and not noqa:
        # Special case: ignore long shebang lines.
        if line_number == 1 and line.startswith('#!'):
            return
        # Special case for long URLs in multi-line docstrings or
        # comments, but still report the error when the 72 first chars
        # are whitespaces.
        chunks = line.split()
        if ((len(chunks) == 1 and multiline) or
            (len(chunks) == 2 and chunks[0] == '#')) and \
                len(line) - len(chunks[-1]) < max_line_length - 7:
            return
        if hasattr(line, 'decode'):   # Python 2
            # The line could contain multi-byte characters
            try:
                length = len(line.decode('utf-8'))
            except UnicodeError:
                pass
        if length > max_line_length:
            return (max_line_length, "E501 line too long "
                    "(%d > %d characters)" % (length, max_line_length))

def extraneous_whitespace(logical_line) -> None:
    line = logical_line
    for match in EXTRANEOUS_WHITESPACE_REGEX.finditer(line):
        text = match.group()
        char = text.strip()
        found = match.start()
        if text == char + ' ':
            yield found + 1, "E201 whitespace after '%s'" % char
        elif line[found - 1] != ',':
            code = ('E202' if char in '}])' else 'E203')
            yield found, "%s whitespace before '%s'" % (code, char)

def whitespace_around_keywords(logical_line) -> None:
    for match in KEYWORD_REGEX.finditer(logical_line):
        before, after = match.groups()

        if '\t' in before:
            yield match.start(1), "E274 tab before keyword"
        elif len(before) > 1:
            yield match.start(1), "E272 multiple spaces before keyword"

        if '\t' in after:
            yield match.start(2), "E273 tab after keyword"
        elif len(after) > 1:
            yield match.start(2), "E271 multiple spaces after keyword"

    if sys.version_info >= (3, 10):
        match = MATCH_CASE_REGEX.match(logical_line)
        if match:
            if match[1] == ' ':
                return
            if match[1] == '':
                yield match.start(1), "E275 missing whitespace after keyword"
            else:
                yield match.start(1), "E271 multiple spaces after keyword"

def missing_whitespace_after_import_keyword(logical_line) -> None:
    line = logical_line
    indicator = ' import('
    if line.startswith('from '):
        found = line.find(indicator)
        if -1 < found:
            pos = found + len(indicator) - 1
            yield pos, "E275 missing whitespace after keyword"

def missing_whitespace(logical_line) -> None:
    line = logical_line
    for index in range(len(line) - 1):
        char = line[index]
        next_char = line[index + 1]
        if char in ',;:' and next_char not in WHITESPACE:
            before = line[:index]
            if char == ':' and before.count('[') > before.count(']') and \
                    before.rfind('{') < before.rfind('['):
                continue  # Slice syntax, no space required
            if char == ',' and next_char == ')':
                continue  # Allow tuple with only one element: (3,)
            if char == ':' and next_char == '=' and sys.version_info >= (3, 8):
                continue  # Allow assignment expression
            yield index, "E231 missing whitespace after '%s'" % char

def whitespace_around_operator(logical_line) -> None:
    for match in OPERATOR_REGEX.finditer(logical_line):
        before, after = match.groups()

        if '\t' in before:
            yield match.start(1), "E223 tab before operator"
        elif len(before) > 1:
            yield match.start(1), "E221 multiple spaces before operator"

        if '\t' in after:
            yield match.start(2), "E224 tab after operator"
        elif len(after) > 1:
            yield match.start(2), "E222 multiple spaces after operator"

def whitespace_around_comma(logical_line) -> None:
    line = logical_line
    for m in WHITESPACE_AFTER_COMMA_REGEX.finditer(line):
        found = m.start() + 1
        if '\t' in m.group():
            yield found, "E242 tab after '%s'" % m.group()[0]
        else:
            yield found, "E241 multiple spaces after '%s'" % m.group()[0]

def imports_on_separate_lines(logical_line) -> None:
    line = logical_line
    if line.startswith('import '):
        found = line.find(',')
        if -1 < found and ';' not in line[:found]:
            yield found, "E401 multiple imports on one line"

def compound_statements(logical_line) -> None:
    line = logical_line
    last_char = len(line) - 1
    found = line.find(':')
    prev_found = 0
    counts = {char: 0 for char in '{}[]()'}
    while -1 < found < last_char:
        if ((counts['{'] <= counts['}'] and   # {'a': 1} (dict)
             counts['['] <= counts[']'] and   # [1:2] (slice)
             counts['('] <= counts[')']) and  # (annotation)
            not (sys.version_info >= (3, 8) and
                 line[found + 1] == '=')):  # assignment expression
            lambda_kw = LAMBDA_REGEX.search(line, 0, found)
            if lambda_kw:
                before = line[:lambda_kw.start()].rstrip()
                if before[-1:] == '=' and isidentifier(before[:-1].strip()):
                    yield 0, ("E731 do not assign a lambda expression, use a "
                              "def")
                break
            if STARTSWITH_DEF_REGEX.match(line):
                yield 0, "E704 multiple statements on one line (def)"
            elif STARTSWITH_INDENT_STATEMENT_REGEX.match(line):
                yield found, "E701 multiple statements on one line (colon)"
        prev_found = found
        found = line.find(':', found + 1)
    found = line.find(';')
    while -1 < found:
        if found < last_char:
            yield found, "E702 multiple statements on one line (semicolon)"
        else:
            yield found, "E703 statement ends with a semicolon"
        found = line.find(';', found + 1)

def comparison_negative(logical_line) -> None:
    match = COMPARE_NEGATIVE_REGEX.search(logical_line)
    if match:
        pos = match.start(1)
        if match.group(2) == 'in':
            yield pos, "E713 test for membership should be 'not in'"
        else:
            yield pos, "E714 test for object identity should be 'is not'"

def python_3000_raise_comma(logical_line) -> None:
    match = RAISE_COMMA_REGEX.match(logical_line)
    if match and not RERAISE_COMMA_REGEX.match(logical_line):
        yield match.end() - 1, "W602 deprecated form of raising exception"

def python_3000_not_equal(logical_line) -> None:
    pos = logical_line.find('<>')
    if pos > -1:
        yield pos, "W603 '<>' is deprecated, use '!='"

def python_3000_backticks(logical_line) -> None:
    pos = logical_line.find('`')
    if pos > -1:
        yield pos, "W604 backticks are deprecated, use 'repr()'"


builtin_functions={
    "abs":"(x)",
    "all":"(iterable)",
    "any":"(iterable)",
    "ascii":"(object)",
    "bin":"(x)",
    "breakpoint":"(*args, **kws)",
    "callable":"(object)",
    "chr":"(i)",
    "compile":"(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)",
    "delattr":"(object, name)",
    "dir":"([object])",
    "divmod":"(a, b)",
    "enumerate":"(iterable, start=0)",
    "eval":"(expression[, globals[, locals]])",
    "exec":"(object[, globals[, locals]])",
    "filter":"(function, iterable)",
    "format":"(value[, format_spec])",
    "getattr":"(object, name[, default])",
    "hasattr":"(object, name)",
    "hash":"(object)",
    "help":"([object])",
    "hex":"(x)",
    "id":"(object)",
    "input":"([prompt])",
    "isinstance":"(object, classinfo)",
    "issubclass":"(class, classinfo)",
    "iter":"(object[, sentinel])",
    "len":"(s)",
    "map":"(function, iterable, ...)",
    "max":"(iterable, *[, key, default])||(arg1, arg2, *args[, key])",
    "min":"(iterable, *[, key, default])||(arg1, arg2, *args[, key])",
    "next":"(iterator[, default])",
    "oct":"(x)",
    "open":"(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)",
    "ord":"(c)",
    "pow":"(base, exp[, mod])",
    "print":r"(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)",
    "repr":"(object)",
    "reversed":"(seq)",
    "round":"(number[, ndigits])",
    "setattr":"(object, name, value)",
    "sorted":"(iterable, *, key=None, reverse=False)",
    "sum":"(iterable, /, start=0)",
    "super":"([type[, object-or-type]])",
    "vars":"([object])",
    "zip":"(*iterables)"
}
primitive_types = {
    "int":"int(x, base=10)",
    "str":"str(object=b'', encoding='utf-8', errors='strict')",
    "float":"float([x])",
    "bool":"bool([x])"
}
builtin_classes = {
    "tuple":"tuple([iterable])",
    "list":"list([iterable])",
    "set":"set([iterable])",
    "dict":"dict(mapping, **kwarg)",
}
python_key_list=['and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'super', 'try', 'while', 'with', 'yield']
python_extra_key_list=['False','True', 'None', 'self', 'int', 'str', 'object', 'list', 'set', 'dict', 'tuple', 'float', 'bool', 'byte']