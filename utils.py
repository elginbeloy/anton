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
'''

def show_banner():
  os.system("clear")
  print(colored(BANNER, "cyan", attrs=["bold"]))
  print()
  print()


def highlight_code(code, language):
  if language == "python":
    lexer = get_lexer_by_name("python")
    formatter = Terminal256Formatter(style="monokai")
    highlighted_code = highlight(code, lexer, formatter)
    highlighted_code = highlighted_code.replace("True", colored("True", "magenta"))
    highlighted_code = highlighted_code.replace("False", colored("False", "red"))
    highlighted_code = highlighted_code.replace("None", colored("None", "yellow"))
    highlighted_code = highlighted_code.replace("(", colored("(", "yellow"))
    highlighted_code = highlighted_code.replace(")", colored(")", "yellow"))
    highlighted_code = highlighted_code.replace("{", colored("{", "yellow"))
    highlighted_code = highlighted_code.replace("}", colored("}", "yellow"))
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

class DataSnippet:
  def __init__(self, data_type, name, content):
    self.data_type = data_type
    self.name = name
    self.content = content

class CodeSnippet:
  def __init__(self, language, name, content):
    self.language = language
    self.name = name
    self.content = content

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
  if lines[0].startswith("```") and snippet.endswith("```"):
    return "\n".join(lines[1:]).replace("```", "")
  

def add_code_markers(language, snippet):
  return f"```{language}\n{snippet}\n```"
