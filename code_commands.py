# CodeSnippet Related Commands
# =====================================

import pyperclip
from anton import *
from os import listdir, popen, system
from termcolor import colored
from utils import (CodeSnippet, DataSnippet, 
  add_code_markers, highlight_code,
  remove_code_markers, show_banner)

# List all code snippets
def command_list_code(command, anton):
  anton.get_past_code_snippets()

# Copy code snippet to clipboard
def command_copy_code(command, anton):
  anton.get_past_code_snippets()
  try:
    snippet_index = int(input("snippet to copy: "))
    pyperclip.copy(anton.past_code_snippets[snippet_index].content)
    print(colored("Code snippet copied to clipboard!", "green", attrs=["bold"]))
  except ValueError:
    print(colored("Invalid snippet index!", "red", attrs=["bold"]))

# Load code from a file
def command_load_code(command, anton):
  languages = {"py": "python", "rs": "rust", "cpp": "c++", "java": "java", "html": "html", "js": "javascript"}
  file_name = input("file path (relative or absolute): ")
  
  file_extension = file_name.split(".")[-1]
  if file_extension in languages.keys():
    language = languages[file_extension]
  else:
    language = input("language: ")

  try:
    with open(file_name, "r") as f:
      file_contents = f.read()
  except FileNotFoundError:
    print(colored("File not found. Please check the file path and try again.", "red", attrs=["bold"]))
    return
  except Exception as e:
    print(colored(f"An error occurred while reading the file: {e}", "red", attrs=["bold"]))
    return
  anton.past_code_snippets.append(CodeSnippet(language, file_name, file_contents))

# Load all code files in a directory
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

# Split a code snippet into a sub-snippet using line numbers
def command_split_code(command, anton):
  def print_selected_file_contents(file_contents, language, start=-1, end=-1):
    for line_num, line in enumerate(file_contents.splitlines()):
      if line == None: 
        break
      color = "red" if start <= line_num < end else "white"
      highlighted_line = highlight_code(line, language)
      print(colored(f"{str(line_num).rjust(3)}  ", color, attrs=["bold"]), end="")
      print(highlighted_line, end="")
    print()

  anton.get_past_code_snippets()
  snippet_index = input("snippet to split: ")
  while not snippet_index.isdigit() or not (0 <= int(snippet_index) < len(anton.past_code_snippets)):
    print(colored(text="Invalid snippet index!", color="red", attrs=["bold"]))
    snippet_index = input("snippet to split: ")

  snippet = anton.past_code_snippets[int(snippet_index)]
  print(print_selected_file_contents(snippet.content, snippet.language))

  lines = input(f"lines to include [0:{len(snippet.content.splitlines())}]: ")
  while not lines or (":" not in lines or not lines.replace(":", "").isdigit()):
    print(colored(text="Invalid line values!", color="red", attrs=["bold"]))
    lines = input(f"lines to include [0:{len(snippet.content.splitlines())}]: ")

  start, end = map(int, lines.split(":"))
  print(print_selected_file_contents(snippet.content, snippet.language, start, end))

  confirm = input("Are you sure? (y/n): ")
  while confirm.lower() not in ['y', 'n']:
    print(colored(text="Invalid input! Please enter 'y' or 'n'.", color="red", attrs=["bold"]))
    confirm = input("Are you sure? (y/n): ")

  if confirm.lower() == "y":
    split_content = "\n".join(snippet.content.splitlines()[start:end])
    anton.past_code_snippets.append(CodeSnippet(snippet.language, snippet.name + "_split", split_content))
    print(colored(text="Snippet split successfully!", color="green", attrs=["bold"]))
  else:
    print(colored(text="Snippet not split.", color="red", attrs=["bold"]))

# Save code snippet to a file
def command_save_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to save: ")
  snippet_name = input("filename (w/ extension): ")
  try:
    with open(snippet_name, "w") as f:
      f.write(anton.past_code_snippets[int(snippet_index)].content)
  except Exception as e:
    print(colored(f"An error occurred while saving the file: {e}", "red", attrs=["bold"]))

# Remove a code snippet from the list
def command_remove_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to remove: ")
  anton.past_code_snippets.pop(int(snippet_index))

# Edit a code snippet
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

# Run a code snippet using a temporarily created file
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

# Update a code snippet's name
def command_update_code_name(command, anton):
  anton.get_past_code_snippets()
  try:
    snippet_index = int(input("snippet to update: "))
    new_name = input("new name: ")
    anton.past_code_snippets[snippet_index].name = new_name
    print(colored("Snippet name updated successfully!", "green", attrs=["bold"]))
  except ValueError:
    print(colored("Invalid snippet index!", "red", attrs=["bold"]))
  except IndexError:
    print(colored("Snippet index out of range!", "red", attrs=["bold"]))
  except Exception as e:
    print(colored(f"An error occurred while updating the snippet name: {e}", "red", attrs=["bold"]))

# Update a code snippet's language
def command_update_code_language(command, anton):
  anton.get_past_code_snippets()
  try:
    snippet_index = int(input("snippet to update: "))
    new_language = input("new language: ")
    anton.past_code_snippets[snippet_index].language = new_language
    print(colored("Snippet name updated successfully!", "green", attrs=["bold"]))
  except ValueError:
    print(colored("Invalid snippet index!", "red", attrs=["bold"]))
  except IndexError:
    print(colored("Snippet index out of range!", "red", attrs=["bold"]))
  except Exception as e:
    print(colored(f"An error occurred while updating the snippet name: {e}", "red", attrs=["bold"]))