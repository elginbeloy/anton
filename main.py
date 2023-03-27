import re
import readline
import os
from termcolor import colored
from anton import AntonAI
from commands import execute_command
from utils import show_banner, highlight_code, get_code_language

_, columns = os.popen('stty size', 'r').read().split()
columns = int(columns)

anton = AntonAI(temperature=0.4)

ANTON_STR = "[" + colored("anton", "cyan", attrs=["bold", "reverse"]) + "]"
YOU_STR = "[" + colored("elgin", "green", attrs=["bold", "reverse"]) + "]"

def get_response(prompt):
  response = anton.get_response(prompt)
  usage = response.usage
  stats = f"[i: {usage.prompt_tokens} | o: {usage.completion_tokens} | t: {usage.total_tokens}/2048]"
  print((max(0, columns - len(stats)) * " ") + colored(stats, "white", attrs=["bold", "reverse"]))
  response = response.choices[0].message.content
  response = re.sub(r"(?<!`)`([^`]+)`(?!`)", colored(r'\g<0>', "cyan", attrs=["bold"]), response)
  response = re.sub(r"```.*?```", lambda match: highlight_code(match.group(0), get_code_language(match.group(0))), response, flags=re.DOTALL)
  return response

show_banner()
while True:
  user_input = input(f"{YOU_STR} ")
  if user_input.startswith("> "):
    command = user_input.replace("> ", "")
    execute_command(command, anton)
  else:
    response = get_response(user_input)
    print(f"{ANTON_STR} {response}")
  print()
