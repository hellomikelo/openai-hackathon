# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import openai
import os
import requests
from pyflowchart import *

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

openai.api_key = "..."

# print(openai.File.list())


def upload_file(filename):
    openai.File.create(file=open(filename), purpose='answers')


def list():
    print(openai.Engine.list())


def call_whisper_api(file_path):
    file_name = os.path.basename(file_path)
    url = "https://whisper.lablab.ai/asr"
    payload = {}
    files = [
      ('audio_file', (file_name, open(file_path, 'rb'), 'audio/mpeg'))
    ]
    print(f"Requesting transcription...")
    response = requests.request("POST", url, data=payload, files=files)
    # TODO: can also read segments
    transcript = response.json()['text']
    return transcript

# "/Users/yuanhunglo/Documents/Zoom/2022-12-05 13.10.02 Yuan Hung Lo's Zoom Meeting/video3155517005.mp4"
#

def make_pyfc():
    # create a simple flowchart

    # Create the start point
    start = StartNode('st')

    # Create the first process
    get_input = OperationNode("Get Input")

    # Create the decision
    dec = ConditionNode("Input Valid?")

    # Create the processes
    process1 = OperationNode("Process 1")
    process2 = OperationNode("Process 2")

    # Create the output
    output = InputOutputNode(InputOutputNode.OUTPUT, 'something...')

    # Create the end point
    end = EndNode('end')

    # Connect the components
    start.connect(get_input)
    get_input.connect(dec)
    dec.connect(process1, 'Yes')
    dec.connect(process2, 'No')
    process1.connect(output)
    process2.connect(output)
    output.connect(end)

    # Render the chart
    # Create the chart
    fc = Flowchart(start)
    print(fc.flowchart())



def answers():
    # Configs
    config = 1

    if config == 1:  # Financial reports
        file = "file-uJbOqtrsK1tub4DQREplrcEY"
        context_1 = "Number of AI journal publications grew by 34.5% from 2019 to 2020"
        context_2 = "Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving."
        context_3 = ""

        example_1 = ["Growth of published AI journals 2018 to 2020?",
                     "19.6% 2018 - 2019 and increased to 34.5% from 2019 to 2020"]
        example_2 = [
            "ai?", "Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed mimic their actions"]

        example_3 = ["",
                     ""]

        context = context_1 + " " + context_2 + " " + context_3
        examples = [example_1, example_2]

        print(context)
        print(examples)

    printer = openai.Answer.create(
        search_model="babbage",
        model="davinci",
        temperature=0.1,
        max_rerank=200,
        n=1,
        return_metadata=True,
        return_prompt=True,
        question="what part of the world is falling behind in AI?",
        file=file,
        examples_context=context,
        examples=examples,
        max_tokens=1500,
        stop=["\n", "<|endoftext|>"],
    )
    print(printer)


# Normal GPT-3
def gpt3():
    # start_sequence = "\nA:"
    # restart_sequence = "\n\nQ: "

    response = openai.Completion.create(
        engine="davinci",
        prompt="I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\".\n\nQ: What is human life expectancy in the United States?\nA: Human life expectancy in the United States is 78 years.\n\nQ: Who was president of the United States in 1955?\nA:",
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]

    )
    print(response)


# Create app UI

# Open and preprocess meeting recordings

# Transcribe

# Summarize

# Create flowchart

# Generate image?

# Display result



# gpt3()

# Run answers
# answers()

# List files
# print(openai.File.list())

# List engines
# list()


# upload_file('aiv7.jsonl')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # transcript = call_whisper_api("/Users/yuanhunglo/Documents/Zoom/2022-12-05 13.10.02 Yuan Hung Lo's Zoom Meeting/video3155517005.mp4")
    # print(transcript)
    make_pyfc()
    print("done")
    # print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
