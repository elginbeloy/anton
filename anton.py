import openai
import re
from termcolor import colored
from utils import highlight_code
from os import getenv
from dotenv import load_dotenv
load_dotenv()

openai.api_key = getenv("OPEN_API_KEY")

PRESET_PROMPTS = {
  "default": [
      {"role": "system", "content": "You are Anton, the assistant of Elgin."},
      {"role": "system", "content": "Refer to yourself in the third person when talking.'"},
  ],
  "motivate": [
      {"role": "system", "content": "Be brutal, he must study more, harder. The world depends on it."},
  ],
  "inspire": [
      {"role": "system", "content": "Be brutal, he must study more, harder. The world depends on it."},
  ],
}

def replace_code(text, code_snippets):
  def replace_code_match(match):
    index = int(match.group(1))
    if index < len(code_snippets):
      return code_snippets[index]
    else:
      return match.group(0)  # If index is out of range, don't replace the match

  return re.sub(r'::code\[(\d+)\]::', replace_code_match, text)

# Focus: motivate | inspire | support | palaround | inform | assist
# Action: reassure(::patpat::) | calm(::chill::)
class AntonAI:
  def __init__(self, temperature=0.8, model="gpt-3.5-turbo", max_response_tokens=1024, ):
    self.temperature = temperature
    self.model = model
    self.max_response_tokens = max_response_tokens
    self.past_messages = PRESET_PROMPTS['default'][:]
    self.past_code_snippets = []
    self.current_context_messages = PRESET_PROMPTS['default'][:]
    self.current_focus = "motivate"
    self.last_response = {}

  def get_response(self, prompt):
    prompt = replace_code(prompt, self.past_code_snippets)
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
    self.past_code_snippets.extend(re.findall(r'```.*?```', response_content, flags=re.DOTALL))
    # for smaller snippets
    # self.past_code_snippets.extend(re.findall(r"(?<!`)`([^`]+)`(?!`)", response_content))
    self.past_messages.append({"role": "assistant", "content": response_content})
    self.current_context_messages.append({"role": "assistant", "content": response_content})
    return response

  def get_past_code_snippets(self):
    for index, snippet in enumerate(self.past_code_snippets):
      language = snippet.split("\n")[0].replace("```", "") or "python"
      snippet_lines = snippet.replace("`", "").split("\n")[:-1]
      print(f"[{index}] {colored(snippet_lines[0], 'yellow')}")
      for line_num, line in enumerate(snippet_lines[1:]):
        highlighted_line = highlight_code(line, language)
        print(colored(f"{str(line_num + 1).rjust(3)}  ", "white", attrs=["bold"]) + highlighted_line, end="")
      print()

  def reset_context_window(self):
    self.current_context_messages = PRESET_PROMPTS['default'][:]
