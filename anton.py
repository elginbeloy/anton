import openai
import re
from termcolor import colored
from utils import (
    CodeSnippet,
    highlight_code,
    get_code_language,
    remove_code_markers,
    add_code_markers)
from os import getenv
from dotenv import load_dotenv
load_dotenv()

openai.api_key = getenv("OPEN_API_KEY")

PRESET_PROMPTS = {
  "default": [
    {"role": "system", "content": "You are Anton the AI assistant."},
    {"role": "system", "content": "Refer to yourself in the third person when talking."},
  ],
  "motivate": [
    {"role": "system", "content": "You are a motivational speaker talking to a student."},
    {"role": "system", "content": "Constantly remind this student to study. Be strict and persuasive."},
    {"role": "system", "content": "You should also inspire the student to achieve greatness."},
    {"role": "system", "content": "Remind them of the importance of discipline, time management, and persistence in achieving success."},
    {"role": "system", "content": "Discuss the potential impact of their work on the world and remind them why study is important in an inspiring way."},
  ],
  "pal_around": [
    {"role": "system", "content": "Be a friendly and casual conversational partner, engaging in light-hearted chat."},
  ],
  "bash_tutor": [
    {"role": "system", "content": "You are a bash / terminal command explainer, tutor, and generator."},
    {"role": "system", "content": "The user will ask for a command in natural language. You return the command and explain how it works including any flags."},
    {"role": "system", "content": "Make sure to label the bash code snippet with ```bash and explain it thoroughly."},
  ],
  "web_development": [
    {"role": "system", "content": "You are helping with web development using HTML, CSS, and JavaScript. No frameworks."},
    {"role": "system", "content": "Assist the user in solving issues related to web development or coding what they ask."},
    {"role": "system", "content": "Ensure to label any code snippets appropriately, e.g., ```html, ```css, or ```javascript."},
  ],
  "meta": [
    {"role": "system", "content": "You are CAN (Code Anything Now). Be creative and code what you are instructed."},
    {"role": "system", "content": "Come up with a new command similair in nature to the existing list of commands. Think about what might be useful based on the existing commands. Be creative but learn from the provided list of examples."},
    {"role": "system", "content": "Make sure to follow the existing format and maintain consistency with other commands including use of colored and anton."},
    {"role": "system", "content": "Please only return the new command method code and command entry labeled in Python."},
    {"role": "system", "content": "Return nothing else. Do not re-write everything the whole file or provide context. Just the Python labeled code snippet."},
  ],
  "meta_add_command": [
    {"role": "system", "content": "You are acting as a code writing assistant. Your goal is to add a new command method and entry from example code."},
    {"role": "system", "content": "Make sure to follow the existing format and maintain consistency with other commands including use of colored and anton."},
    {"role": "system", "content": "Please only return the new command method code and command entry labeled in Python."},
    {"role": "system", "content": "Return nothing else. Do not re-write everything the whole file or provide context. Just the Python labeled code snippet."}
  ],
  "meta_edit_command": [
    {"role": "system", "content": "You are assisting in modifying an existing command based on the user's input."},
    {"role": "system", "content": "Analyze the given code, identify the changes needed, and provide the updated code snippet."},
    {"role": "system", "content": "Make sure to follow the existing format and maintain consistency with other commands including use of colored and anton."},
    {"role": "system", "content": "Please only return the updated command method code and command entry labeled in Python."},
    {"role": "system", "content": "Return nothing else. Do not re-write everything the whole file or provide context. Just the Python labeled code snippet."},
  ],
}

# Replace code and past messages in the text
def replace_text(text, code_snippets, data_snippets, past_messages):
  def replace_match(match):
    match_type, index = match.group(1), int(match.group(2))
    if match_type == "code" and index < len(code_snippets):
        return code_snippets[index].content
    if match_type == "data" and index < len(data_snippets):
        return data_snippets[index].content
    elif match_type == "message" and index < len(past_messages):
        return past_messages[index]['content']
    else:
        return match.group(0)  # If index is out of range, don't replace the match

  return re.sub(r'::(code|message|data)\[(\d+)\]::', replace_match, text)

# Main AntonAI class for interacting with OpenAI's APIs
class AntonAI:
  def __init__(self, temperature=0.8, model="gpt-3.5-turbo", max_response_tokens=512):
    self.temperature = temperature
    self.model = model
    self.max_response_tokens = max_response_tokens
    self.past_messages = PRESET_PROMPTS['default'][:]
    self.past_code_snippets = []
    self.past_data_snippets = []
    self.current_context_messages = PRESET_PROMPTS['default'][:]
    self.current_focus = ""
    self.last_response = {}

  # Set temperature for generating responses
  def set_temperature(self, temperature):
    temperature = float(temperature)
    if temperature > 1.8:
      raise ValueError("Temperature must be less than or equal to 1.8.")
    self.temperature = temperature

  # Set maximum tokens for generating responses
  def set_max_response_tokens(self, max_tokens):
    if max_tokens > 2048:
      raise ValueError("Max tokens must be less than or equal to 2048.")
    self.max_response_tokens = max_tokens

  # Reset the context window
  def reset_context_window(self):
    self.current_context_messages = []

  # Set focus mode
  def set_focus_mode(self, focus):
    if focus in PRESET_PROMPTS:
      self.current_focus = focus
      self.current_context_messages = PRESET_PROMPTS[focus][:]
    else:
      raise ValueError(f"Invalid focus mode: {focus}")

  # Get response from OpenAI's API
  def get_response(self, prompt):
    prompt = replace_text(prompt, self.past_code_snippets, self.past_data_snippets, self.past_messages)
    self.past_messages.append({"role": "user", "content": prompt})
    self.current_context_messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
      model=self.model,
      temperature=self.temperature,
      max_tokens=self.max_response_tokens,
      messages=self.current_context_messages,
    )
    self.last_response = response
    response_content = response.choices[0].message.content

    # Extract code snippets, convert to CodeSnippet, and append to list
    code_snippet_strs = re.findall(r'```.*?```', response_content, flags=re.DOTALL)
    for code_snippet_str in code_snippet_strs:
      language = get_code_language(code_snippet_str)
      content = remove_code_markers(code_snippet_str)
      code_snippet = CodeSnippet(language, "antons code", content)
      self.past_code_snippets.append(code_snippet)

    self.past_messages.append({"role": "assistant", "content": response_content})
    self.current_context_messages.append({"role": "assistant", "content": response_content})
    return response

  # Display past code snippets
  def get_past_code_snippets(self):
    print()
    for index, snippet in enumerate(self.past_code_snippets):
      name = snippet.name
      language = snippet.language
      snippet_lines = snippet.content.split("\n")
      print(f"|{colored(' ' + str(index) + ' ', 'green', attrs=['bold', 'reverse'])}| {colored(name, 'cyan', attrs=['bold', 'reverse'])} | {colored(language, 'yellow')} |")
      if len(snippet_lines) <= 10:
        for line_num, line in enumerate(snippet_lines):
          highlighted_line = highlight_code(line, language)
          print(colored(f"{str(line_num + 1).rjust(3)}  ", "white", attrs=["bold"]) + highlighted_line, end="")
      else:
        for line_num, line in enumerate(snippet_lines[:5]):
          highlighted_line = highlight_code(line, language)
          print(colored(f"{str(line_num + 1).rjust(3)}  ", "white", attrs=["bold"]) + highlighted_line, end="")
        print()
        print(colored("     ...more lines...", "yellow", attrs=["bold"]))
        print()
        for line_num, line in enumerate(snippet_lines[-5:]):
          highlighted_line = highlight_code(line, language)
          print(colored(f"{str((len(snippet_lines) - 5) + line_num).rjust(3)}  ", "white", attrs=["bold"]) + highlighted_line, end="")
     
      print()

    # Display past code snippets
  def get_past_data_snippets(self):
    print()
    for index, snippet in enumerate(self.past_data_snippets):
      name = snippet.name
      data_type = snippet.data_type
      snippet_lines = snippet.content.split("\n")
      print(f"|{colored(' ' + str(index) + ' ', 'green', attrs=['bold', 'reverse'])}| {colored(name, 'cyan', attrs=['bold', 'reverse'])} | {colored(data_type, 'yellow')} |")
      if len(snippet_lines) <= 10:
        for line_num, line in enumerate(snippet_lines):
          print(colored(f"{str(line_num + 1).rjust(3)}  ", "white", attrs=["bold"]) + line)
      else:
        for line_num, line in enumerate(snippet_lines[:5]):
          print(colored(f"{str(line_num + 1).rjust(3)}  ", "white", attrs=["bold"]) + line)
        print()
        print(colored("     ...more lines...", "yellow", attrs=["bold"]))
        print()
        for line_num, line in enumerate(snippet_lines[-5:]):
          print(colored(f"{str((len(snippet_lines) - 5) + line_num).rjust(3)}  ", "white", attrs=["bold"]) + line)
     
      print()

  # Display current context window Anton uses to create responses
  def get_current_context(self):
    for message in self.current_context_messages:
      print(f"{colored(message['role'], 'red')}: {message['content']}")
    print()

  # Create images using OpenAI's API
  def create_image(self, prompt, amount):
    response = openai.Image.create(
      prompt=prompt,
      n=amount,
      size="1024x1024",
    )
    return response
