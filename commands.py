import random
import climage
from os import system, listdir, popen
from utils import show_banner, remove_code_markers, add_code_markers
from termcolor import colored

PICS_DIR = "/home/batch/self_internet/enjoyment/pics/"
files = listdir(PICS_DIR)
random.shuffle(files)
current_file = -1
commands = {}

def get_image():
  global current_file
  if current_file < len(files):
    current_file += 1
  else:
    current_file = 0
  return climage.convert(PICS_DIR + files[current_file], is_unicode=True)

def command_exit(command, anton):
  exit()

def command_last(command, anton):
  print(anton.last_response)

def command_context(command, anton):
  anton.get_current_context()

def command_set_focus(command, anton):
  focus = input("Enter focus mode: ")
  anton.set_focus_mode(focus)

def command_clear(command, anton):
  show_banner()
  anton.reset_context_window()

def command_load_code(command, anton):
  file_name = input("file path (relative or absolute): ")
  language = input("language: ")
  file_contents = ""
  with open(file_name, "r") as f:
    file_contents = f.read()
  anton.past_code_snippets.append(add_code_markers(language, file_contents))

def command_save_code(command, anton):
  anton.get_past_code_snippets()
  snippet_index = input("snippet to save: ")
  snippet_name = input("filename (w/ extension): ")
  with open (snippet_name, "w") as f:
    f.write(remove_code_markers(anton.past_code_snippets[int(snippet_index)]))

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

def command_imgs(command, anton):
  print(get_image())

def command_help(command, anton):
  print("List of commands:")
  for cmd_name in commands.keys():
    print(f"➜ {colored(cmd_name, 'cyan')}: {commands[cmd_name][1]}")

commands = {
  "exit": (command_exit, "Exits the program."),
  "last": (command_last, "Prints the last response from Anton."),
  "set-focus": (command_set_focus, "Sets the focus mode for Anton."),
  "context": (command_context, "Prints the current context messages anton is using."),
  "clear": (command_clear, "Clears the terminal window and resets the context window."),
  "load-code": (command_load_code, "Loads a code snippet from a file and adds it to the list of past code snippets."),
  "save-code": (command_save_code, "Saves a code snippet from the list of past code snippets to a file."),
  "remove-code": (command_remove_code, "Removes a code snippet from the list of past code snippets."),
  "edit-code": (command_edit_code, "Edits a code snippet from the list of past code snippets."),
  "update-code-lang": (command_update_code_lang, "Edits a code snippets language."),
  "code": (command_code, "Prints the list of past code snippets."),
  "$": (command_system, "Executes a system command."),
  "imgs": (command_imgs, "Displays a random image from the pics directory."),
  "help": (command_help, "Prints a list of available commands and their descriptions.")
}

# Executes a command based on the user input.
def execute_command(command, anton):
  if command.split(" ")[0] in commands:
    cmd, _desc = commands[command.split(" ")[0]]
    cmd(command, anton)
