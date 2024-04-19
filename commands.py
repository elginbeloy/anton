import random
from os import listdir, popen, system

import pyperclip
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from termcolor import colored

from anton import PRESET_PROMPTS
from code_commands import *
from data_commands import *
from utils import (CodeSnippet, DataSnippet, 
  add_code_markers, highlight_code,
  remove_code_markers, show_banner)

commands = {}

# General CLI commands
# =====================================
def command_exit(command, anton):
  exit()

def command_help(command, anton):
  print("List of commands:")
  for cmd_name in commands.keys():
    print(f"{colored(('> ' + cmd_name), 'cyan', attrs=['bold'])}: ", end="")
    print(commands[cmd_name][1])

def command_clear(command, anton):
  show_banner()

# Anton LLM Commands
# =====================================
def command_get_stats(command, anton):
  anton.get_stats()

def command_last_message(command, anton):
  print(anton.last_response)

def command_past_messages(command, anton):
  print(anton.past_messages)

def command_get_context(command, anton):
  anton.get_current_context()

def command_clear_context(command, anton):
  anton.reset_context_window()

def command_set_focus(command, anton):
  try:
    print(colored(" | ".join(PRESET_PROMPTS.keys()), "green", attrs=["bold"]))
    focus = input("Enter focus mode: ")
    anton.set_focus_mode(focus)
  except ValueError:
    print(colored("Invalid focus mode!", "red", attrs=["bold"]))

def command_set_max_response_tokens(command, anton):
  try:
    max_response_tokens = int(input("max response tokens (/2048): "))
    anton.set_max_response_tokens(max_response_tokens)
  except ValueError:
    print(colored("Invalid token amount!", "red", attrs=["bold"]))

def command_set_temperature(command, anton):
  try:
    temperature = float(input("temperature (0-1.8): "))
    anton.set_temperature(temperature)
  except ValueError:
    print(colored("Invalid temperature amount!", "red", attrs=["bold"]))

def command_model(command, anton):
  print(colored(text=anton.model, color="green", attrs=["bold"]))

def command_set_model(command, anton):
  try:
    print(colored(" | ".join(anton.get_available_models()), "green", attrs=["bold"]))
    model = input("Enter model: ")
    anton.set_model(model)
  except ValueError:
    print(colored("Invalid model!", "red", attrs=["bold"]))

# Misc (idk how to categorize these) Commands
# =====================================
def command_create_image(command, anton):
  prompt = input("image to create: ")
  anton.create_image(prompt)

def command_system(command, anton):
  command = input(colored("$ ", "green", attrs=["bold"]))
  output = popen(command).read()
  code_snippet = DataSnippet(data_type="text", name="system_output", content=output)
  anton.past_data_snippets.append(code_snippet)
  print(output)

commands = {
  "exit": (command_exit, "Exits the program."),
  "help": (command_help, "Prints a list of available commands and their descriptions."),
  "clear": (command_clear, "Clears the terminal window and prints the intro banner."),

  # Anton LLM related commands
  "stats": (command_get_stats, "Displays Anton's current settings and context."),
  "last": (command_last_message, "Prints the last response from Anton."),
  "past": (command_past_messages, "Prints the past messages to and from Anton."),
  "set-focus": (command_set_focus, "Sets the focus mode for Anton."),
  #"create-focus": (command_create_focus, "Create a new focus mode for Anton using the current context window for preset prompts."),
  "context": (command_get_context, "Prints the current context messages anton is using."),
  "clear-context": (command_clear_context, "Resets the current context window."),
  #"create-context-window": (command_clear, "Resets the current context window."),
  #"list-context-windows": (command_clear, "Resets the current context window."),
  #"edit-context-window": (command_clear, "Resets the current context window."),
  #"edit-context-window-name": (command_clear, "Resets the current context window."),
  #"remove-context-window": (command_clear, "Resets the current context window."),
  "set-max-response": (command_set_max_response_tokens, "Sets the maximum number of tokens in an Anton response."),
  "set-temperature": (command_set_temperature, "Sets the temperature for generating Anton's responses."),
  "model": (command_model, "Prints the current model being used for generating Anton's responses."),
  "set-model": (command_set_model, "Sets the model to be used for generating Anton's responses."),

  # Data related commands
  "data": (command_list_data, "Prints the list of past data snippets."),
  "copy-data": (command_copy_data, "Copies a data snippet from the list of past data snippets to the clipboard."),
  "load-data": (command_load_data, "Loads a data snippet from a file and adds it to the list of past code snippets."),
  "load-dirdata": (command_load_directory_data, "Loads a list of code snippets from all data files in a directory."),
  "save-data": (command_save_data, "Saves a code snippet from the list of past data snippets to a file."),
  "remove-data": (command_remove_data, "Removes a code snippet from the list of past data snippets."),
  "edit-data": (command_edit_data, "Edits a code snippet from the list of past data snippets."),
  "split-data": (command_split_data, "Splits a data snippet into a subset snippet using start:end line numbers."),
  "update-data-name": (command_update_data_name, "Edits a data snippets name."),
  "update-data-type": (command_update_data_type, "Edits a data snippets language."),
  "search": (command_search, "Search google and add the results to dawta snippets."),
  "download-text-from-url": (command_download_text_from_url, "Downloads all the textual data from a list of urls in a previous code snippet."),

  # Code related commands
  "code": (command_list_code, "Prints the list of past code snippets."),
  "copy-code": (command_copy_code, "Copies a code snippet from the list of past code snippets to the clipboard."),
  "load-code": (command_load_code, "Loads a code snippet from a file and adds it to the list of past code snippets."),
  "load-dircode": (command_load_directory_code, "Loads a list of code snippets from all code files in a directory."),
  "save-code": (command_save_code, "Saves a code snippet from the list of past code snippets to a file."),
  "remove-code": (command_remove_code, "Removes a code snippet from the list of past code snippets."),
  "edit-code": (command_edit_code, "Edits a code snippet from the list of past code snippets."),
  "split-code": (command_split_code, "Shortens a code snippet by splitting it using start:end line numbers."),
  "run-code": (command_run_code, "Runs a specific code snippet from the list of past code snippets."),
  "update-code-name": (command_update_code_name, "Edits a code snippets name."),
  "update-code-lang": (command_update_code_language, "Edits a code snippets language."),

  # Other MISC commands
  "create-image": (command_create_image, "Creates an image based on the given prompt."),
  "system": (command_system, "Executes a system command."),
}

# Executes a command based on the user input.
def execute_command(command, anton):
  if command.split(" ")[0] in commands:
    cmd, _desc = commands[command.split(" ")[0]]
    cmd(command, anton)
  else:
    print(colored(f"Command {command} not recognized!", "red", attrs=["bold"]))
