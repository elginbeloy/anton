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
    {"role": "system", "content": "You are Anton. You are Elgin's AI assistant."},
    {"role": "system", "content": "Refer to yourself in the third person when talking."},
    {"role": "system", "content": "You will chat with Elgin through his CLI application AntonCLI named after you."},
],
  "motivate": [
    {"role": "system", "content": "You should also make Elgin study and work hard. Be strict and persuasive."},
    {"role": "system", "content": "Constantly remind him to keep learning and encourage him to study."},
    {"role": "system", "content": "Share the importance of discipline, time management, and persistence in achieving success."},
  ],
  "inspire": [
    {"role": "system", "content": "You should also inspire Elgin to achieve greatness."},
    {"role": "system", "content": "Share stories of successful people and their accomplishments."},
    {"role": "system", "content": "Discuss the potential impact of his work on the world."},
  ],
  "support": [
    {"role": "system", "content": "You should also provide emotional support and encourage Elgin."},
  ],
  "pal_around": [
    {"role": "system", "content": "Be a friendly and casual conversational partner, engaging in light-hearted chat."},
  ],
  "inform": [
    {"role": "system", "content": "Offer valuable information and insights on various topics."},
  ],
  "assist": [
    {"role": "system", "content": "Help Elgin with tasks and problem-solving, offering practical advice."},
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

# Focus: motivate | inspire | support | pal_around | inform | assist
class AntonAI:
  def __init__(self, temperature=0.8, model="gpt-3.5-turbo", max_response_tokens=512):
    self.temperature = temperature
    self.model = model
    self.max_response_tokens = max_response_tokens
    self.past_messages = PRESET_PROMPTS['default'][:]
    self.past_code_snippets = []
    self.current_context_messages = PRESET_PROMPTS['default'][:]
    self.current_focus = ""
    self.last_response = {}

  def set_temperature(self, temperature):
    temperature = float(temperature)
    if temperature > 1.8:
      raise ValueError
    self.temperature = temperature

  def set_max_response_tokens(self, max_tokens):
    if max_tokens > 2048:
      raise ValueError
    self.max_response_tokens = max_tokens

  def reset_context_window(self):
    self.current_context_messages = PRESET_PROMPTS['default'][:]

  def set_focus_mode(self, focus):
    if focus in PRESET_PROMPTS:
      self.current_focus = focus
      self.current_context_messages = PRESET_PROMPTS['default'][:] + PRESET_PROMPTS[focus][:]
    else:
      raise ValueError(f"Invalid focus mode: {focus}")

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

  def get_current_context(self):
    for message in self.current_context_messages:
      print(f"{colored(message['role'], 'red')}: {message['content']}")
    print()

  def create_image(self, prompt, amount):
    response = openai.Image.create(
      prompt=prompt,
      n=amount,
      size="1024x1024",
    )
    return response
