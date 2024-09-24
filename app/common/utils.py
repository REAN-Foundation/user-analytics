import json
import os
import traceback
import uuid
from pygments import highlight, lexers, formatters
import random
import string

def print_colorized_json(obj):
    jsonStr = json.dumps(obj.__dict__, default=str, indent=2)
    colored = highlight(jsonStr, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colored)

def generate_uuid4():
    return str(uuid.uuid4())

def generate_random_code(length=8):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def print_exception(e):
    tb = traceback.extract_tb(e.__traceback__)
    filename = os.path.basename(tb[-1].filename)  # Get the filename without path
    function_name = tb[-1].name                   # Get the function name
    line_number = tb[-1].lineno
    text = f"Error: {e} \nFile: {filename}, Function: {function_name}, Line: {line_number}"
    colored = highlight(text, lexers.PythonLexer(), formatters.TerminalFormatter())
    print(colored)
    # print(f"Error: {e} \nFile: {filename}, Function: {function_name}, Line: {line_number}")
