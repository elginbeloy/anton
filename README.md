# anton

anton is a powerful CLI chatbot assistant that utilizes an LLM, code + data snippets, its own REPL and reference syntax, preset prompts, and context window editing to assist users in their various workflows. 

Anton contains a code and data snippet system that can be viewed with `> code` and `> data`. These code snippets can be used in prompts via `::code[n]::` and `::data[n]``, where the string is replaced with the n'th snippet. The same can be done with past messages via the string `::message[0]::`.

Some example use cases include
- use natural language to create, edit, summarize, or review code
- speed up your dev workflows with boilerplate code creation, and content text/image generation
- **WARNING**: start exploring baby agi by hooking up your own LLM, and having anton develop himself and execute commands locally using `> meta`

## Installation

To install Anton, follow these three steps:

1. Clone the repository: `git clone https://github.com/elginbeloy/anton.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file in the root directory of the project and add your OpenAI API key: `OPEN_API_KEY=your_api_key_here`

## Get Started

To start using Anton, simply run the following command:

```
python main.py
```


You will see a prompt that looks like this:

```
[you] 
```


Enter your message and AntonAI will respond with a generated message.

You can also use `> ` to execute commands. Try `> help` for a full command list.

Set focus (preset prompts context window) using `> focus`.

See Anton's current context window with `> context`. 

## Screenshots

Check out these screenshots of Anton in action:

![Alt text](./screenshot_1.png?raw=true "Screenshot of AntonCLI")
![Alt text](./screenshot_2.png?raw=true "Screenshot of AntonCLI adding code to himself.")
