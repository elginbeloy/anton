from os import listdir, popen, system

import pyperclip
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from termcolor import colored

from utils import (CodeSnippet, DataSnippet, 
  add_code_markers, highlight_code,
  remove_code_markers, show_banner)

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

# Load data from a file
def command_load_data(command, anton):
    file_name = input("file path (relative or absolute): ")
    data_type = input("data type: ")
    
    try:
        with open(file_name, "r") as f:
            file_contents = f.read()
    except FileNotFoundError:
        print("File not found. Please check the file path and try again.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return
    
    anton.past_data_snippets.append(DataSnippet(data_type, file_name, file_contents))

# Split a code snippet into a sub-snippet using line numbers
def command_split_data(command, anton):
  def print_selected_file_contents(file_contents, start=-1, end=-1):
    for line_num, line in enumerate(file_contents.splitlines()):
      if line == None: 
        break
      color = "red" if start <= line_num < end else "white"
      print(colored(f"{str(line_num).rjust(3)}  ", color, attrs=["bold"]), end="")
      print(line, end="")
    print()
  
  anton.get_past_data_snippets()
  snippet_index = input("snippet to split: ")
  while not snippet_index.isdigit() or not (0 <= int(snippet_index) < len(anton.past_data_snippets)):
    print(colored(text="Invalid snippet index!", color="red", attrs=["bold"]))
    snippet_index = input("snippet to split: ")
  
  snippet = anton.past_data_snippets[int(snippet_index)]
  print(print_selected_file_contents(snippet.content))

  lines = input(f"lines to include [0:{len(snippet.content.splitlines())}]: ")
  while not lines or (":" not in lines or not lines.replace(":", "").isdigit()):
    print(colored(text="Invalid line values!", color="red", attrs=["bold"]))
    lines = input(f"lines to include [0:{len(snippet.content.splitlines())}]: ")

  start, end = map(int, lines.split(":"))
  print(print_selected_file_contents(snippet.content, start, end))

  confirm = input("Are you sure? (y/n): ")
  while confirm.lower() not in ['y', 'n']:
    print(colored(text="Invalid input! Please enter 'y' or 'n'.", color="red", attrs=["bold"]))
    confirm = input("Are you sure? (y/n): ")

  if confirm.lower() == "y":
    split_content = "\n".join(snippet.content.splitlines()[start:end])
    anton.past_data_snippets.append(DataSnippet(snippet.data_type, snippet.name + "_split", split_content))
    print(colored(text="Data split successfully!", color="green", attrs=["bold"]))
  else:
    print(colored(text="Data not split.", color="red", attrs=["bold"]))

def command_load_directory_data(command, anton):
  dir_to_search = input("directory to load: ")
  extension_to_load = input("extension to load (dont include period)")
  try:
    files = [f for f in listdir(dir_to_search) if f.endswith(extension_to_load)]
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
      anton.past_data_snippets.append(DataSnippet(extension_to_load, file_name, file_contents))
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
  search_results_snippet = DataSnippet(data_type="text", name="search_results", content="\n".join(results))
  anton.past_data_snippets.append(search_results_snippet)

def command_download_text_from_url(command, anton):
  anton.get_past_data_snippets()
  snippet_index = input("snippet url list to download from: ")
  try:
    print(anton.past_data_snippets[int(snippet_index)])
    urls = anton.past_data_snippets[int(snippet_index)].content.split("\n")
    for url in urls:
      page = requests.get(url)
      soup = BeautifulSoup(page.content, 'html.parser')
      text = soup.get_text()
      clean_text = "\n".join([l.strip() for l in text.split("\n") if len(l.strip()) > 8])
      download_results_snippet = DataSnippet(data_type="text", name=f"url_{url}", content=clean_text)
      anton.past_data_snippets.append(download_results_snippet)
      print(colored(f"Downloaded {len(clean_text)} chars from {url} successfully!", "green", attrs=["bold"]))
  except Exception as e:
    print(colored(f"An error occurred while downloading text: {e}", "red", attrs=["bold"]))
