# anton

anton is a CLI chatbot assistant that uses an LLM, code snippets, and its own
REPL + reference syntax.

## Installation

1. Clone the repository: `git clone https://github.com/elginbeloy/anton.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file in the root directory of the project and add your OpenAI API key: `OPEN_API_KEY=your_api_key_here`

## Usage

To start the chatbot, run the following command:

```
python main.py
```

You will see a prompt that looks like this:

```
[you] 
```

Enter your message and AntonAI will respond with a generated message.

You can also use `> ` to execute commands. Try `> help` for a list.

Set focus (preset prompts) using `> focus`.

See Antons current context window with `> context`. 

Anton contains a code snippet system, view it with `> code` and use 
in prompts via `::code[n]::` where this string is replaced with the n'th
previous code snippet.

## Screenshots

![Alt text](./screenshot_1.png?raw=true "Screenshot of AntonCLI")
![Alt text](./screenshot_2.png?raw=true "Screenshot of AntonCLI adding code to himself.")

## Todos

[ ] Code snippets as a class instead of just strings
[ ] Data snippets as a class instead of code snippets
-> [ ] Data snippets using their own commands and ::data[n]::
[ ] Locally stored .history file for storing permanant history
[ ] Context window editing
[ ] Session / context window storage of some sort ??? 