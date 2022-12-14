import os

import requests
import whisper
import streamlit as st
from pydub import AudioSegment
import openai
from dotenv import load_dotenv
import graphviz

load_dotenv()

# import sys
# import subprocess
#
# # implement pip as a subprocess:
# subprocess.check_call([sys.executable, '-m', 'pip', 'install',
# '<packagename>'])

st.set_page_config(
    page_title="Whisper & GPT-3",
    page_icon="rocket",
    layout="wide",
    initial_sidebar_state="auto",
)

upload_path = "uploads/"
download_path = "downloads/"
transcript_path = "transcripts/"


@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def call_whisper_api(file_path):
    file_name = os.path.basename(file_path)
    url = "https://whisper.lablab.ai/asr"
    payload = {}
    files = [
      ('audio_file', (file_name, open(file_path, 'rb'), 'audio/mpeg'))
    ]
    print(f"Requesting transcription...")
    # response = requests.request("POST", url, data=payload, files=files)
    # transcript = response.json()['text']
    # HACK
    transcript = "Helloa, my name is Mike and for this lab lab AI and Coheir hackathon, I like to share my project called smarty. And say mindful personal assistance. So in today's attention economy, our attention is a rare commodity. We're constantly inundated by more content, more social interactions, chores and work than our minds can adequately handle. David Allen, the author of getting things done, said that if you don't pay attention, appropriate attention to what has your attention, it will take more of your attention than it deserves. This problem is especially evident in the modern knowledge workforce. And being a knowledge worker myself. I definitely share that pain. I think there are three factors that contribute to the rules of modern knowledge work. We have a lack of boundary because of easily easy accessibility by messaging tools, resulting in a lot of ad hoc requests that pile on quickly, but without effective ways to clear them. To we have an accumulation of tasks, large and small that forces us to constantly switch context, leading to burnouts and frustrations. Three, the productivity tools that we use today are still not intelligent enough to adequately fill filter our date to do list and to help protect our time. So these issues result in significant cost of context switching on any given day and knowledge workers toggle on an average 1200 times between different apps and websites. And once distracted workers need an average of 23 minutes returns the original task. This totals into roughly 9% of one's annual work time that's spent just on context switching. Yuck. So my project, smarty is an attempt to address those problems. Smarty quiets the noise around you so you could work peacefully to get things done. It's a task planner that evaluates the importance and urgency of your tasks, then prioritizes and batches them rigorously. So you can focus on accomplishing what matters the most. So here I will stop and do a quick demo. So here is the stream of that that I built smarty on top of a and the user starts by adding the tasks that they want to analyze and classify. And you can do it either via upload or copy pasting. And by default, there are two examples to get started. One is to get a doctor appointment for checkup. The other one is fly to the moon just for fun. And smarty will analyze and classify and batch these tasks into one of four buckets. Do these now schedule these reassign these to others and discard these. So as you can see here, smarty seems to think that doctor appointment is pretty important. So this is a do it now type of task. And as for fly to the moon just for fun. This is seems like a kind of a trivial task or so smarty says just discarded for now. Yeah. And so if we want to add additional tasks. It's as simple as copy a pasting new ones in here. And then you'll see that there are new analysis that are turned out. And you can see that they're batched into tasks that are more suitable to do at in the same time, just due to the nature of those tasks. So for instance here you can see that cleaning the toilet vacuuming idea of after dinner they belong to batch zero. So they should be done at around the same time. And because they involve the same activities, whereas thinking through maternity leave schedule. That's more of a sit down and think type of task. So that's batch one. So there you have it. This is a quick demo of the smarty app. And I will go back to the presentation. Great. Okay, so smarty provides value by allowing you to one focus your energy on impactful goals by setting boundaries around your time and mental space. To it reduces contact switching fatigue by understanding the relationships between tasks and bundling similar ones together to work on at once. It creates opportunities for teamwork by delegating tasks to collaborators and giving others a chance to shine. And for it identify and eliminate unnecessary busy work to free up your time for things that matter. So how does smarty work underneath the hood. So one user provides an example pairs of tasks and classes to the cohere classify API and the API learns from the examples using future learning and then clusters new tasks into one of four classes do it now delegated discarded or designated. And the output pairs of tasks and classes are fed into the cohere embed API to calculate string embeddings, which are then bundled into similar batches using k means. And then for the resulting task classes and batches are displayed via a stream but interface. So there are a lot of different exciting paths that can be pursued from here, and three major ones that I can think of our, we can add upstream and downstream integrations in a smarty to enable seamless in task and ingestion and hand off with different applications to we can also implement natural language explainability to describe why tasks are classified and batched away they are. And with that can help humans make the final decisions in terms of what they want to do. And three, finally, we can also set up quantitative and qualitative evaluation metrics to measure classifier performance and understand how well it caters to the user's needs. Okay, so this concludes my presentation on smarty. So thank you for your attention. And before I'm here and here, here's a little bit of me. I work as a machine learning platform architect as soon. And in my spare time I'm interested in following the evolution of technologies and exploring how they can turn into products that shape our future. So thanks again for your time. And please try out the smarty app and let me know what you think. Thank you."
    return transcript
    # print(f"Response result:\n{response.text}")


@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def call_summary_api(transcript):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # response = openai.Completion.create(
    #     model="text-davinci-003",
    #     # prompt=f"{transcript}\n\nTl;dr",
    #     prompt=f"summarize the following text and divide the key points into no more than 7 bullet points, sorted in logical sequential order:\n\n",
    #     # prompt=f"Generate 3 follow-up questions and 3 action items for the following meeting summary bullet points, ranked by importance."
#         prompt=f"analyze zoom's product strategies based on Porter's 5 forces."
    #     temperature=0.7,
    #     max_tokens=60,
    #     top_p=1.0,
    #     frequency_penalty=0.0,
    #     presence_penalty=1
    # )
    # summary = response.choices[0].text
    # HACK
    summary = "My project, SmarTy, is an attempt to make life easier for knowledge workers in the modern attention economy. It's a task planner that evaluates the importance and urgency of tasks, prioritizes them, and batches them together to reduce context switching fatigue. SmarTy works by providing example pairs of tasks and classes to the Cohere Classify API, which uses transfer learning to cluster new tasks into one of four categories: do it now, delegate, discard, or designate. The output pairs are then fed into the Cohere Embed API to calculate string embeddings, which are bundled into similar batches using k-means. SmarTy provides value by allowing users to focus their energy on impactful goals, reduce contact switching fatigue, create opportunities for teamwork, and identify and eliminate unnecessary busy work."
    return summary


@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def to_mp3(audio_file, output_audio_file, upload_path, download_path):
    ## Converting Different Audio Formats To MP3 ##
    if audio_file.name.split('.')[-1].lower()=="wav":
        audio_data = AudioSegment.from_wav(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="mp3":
        audio_data = AudioSegment.from_mp3(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="ogg":
        audio_data = AudioSegment.from_ogg(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="wma":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"wma")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="aac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"aac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="flac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"flac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="flv":
        audio_data = AudioSegment.from_flv(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="mp4":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"mp4")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")
    return output_audio_file

@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def process_audio(filename, model_type):
    model = whisper.load_model(model_type)
    result = model.transcribe(filename)
    return result["text"]

@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def save_transcript(transcript_data, txt_file):
    with open(os.path.join(transcript_path, txt_file),"w") as f:
        f.write(transcript_data)

audio_file = None
# st.session_state['transcript'] = ''

st.title("Whisper + GPT-3")
# st.info('✨ Supports all popular audio formats - WAV, MP3, MP4, OGG, WMA, AAC, FLAC, FLV 😉')
st.text("First upload your audio file and then select the model type. \nThen click on the button to transcribe and classify the sentiment of the text in the audio.")
upload_path = st.text_input("File directory:")
uploaded_file = st.file_uploader("Upload audio file", type=["wav","mp3","ogg","wma","aac","flac","mp4","flv"])

# if uploaded_file is not None:
    # audio_bytes = uploaded_file.read()
    # with open(os.path.join(upload_path,uploaded_file.name),"wb") as f:
    #     f.write((uploaded_file).getbuffer())
    # with st.spinner(f"Processing Audio ... 💫"):
    #     output_audio_file = uploaded_file.name.split('.')[0] + '.mp3'
    #     output_audio_file = to_mp3(uploaded_file, output_audio_file, upload_path, download_path)
    #     audio_file = open(os.path.join(download_path,output_audio_file), 'rb')
    #     audio_bytes = audio_file.read()
    # print("Opening ",audio_file)
    # st.markdown("---")
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.markdown("Feel free to play your uploaded audio file 🎼")
    #     st.audio(audio_bytes)
    # with col2:
    #     whisper_model_type = st.radio("Please choose your model type", ('Tiny', 'Base', 'Small', 'Medium', 'Large'))

    # print("Opening ", audio_file)

st.markdown("---")
col1, col2 = st.columns(2)
# generate_transcript = st.button("Generate Transcript")
if 'button_1' not in st.session_state:
    st.session_state.button_1 = False
if 'button_2' not in st.session_state:
    st.session_state.button_2 = False

if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ''
if 'summary' not in st.session_state:
    st.session_state['summary'] = ''


def cb1():
    st.session_state.button_1 = True
    st.write(f'"{st.session_state["transcript"]}"')


def cb2():
    st.session_state.button_2 = True

# Create a graphlib graph object
def create_graph():
    """Create graph."""
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    # response = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt="create a simple graphviz chart that explains how to make a pancake\n\nimport graphviz",
    #     temperature=0.7,
    #     max_tokens=500,
    #     top_p=1,
    #     frequency_penalty=0,
    #     presence_penalty=0
    # )
    # graph = response.choices[0].text
    graph = graphviz.Digraph()

    # Add nodes to the graph
    graph.node("A", "Gather Ingredients")
    graph.node("B", "Mix Together")
    graph.node("C", "Heat Pan")
    graph.node("D", "Pour Batter Into Pan")
    graph.node("E", "Flip Pancake")
    graph.node("F", "Enjoy!")

    # Add edges to the graph
    graph.edge("A", "B")
    graph.edge("B", "C")
    graph.edge("C", "D")
    graph.edge("D", "E")
    graph.edge("E", "F")
    return graph



# if upload_path:
#     with col1:
#         in1 = st.text_input("Enter transcript")
        # whisper_model_type = st.radio("Please choose your model type", ('Tiny', 'Base', 'Small', 'Medium', 'Large'))

if st.button("Generate Transcript"):
    with st.spinner(f"Generating Transcript... 💫"):
        transcript = call_whisper_api(os.path.join(upload_path, uploaded_file.name))
        # transcript = process_audio(str(os.path.abspath(os.path.join(download_path,output_audio_file))), whisper_model_type.lower())
        st.session_state['transcript'] = transcript
    if transcript is not None:
        st.subheader("Transcript:")
        st.write(f'"{st.session_state["transcript"]}"')
        # st.write(f'"{transcript}"')
    else:
        st.write("No transcript")
    # st.session_state.button_1 = False

    with st.spinner(f"Generating Summary... 💫"):
        summary = call_summary_api(st.session_state['transcript'])
        st.balloons()
    if summary is not None:
        st.subheader("Summary:")
        # st.write(f'"{st.session_state["summary"]}"')
        st.write(f'"{summary}"')
        # st.success('✅ Successful !!')
    else:
        st.write("No summary")

# Display the graph
graph = create_graph()
st.graphviz_chart(graph)

    # with col2:
    #     # summary = st.text_input("Enter summary")
    #
    #     if st.button("Generate Summary"):
    #
    #         # st.session_state.button_2 = False
# else:
#     st.warning('⚠ Please upload your audio file 😯')