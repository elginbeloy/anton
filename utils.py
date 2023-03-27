from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter
from termcolor import colored
import climage
import os
import re

BANNER = r'''
      ___           ___           ___           ___           ___     
     /\  \         /\__\         /\  \         /\  \         /\__\    
    /::\  \       /::|  |        \:\  \       /::\  \       /::|  |   
   /:/\:\  \     /:|:|  |         \:\  \     /:/\:\  \     /:|:|  |   
  /::\~\:\  \   /:/|:|  |__       /::\  \   /:/  \:\  \   /:/|:|  |__ 
 /:/\:\ \:\__\ /:/ |:| /\__\     /:/\:\__\ /:/__/ \:\__\ /:/ |:| /\__\
 \/__\:\/:/  / \/__|:|/:/  /    /:/  \/__/ \:\  \ /:/  / \/__|:|/:/  /
      \::/  /      |:/:/  /    /:/  /       \:\  /:/  /      |:/:/  / 
      /:/  /       |::/  /     \/__/         \:\/:/  /       |::/  /  
     /:/  /        /:/  /                     \::/  /        /:/  /   
     \/__/         \/__/                       \/__/         \/__/    
v1.1 by Elgin Beloy                                                   
'''
IMAGE_BANNER = climage.convert('./anton-image.jpg', is_unicode=True)

def show_banner():
  os.system("clear")
  print(IMAGE_BANNER)
  print(colored(BANNER, "cyan", attrs=["bold"]))
  print()
  print()


def highlight_code(code, language):
  if language == "python":
    lexer = get_lexer_by_name("python")
    formatter = Terminal256Formatter(style="monokai")
    highlighted_code = highlight(code, lexer, formatter)
    highlighted_code = highlighted_code.replace("True", colored("True", "green"))
    highlighted_code = highlighted_code.replace("False", colored("False", "red"))
    highlighted_code = highlighted_code.replace("None", colored("None", "yellow"))
    highlighted_code = highlighted_code.replace("range", colored("range", "cyan"))
    highlighted_code = highlighted_code.replace("print", colored("print", "cyan"))
    highlighted_code = highlighted_code.replace("len", colored("print", "cyan"))
    highlighted_code = highlighted_code.replace("input", colored("print", "cyan"))
    highlighted_code = highlighted_code.replace("(", colored("(", "magenta"))
    highlighted_code = highlighted_code.replace(")", colored(")", "magenta"))
  elif language == "rust":
    lexer = get_lexer_by_name("rust")
    formatter = Terminal256Formatter(style="monokai")
    highlighted_code = highlight(code, lexer, formatter)
    highlighted_code = highlighted_code.replace("&amp;", "&")
    highlighted_code = highlighted_code.replace("&#x27;", "'")
    highlighted_code = highlighted_code.replace("&gt;", ">")
    highlighted_code = highlighted_code.replace("&lt;", "<")
    highlighted_code = highlighted_code.replace("&quot;", "\"")
  else:
    lexer = get_lexer_by_name(language)
    formatter = Terminal256Formatter(style="monokai")
    highlighted_code = highlight(code, lexer, formatter)
  return highlighted_code


def get_code_language(code):
  match = re.match(r"^```(\w+)\n", code)
  if match:
    return match.group(1)
  else:
    return 'python'


def remove_code_markers(snippet):
  lines = snippet.split("\n")
  if len(lines) < 3:
    return snippet  # Invalid code snippet format
  if lines[0].startswith("```") and lines[-1] == "```":
    return "\n".join(lines[1:-1])
  

def add_code_markers(language, snippet):
  return f"```{language}\n{snippet}\n```"