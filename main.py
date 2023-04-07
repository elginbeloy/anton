import re
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style, style_from_pygments_cls
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexer import RegexLexer
from pygments.style import Style as PygmentsStyle
from pygments.token import Token
from termcolor import colored
from anton import AntonAI
from commands import execute_command, commands
from utils import show_banner, highlight_code, get_code_language

class CustomLexer(RegexLexer):
  tokens = {
    "root": [
      (r'::code\[\d\]::', Token.CodeElement),
      (r'::data\[\d\]::', Token.CodeElement),
      (r'::message\[\d\]::', Token.CodeElement),
      (r'[^:]+', Token.Text),
      (r':', Token.Text),
    ],
  }

class CustomStyle(PygmentsStyle):
  default_style = ""
  styles = {
    Token.CodeElement: '#00FF00',
  }

class CommandCompleter(Completer):
  def __init__(self, commands):
    self.commands = commands

  def get_completions(self, document, complete_event):
    if document.text.replace(" ", "").startswith(">"):
      command = document.text.replace(" ", "").replace(">", "")
      for cmd_name in self.commands.keys():
        if cmd_name.startswith(command):
          yield Completion(cmd_name, start_position=-len(command))

session = PromptSession(completer=CommandCompleter(commands))

_, columns = os.popen('stty size', 'r').read().split()
columns = int(columns)

anton = AntonAI(temperature=0.4)

ANTON_STR = "[" + colored("anton", "cyan", attrs=["bold", "reverse"]) + "]"
YOU_STR = "[" + colored("you", "green", attrs=["bold", "reverse"]) + "]"

def get_response(prompt):
  response = anton.get_response(prompt)
  usage = response.usage
  stats = f"[i: {usage.prompt_tokens}/3584 | o: {usage.completion_tokens}/512 | t: {usage.total_tokens}/4096]"
  print((max(0, columns - len(stats)) * " ") + colored(stats, "white", attrs=["bold", "reverse"]))
  response = response.choices[0].message.content
  response = re.sub(r"(?<!`)`([^`]+)`(?!`)", colored(r'\g<0>', "cyan", attrs=["bold"]), response)
  response = re.sub(r"```.*?```", lambda match: highlight_code(match.group(0), get_code_language(match.group(0))), response, flags=re.DOTALL)
  return response

show_banner()
style = style_from_pygments_cls(CustomStyle)
while True:
  user_input = session.prompt(ANSI(f"{YOU_STR} "), lexer=PygmentsLexer(CustomLexer), style=style)
  if not user_input:
    continue
  if user_input.replace(" ", "").startswith(">"):
    command = user_input.replace(" ", "").replace(">", "")
    execute_command(command, anton)
  else:
    response = get_response(user_input)
    print(f"{ANTON_STR} {response}")
  print()
