import random
from os import listdir, popen, system

import pyperclip
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from termcolor import colored

from anton import PRESET_PROMPTS
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

# DataSnippet Related Commands
# =====================================
def command_list_data(command, anton):
  anton.get_past_data_snippets()

def command_copy_data(command, anton):
  anton.get_past_data_snippets()
  try:
    snippet_index = int(input("snippet to copy: "))
    pyperclip.copy(anton.past_data_snippets[snippet_index].content)
    print(colored("Data snippet copied to clipboard!", "green", attrs=["bold"]))
  except ValueError:
    print(colored("Invalid snippet index!", "red", attrs=["bold"]))

def command_load_data(command, anton):
  def print_file_contents(file_contents, start=0, end=None):
    if end is None:
      end = len(file_contents)
    for line_num, line in enumerate(file_contents):
      color = "red" if start <= line_num < end else "white"
      print(colored(f"{str(line_num).rjust(3)}  ", color, attrs=["bold"]) + line, end="")

  file_name = input("file path (relative or absolute): ")
  data_type = input("data type: ")
  try:
    with open(file_name, "r") as f:
      file_contents = f.readlines()
  except FileNotFoundError:
    print("File not found. Please check the file path and try again.")
    return
  except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    return
  print_file_contents(file_contents)
  print()
  lines = input(f"lines to include [0:{len(file_contents)}, default all]: ")
  if lines:
    try:
      start, end = map(int, lines.split(":"))
      while True:
        print_file_contents(file_contents, start, end)
        confirm = input("Are you sure? (y/n): ")
        if confirm.lower() == "y":
          break
        else:
          lines = input(f"lines to include [0:{len(file_contents)}, default all]: ")
          if not lines:
            start, end = 0, len(file_contents)
            break
          start, end = map(int, lines.split(":"))
    except ValueError:
      print("Invalid input. Please enter the lines to include in the format 'start:end'.")
      return
    except Exception as e:
      print(f"An error occurred while processing your input: {e}")
      return
  else:
    start, end = 0, len(file_contents)
  file_contents = "".join(file_contents[start:end])
  anton.past_data_snippets.append(DataSnippet(data_type, file_name, file_contents))

def command_load_directory_data(command, anton):
  dir_to_search = input("directory to load: ")
  try:
    files = listdir(dir_to_search)
  except FileNotFoundError:
    print(colored(f"Directory {dir_to_search} not found!", "red", attrs=["bold"]))
    return
  except Exception as e:
    print(colored(f"An error occurred while reading the directory {dir_to_search}: {e}", "red", attrs=["bold"]))
    return
  for file_name in files:
    try:
      with open(dir_to_search + file_name, "r") as f:
        file_contents = f.read()
      data_type = input(f"Enter data type for file {file_name}: ")
      anton.past_data_snippets.append(DataSnippet(data_type, file_name, file_contents))
      print(colored(f"Loaded {file_name} successfully!", "green", attrs=["bold"]))
    except FileNotFoundError:
      print(colored(f"File {file_name} not found!", "red", attrs=["bold"]))
    except Exception as e:
      print(colored(f"An error occurred while reading the file {file_name}: {e}", "red", attrs=["bold"]))

def command_save_data(command, anton):
  anton.get_past_data_snippets()
  snippet_index = input("snippet to save: ")
  snippet_name = input("filename (w/ extension): ")
  try:
    with open(snippet_name, "w") as f:
      f.write(anton.past_data_snippets[int(snippet_index)].content)
  except Exception as e:
    print(colored(f"An error occurred while saving the file: {e}", "red", attrs=["bold"]))

def command_remove_data(command, anton):
  anton.get_past_data_snippets()
  snippet_index = input("snippet to remove: ")
  anton.past_data_snippets.pop(int(snippet_index))

def command_edit_data(command, anton):
  anton.get_past_data_snippets()
  snippet_index = input("snippet to edit: ")
  with open("temp_snippet.txt", "w") as f:
      f.write(anton.past_data_snippets[int(snippet_index)].content)
  system("nano temp_snippet.txt")
  with open("temp_snippet.txt", "r") as f:
      updated_snippet_content = f.read()
  anton.past_data_snippets[int(snippet_index)].content = updated_snippet_content
  system("rm -rf temp_snippet.txt")

def command_update_data_name(command, anton):
  anton.get_past_data_snippets()
  try:
    snippet_index = int(input("snippet to update name: "))
    new_name = input("new name: ")
    anton.past_data_snippets[snippet_index].name = new_name
    print(colored(f"Data snippet name updated successfully!", "green", attrs=["bold"]))
  except ValueError:
    print(colored("Invalid snippet index!", "red", attrs=["bold"]))
  except IndexError:
    print(colored("Snippet index out of range!", "red", attrs=["bold"]))

def command_update_data_type(command, anton):
  anton.get_past_data_snippets()
  try:
    snippet_index = int(input("snippet to update data type: "))
    new_data_type = input("new data type: ")
    anton.past_data_snippets[snippet_index].data_type = new_data_type
    print(colored(f"Data snippet data type updated successfully!", "green", attrs=["bold"]))
  except ValueError:
    print(colored("Invalid snippet index!", "red", attrs=["bold"]))
  except IndexError:
    print(colored("Snippet index out of range!", "red", attrs=["bold"]))

def command_search(command, anton):
  query = input("What do you want to search for? ")
  results = []
  for result in search(query, num_results=5):
    results.append(result)
    print(colored(result, "green", attrs=["bold"]))
  search_results_snippet = CodeSnippet(language="text", name="search_results", content="\n".join(results))
  anton.past_code_snippets.append(search_results_snippet)

def command_download_text_from_url(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet url list to download from: ")
  try:
    print(anton.past_code_snippets[int(snippet_index)])
    urls = remove_code_markers(anton.past_code_snippets[int(snippet_index)]).split("\n")
    for url in urls:
      page = requests.get(url)
      soup = BeautifulSoup(page.content, 'html.parser')
      text = soup.get_text()
      clean_text = "\n".join([l.strip() for l in text.split("\n") if len(l.strip()) > 8])
      download_results_snippet = CodeSnippet(language="text", name=f"url_{url}", content=clean_text)
      anton.past_code_snippets.append(download_results_snippet)
      print(colored(f"Downloaded {len(clean_text)} chars from {url} successfully!", "green", attrs=["bold"]))
  except Exception as e:
    print(colored(f"An error occurred while downloading text: {e}", "red", attrs=["bold"]))

# CodeSnippet Related Commands
# =====================================
def command_copy_code(command, anton):
  anton.get_past_code_snippets()
  try:
    snippet_index = int(input("snippet to copy: "))
    pyperclip.copy(anton.past_code_snippets[snippet_index].content)
    print(colored("Code snippet copied to clipboard!", "green", attrs=["bold"]))
  except ValueError:
    print(colored("Invalid snippet index!", "red", attrs=["bold"]))

def command_load_directory_code(command, anton):
  languages = {"py": "python", "rs": "rust", "cpp": "c++", "java": "java", "html": "html", "js": "javascript"}
  dir_to_search = input("directory to load: ")
  try:
    files = listdir(dir_to_search)
  except FileNotFoundError:
    print(colored(f"Directory {dir_to_search} not found!", "red", attrs=["bold"]))
    return
  except Exception as e:
    print(colored(f"An error occurred while reading the directory {dir_to_search}: {e}", "red", attrs=["bold"]))
    return
  for file_name in files:
    file_extension = file_name.split(".")[-1]
    if file_extension in languages.keys():
      try:
        with open(dir_to_search + file_name, "r") as f:
          file_contents = f.read()
        anton.past_code_snippets.append(CodeSnippet(languages[file_extension], file_name, file_contents))
        print(colored(f"Loaded {file_name} successfully!", "green", attrs=["bold"]))
      except FileNotFoundError:
        print(colored(f"File {file_name} not found!", "red", attrs=["bold"]))
      except Exception as e:
        print(colored(f"An error occurred while reading the file {file_name}: {e}", "red", attrs=["bold"]))

def command_load_code(command, anton):
  def print_file_contents(file_contents, start=0, end=None):
    if end is None:
      end = len(file_contents)
    for line_num, line in enumerate(file_contents):
      color = "red" if start <= line_num < end else "white"
      highlighted_line = highlight_code(line, language)
      print(colored(f"{str(line_num).rjust(3)}  ", color, attrs=["bold"]) + highlighted_line, end="")

  file_name = input("file path (relative or absolute): ")
  language = input("language: ")
  try:
    with open(file_name, "r") as f:
      file_contents = f.readlines()
  except FileNotFoundError:
    print("File not found. Please check the file path and try again.")
    return
  except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    return
  print_file_contents(file_contents)
  print()
  lines = input(f"lines to include [0:{len(file_contents)}, default all]: ")
  if lines:
    try:
      start, end = map(int, lines.split(":"))
      while True:
        print_file_contents(file_contents, start, end)
        confirm = input("Are you sure? (y/n): ")
        if confirm.lower() == "y":
          break
        else:
          lines = input(f"lines to include [0:{len(file_contents)}, default all]: ")
          if not lines:
            start, end = 0, len(file_contents)
            break
          start, end = map(int, lines.split(":"))
    except ValueError:
      print("Invalid input. Please enter the lines to include in the format 'start:end'.")
      return
    except Exception as e:
      print(f"An error occurred while processing your input: {e}")
      return
  else:
    start, end = 0, len(file_contents)
  file_contents = "".join(file_contents[start:end])
  anton.past_code_snippets.append(CodeSnippet(language, file_name, file_contents))

def command_save_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to save: ")
  snippet_name = input("filename (w/ extension): ")
  try:
    with open(snippet_name, "w") as f:
      f.write(anton.past_code_snippets[int(snippet_index)].content)
  except Exception as e:
    print(colored(f"An error occurred while saving the file: {e}", "red", attrs=["bold"]))

def command_remove_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to remove: ")
  anton.past_code_snippets.pop(int(snippet_index))

def command_edit_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to edit: ")
  with open("temp_snippet.txt", "w") as f:
      f.write(anton.past_code_snippets[int(snippet_index)].content)
  system("nano temp_snippet.txt")
  with open("temp_snippet.txt", "r") as f:
      updated_snippet_content = f.read()
  anton.past_code_snippets[int(snippet_index)].content = updated_snippet_content
  system("rm -rf temp_snippet.txt")

def command_run_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to run: ")
  snippet = anton.past_code_snippets[int(snippet_index)]
  language = snippet.language
  content = snippet.content
  if language == "python":
    with open("temp_snippet.py", "w") as f:
      f.write(content)
    system("python3 temp_snippet.py && rm -rf temp_snippet.py")
  elif language == "bash":
    with open("temp_snippet.sh", "w") as f:
      f.write(content)
    system("bash temp_snippet.sh && rm -rf temp_snippet.sh")
  else:
    print(colored(f"Language {language} not supported for running code snippets!", "red", attrs=["bold"]))

def command_update_code_lang(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to update: ")
  new_language = input("new language: ")
  new_snippet = anton.past_code_snippets[int(snippet_index)]
  new_snippet.language = new_language

def command_update_code_name(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to update: ")
  new_name = input("new name: ")
  new_snippet = anton.past_code_snippets[int(snippet_index)]
  new_snippet.name = new_name

def command_list_code(command, anton):
  anton.get_past_code_snippets()

# Misc (idk how to categorize these) Commands
# =====================================
def command_create_image(command, anton):
  prompt = input("image to create: ")
  amount = int(input("# of images: "))
  if amount < 1 or amount > 10:
    print(colored("Invalid amount!", "red", attrs=["bold"]))
    return
  print(anton.create_image(prompt, amount))

def command_system(command, anton):
  command = input(colored("$ ", "green", attrs=["bold"]))
  output = popen(command).read()
  code_snippet = DataSnippet(data_type="text", name="system_output", content=output)
  anton.past_data_snippets.append(code_snippet)
  print(output)

commands = {
  "exit": (command_exit, "Exits the program."),
  "help": (command_help, "Prints a list of available commands and their descriptions."),
  "clear": (command_clear, "Clears the terminal window and resets the context window."),

  # Anton LLM related commands
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

  # Data related commands
  "data": (command_list_data, "Prints the list of past data snippets."),
  "copy-data": (command_copy_data, "Copies a data snippet from the list of past code snippets to the clipboard."),
  "load-data": (command_load_data, "Loads a data snippet from a file and adds it to the list of past code snippets."),
  "load-dirdata": (command_load_directory_data, "Loads a list of code snippets from all code files in a directory."),
  "save-data": (command_save_data, "Saves a code snippet from the list of past code snippets to a file."),
  "remove-data": (command_remove_data, "Removes a code snippet from the list of past code snippets."),
  "edit-data": (command_edit_data, "Edits a code snippet from the list of past code snippets."),
  "update-data-name": (command_update_data_name, "Edits a code snippets name."),
  "update-data-type": (command_update_data_type, "Edits a code snippets language."),
  "search": (command_search, "Search google and add the results to code snippets."),
  "download-text-from-url": (command_download_text_from_url, "Downloads all the textual data from a list of urls in a previous code snippet."),

  # Code related commands
  "code": (command_list_code, "Prints the list of past code snippets."),
  "copy-code": (command_copy_code, "Copies a code snippet from the list of past code snippets to the clipboard."),
  "load-code": (command_load_code, "Loads a code snippet from a file and adds it to the list of past code snippets."),
  "load-dircode": (command_load_directory_code, "Loads a list of code snippets from all code files in a directory."),
  "save-code": (command_save_code, "Saves a code snippet from the list of past code snippets to a file."),
  "remove-code": (command_remove_code, "Removes a code snippet from the list of past code snippets."),
  "edit-code": (command_edit_code, "Edits a code snippet from the list of past code snippets."),
  "run-code": (command_run_code, "Runs a specific code snippet from the list of past code snippets."),
  "update-code-name": (command_update_code_name, "Edits a code snippets name."),
  "update-code-lang": (command_update_code_lang, "Edits a code snippets language."),

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
