import random
import climage
import pyperclip
from termcolor import colored
from googlesearch import search
from anton import PRESET_PROMPTS
from os import system, listdir, popen
from utils import show_banner, remove_code_markers, add_code_markers, highlight_code
from termcolor import colored

PICS_DIR = "/home/batch/self_internet/enjoyment/pics/"
current_file = -1
commands = {}

def command_exit(command, anton):
  exit()

def command_get_image(command, anton):
  files = listdir(PICS_DIR)
  random.shuffle(files)
  print(climage.convert(PICS_DIR + files[0], is_unicode=True))

def command_create_image(command, anton):
  prompt = input("image to create: ")
  amount = int(input("# of images: "))
  if amount < 1 or amount > 10:
    print(colored("Invalid amount!", "red", attrs=["bold"]))
    return
  print(anton.create_image(prompt, amount))

def command_search(command, anton):
  query = input("What do you want to search for? ")
  results = []
  for result in search(query, num_results=5):
    results.append(result)
    print(colored(result, "green", attrs=["bold"]))
  anton.past_code_snippets.append("```text\n" + "\n".join(results) + "```")

def command_last(command, anton):
  print(anton.last_response)

def command_past_messages(command, anton):
  print(anton.past_messages)

def command_context(command, anton):
  anton.get_current_context()

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

def command_set_focus(command, anton):
  try:
    print(colored(" | ".join(PRESET_PROMPTS.keys()), "green", attrs=["bold"]))
    focus = input("Enter focus mode: ")
    anton.set_focus_mode(focus)
  except ValueError:
    print(colored("Invalid focus mode!", "red", attrs=["bold"]))

def command_clear(command, anton):
  show_banner()
  anton.reset_context_window()

def command_copy_code(command, anton):
  anton.get_past_code_snippets()
  try:
    snippet_index = int(input("snippet to copy: "))
    pyperclip.copy(remove_code_markers(anton.past_code_snippets[snippet_index]))
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
        anton.past_code_snippets.append(add_code_markers(languages[file_extension], file_contents))
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
  print_file_contents(file_contents, -1, -1)
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
  anton.past_code_snippets.append(add_code_markers(language, file_contents))

def command_save_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to save: ")
  snippet_name = input("filename (w/ extension): ")
  try:
    with open(snippet_name, "w") as f:
      f.write(remove_code_markers(anton.past_code_snippets[int(snippet_index)]))
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
      f.write(remove_code_markers(anton.past_code_snippets[int(snippet_index)]))
  system("nano temp_snippet.txt")
  with open("temp_snippet.txt", "r") as f:
      edited_snippet = f.read()
  language = anton.past_code_snippets[int(snippet_index)].split("\n", 1)[0].strip("`")
  anton.past_code_snippets[int(snippet_index)] = add_code_markers(language, edited_snippet)
  system("rm -rf temp_snippet.txt")

def command_run_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to run: ")
  language = anton.past_code_snippets[int(snippet_index)].split("\n", 1)[0].strip("`")
  if language == "python":
    with open("temp_snippet.py", "w") as f:
      f.write(remove_code_markers(anton.past_code_snippets[int(snippet_index)]))
    system("python3 temp_snippet.py && rm -rf temp_snippet.py")
  elif language == "bash":
    with open("temp_snippet.sh", "w") as f:
      f.write(remove_code_markers(anton.past_code_snippets[int(snippet_index)]))
    system("bash temp_snippet.sh && rm -rf temp_snippet.sh")
  else:
    print(colored(f"Language {language} not supported for running code snippets!", "red", attrs=["bold"]))

def command_update_code_lang(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to update: ")
  new_language = input("new language: ")
  new_snippet = anton.past_code_snippets[int(snippet_index)]
  new_snippet = f"```{new_language}\n" + "\n".join(new_snippet.split("\n")[1:])
  anton.past_code_snippets[int(snippet_index)] = new_snippet

def command_code(command, anton):
  anton.get_past_code_snippets()

def command_system(command, anton):
  command = command.replace("$ ", "")
  output = popen(command).read()
  anton.past_code_snippets.append("```text\n" + output + "```")
  print(output)

def command_help(command, anton):
  print("List of commands:")
  for cmd_name in commands.keys():
    print(f"{colored(('> ' + cmd_name), 'cyan', attrs=['bold'])}: ", end="")
    print(commands[cmd_name][1])

commands = {
  "exit": (command_exit, "Exits the program."),
  "get-image": (command_get_image, "Displays a random image from the pics directory."),
  "create-image": (command_create_image, "Creates an image based on the given prompt."),
  "last": (command_last, "Prints the last response from Anton."),
  "past": (command_past_messages, "Prints the past messages to and from Anton."),
  "search": (command_search, "Search google and add the results to code snippets."),
  "set-focus": (command_set_focus, "Sets the focus mode for Anton."),
  "context": (command_context, "Prints the current context messages anton is using."),
  "set-max-response": (command_set_max_response_tokens, "Sets the maximum number of tokens in an Anton response."),
  "set-temperature": (command_set_temperature, "Sets the temperature for generating Anton's responses."),
  "clear": (command_clear, "Clears the terminal window and resets the context window."),
  "copy-code": (command_copy_code, "Copies a code snippet from the list of past code snippets to the clipboard."),
  "load-code": (command_load_code, "Loads a code snippet from a file and adds it to the list of past code snippets."),
  "load-dircode": (command_load_directory_code, "Loads a list of code snippets from all code files in a directory."),
  "save-code": (command_save_code, "Saves a code snippet from the list of past code snippets to a file."),
  "remove-code": (command_remove_code, "Removes a code snippet from the list of past code snippets."),
  "edit-code": (command_edit_code, "Edits a code snippet from the list of past code snippets."),
  "run-code": (command_run_code, "Runs a specific code snippet from the list of past code snippets."),
  "update-code-lang": (command_update_code_lang, "Edits a code snippets language."),
  "code": (command_code, "Prints the list of past code snippets."),
  "system": (command_system, "Executes a system command."),
  "help": (command_help, "Prints a list of available commands and their descriptions.")
}

# Executes a command based on the user input.
def execute_command(command, anton):
  if command.split(" ")[0] in commands:
    cmd, _desc = commands[command.split(" ")[0]]
    cmd(command, anton)
  else:
    print(colored(f"Command {command} not recognized!", "red", attrs=["bold"]))
