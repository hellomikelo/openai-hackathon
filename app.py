import base64
import os

import requests
import whisper
import streamlit as st
# from fpdf import FPDF
from pydub import AudioSegment
import openai
from dotenv import load_dotenv
import graphviz
from gdoc import GoogleDoc, get_creds

load_dotenv()

# import sys
# import subprocess
#
# # implement pip as a subprocess:
# subprocess.check_call([sys.executable, '-m', 'pip', 'install',
# '<packagename>'])

st.set_page_config(
    page_title="distill.ai",
    page_icon="alembic",
    layout="wide",
    initial_sidebar_state="auto",
)

upload_path = "./uploads/"
download_path = "./downloads/"
transcript_path = "./transcripts/"

openai.api_key = os.getenv("OPENAI_API_KEY")


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def make_transcript(file_path):
    file_name = os.path.basename(file_path)
    url = "https://whisper.lablab.ai/asr"
    payload = {}
    files = [
        ('audio_file', (file_name, open(file_path, 'rb'), 'audio/mpeg'))
    ]
    # https://audiotrimmer.com/
    response = requests.request("POST", url, data=payload, files=files)
    if response.status_code == 500:
        st.error("Failed to transcribe.")

    def parse_response(response):
        """Parse and reformat Whisper API response."""
        transcript = ''
        segments = response.json()['segments']
        for segment in segments:
            _s = segment["text"].strip()
            if _s[-1] not in ['.', '!', '?']:
                # Keep in same line
                transcript += f'{_s} '
            else:
                # Add new line
                transcript += f'{_s}\n'
        transcript = transcript[:-1]
        return transcript
    # transcript = response.json()['text'].strip()
    transcript = parse_response(response)

    # TMP
    # transcript = "Hello, my name is Mike and for this lab lab AI and Coheir hackathon, I like to share my project called smarty. And say mindful personal assistance. So in today's attention economy, our attention is a rare commodity. We're constantly inundated by more content, more social interactions, chores and work than our minds can adequately handle. David Allen, the author of getting things done, said that if you don't pay attention, appropriate attention to what has your attention, it will take more of your attention than it deserves. This problem is especially evident in the modern knowledge workforce. And being a knowledge worker myself. I definitely share that pain. I think there are three factors that contribute to the rules of modern knowledge work. We have a lack of boundary because of easily easy accessibility by messaging tools, resulting in a lot of ad hoc requests that pile on quickly, but without effective ways to clear them. To we have an accumulation of tasks, large and small that forces us to constantly switch context, leading to burnouts and frustrations. Three, the productivity tools that we use today are still not intelligent enough to adequately fill filter our date to do list and to help protect our time. So these issues result in significant cost of context switching on any given day and knowledge workers toggle on an average 1200 times between different apps and websites. And once distracted workers need an average of 23 minutes returns the original task. This totals into roughly 9% of one's annual work time that's spent just on context switching. Yuck. So my project, smarty is an attempt to address those problems. Smarty quiets the noise around you so you could work peacefully to get things done. It's a task planner that evaluates the importance and urgency of your tasks, then prioritizes and batches them rigorously. So you can focus on accomplishing what matters the most. So here I will stop and do a quick demo. So here is the stream of that that I built smarty on top of a and the user starts by adding the tasks that they want to analyze and classify. And you can do it either via upload or copy pasting. And by default, there are two examples to get started. One is to get a doctor appointment for checkup. The other one is fly to the moon just for fun. And smarty will analyze and classify and batch these tasks into one of four buckets. Do these now schedule these reassign these to others and discard these. So as you can see here, smarty seems to think that doctor appointment is pretty important. So this is a do it now type of task. And as for fly to the moon just for fun. This is seems like a kind of a trivial task or so smarty says just discarded for now. Yeah. And so if we want to add additional tasks. It's as simple as copy a pasting new ones in here. And then you'll see that there are new analysis that are turned out. And you can see that they're batched into tasks that are more suitable to do at in the same time, just due to the nature of those tasks. So for instance here you can see that cleaning the toilet vacuuming idea of after dinner they belong to batch zero. So they should be done at around the same time. And because they involve the same activities, whereas thinking through maternity leave schedule. That's more of a sit down and think type of task. So that's batch one. So there you have it. This is a quick demo of the smarty app. And I will go back to the presentation. Great. Okay, so smarty provides value by allowing you to one focus your energy on impactful goals by setting boundaries around your time and mental space. To it reduces contact switching fatigue by understanding the relationships between tasks and bundling similar ones together to work on at once. It creates opportunities for teamwork by delegating tasks to collaborators and giving others a chance to shine. And for it identify and eliminate unnecessary busy work to free up your time for things that matter. So how does smarty work underneath the hood. So one user provides an example pairs of tasks and classes to the cohere classify API and the API learns from the examples using future learning and then clusters new tasks into one of four classes do it now delegated discarded or designated. And the output pairs of tasks and classes are fed into the cohere embed API to calculate string embeddings, which are then bundled into similar batches using k means. And then for the resulting task classes and batches are displayed via a stream but interface. So there are a lot of different exciting paths that can be pursued from here, and three major ones that I can think of our, we can add upstream and downstream integrations in a smarty to enable seamless in task and ingestion and hand off with different applications to we can also implement natural language explainability to describe why tasks are classified and batched away they are. And with that can help humans make the final decisions in terms of what they want to do. And three, finally, we can also set up quantitative and qualitative evaluation metrics to measure classifier performance and understand how well it caters to the user's needs. Okay, so this concludes my presentation on smarty. So thank you for your attention. And before I'm here and here, here's a little bit of me. I work as a machine learning platform architect as soon. And in my spare time I'm interested in following the evolution of technologies and exploring how they can turn into products that shape our future. So thanks again for your time. And please try out the smarty app and let me know what you think. Thank you."
    return transcript


def call_complete_api(prompt, max_tokens=60):
    response = openai.Completion.create(
        model="text-davinci-003",
        # prompt=f"summarize the following text and divide the key points into no more than 7 bullet points, sorted in logical sequential order:\n\n",
        prompt=prompt,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1
    )
    return response


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def make_summary(transcript, max_tokens=500):
    prompt=f"{transcript}\n\nTl;dr:\n\n",
    response = call_complete_api(prompt, max_tokens)
    summary = response.choices[0].text.strip()
    # TMP
    # summary = "- My project, SmarTy, is an attempt to make life easier for knowledge workers in the modern attention economy \n- It's a task planner that evaluates the importance and urgency of tasks, prioritizes them, and batches them together to reduce context switching fatigue \n- SmarTy works by providing example pairs of tasks and classes to the Cohere Classify API which uses transfer learning to cluster new tasks into one of four categories: do it now, delegate, discard, or designate \n- The output pairs are then fed into the Cohere Embed API to calculate string embeddings, which are bundled into similar batches using k- means \n- SmarTy provides value by allowing users to: \n\t- Focus their energy on impactful goals \n\t- Reduce contact switching fatigue \n\t- Create opportunities for teamwork \n\t- Identify and eliminate unnecessary busy work\n"
    return summary


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def make_title(summary, max_tokens=60):
    prompt = f'generate a blog title from the following summary:\n\n"{summary}"'
    response = call_complete_api(prompt, max_tokens)
    title = response.choices[0].text.strip()
    title = title.replace('"', '')
    # TMP
    # questions = """
    # 1. How is Smary different from other personal assistant technologies?
    # 2. What plans do you have to further develop the Coheir API?
    # 3. What type of user feedback have you received so far?
    # """
    return title


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def make_questions_action_items(prompt, max_tokens=200):
    prompt=f'Generate 3 follow-up questions and 3 action items as bullet points for the following conversation summary.\n\n"{prompt}"'
    response = call_complete_api(prompt, max_tokens)
    action_items = response.choices[0].text
    # TMP
    # action_items = """
    # 1. Research potential integrations for Smary.
    # 2. Develop natural language explainability for Smary.
    # 3. Set up evaluation metrics for Smary.
    # """
    return action_items


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def make_metaphor(prompt, max_tokens=200):
    prompt = f'Generate a metaphor for the following concepts.\n\n"{prompt}"'
    response = call_complete_api(prompt, max_tokens)
    metaphor = response.choices[0].text
    return metaphor


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def make_image(metaphor, max_tokens=40):
    prompt = f'describe the metaphor below as an photo in one bullet point.\n\n"{metaphor}"'
    response = call_complete_api(prompt, max_tokens)
    metaphor = response.choices[0].text
    response = openai.Image.create(
      prompt=metaphor.strip(),
      n=1,
      size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def save_transcript(transcript_data, txt_file):
    with open(os.path.join(transcript_path, txt_file), "w") as f:
        f.write(transcript_data)


@st.cache(persist=True, allow_output_mutation=False, show_spinner=False, suppress_st_warning=True)
def make_graph(summary, img_file_name, max_tokens=500):
    """Create a graphlib graph object."""
    prompt = f'create but do render a graphviz chart that connects the relationships within the following concept:\n"{summary}"\n\nimport graphviz\ngraph = graphviz.Digraph()\n\n'
    response = call_complete_api(prompt, max_tokens)
    graph_plan = response.choices[0].text
    graph = graphviz.Digraph()
    try:
        exec(graph_plan)
        graph.render(img_file_name, format='png', view=False)
    except:
        print('no graph plan')

    return graph

audio_file = None
# st.session_state['transcript'] = ''

with st.sidebar:
    st.title("⚗️ Distiller")

    # st.info('✨ Supports all popular audio formats - WAV, MP3, MP4, OGG, WMA, AAC, FLAC, FLV 😉')
    # st.write("👋 What would you like to distill today?️")
    # uploaded_file = st.file_uploader("Upload audio file",
    #                                  type=["wav", "mp3", "ogg", "wma", "aac", "flac", "mp4", "flv"])

    uploaded_file = st.selectbox(
        "👋 What would you like to distill today?️",
        ("TFTS-1.mp3", "TFTS-2.mp3", "TFTS-3.mp3", "TFTS-4.mp3"),
    )
    if uploaded_file:
        # audio_file = open(os.path.join(upload_path, uploaded_file.name), 'rb')
        audio_file = open(os.path.join(upload_path, uploaded_file), 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/ogg')

        generate_transcript = st.button("Generate Transcript")
    # generate_summary = st.button("Generate Summary")

# if upload_path:
#     with col1:
#         in1 = st.text_input("Enter transcript")
# whisper_model_type = st.radio("Please choose your model type", ('Tiny', 'Base', 'Small', 'Medium', 'Large'))

if uploaded_file and generate_transcript:
    with st.spinner(f"Generating Transcript... 💫"):
        # Create Google Doc and add content
        creds = get_creds()
        gdoc = GoogleDoc(creds)

        # img_file_name = 'diagram'
        transcript = make_transcript(os.path.join(upload_path, uploaded_file.name))
        summary = make_summary(transcript)
        metaphor = make_metaphor(summary)
        img_url = make_image(metaphor)
        action_items = make_questions_action_items(summary)
        title = make_title(summary)
        # make_graph(summary, img_file_name)

        # title = 'Meeting Aid Summary'

        # Put it all together
        full_text = f"TRANSCRIPT OF CONVERSATION:\n{transcript.strip()}\nSUMMARY OF CONVERSATION:\n{summary.strip()}\nSOME NEXT STEPS TO CONSIDER:\n{action_items.strip()}\nA NICE METAPHOR TO ROUND IT OUT:\n{metaphor.strip()}\n"

        # W/O diagram
        doc_url, img_file_id = gdoc.create_doc(title, full_text, img_file_id=img_url) # f'{img_file_name}.png')
        # W diagram
        # doc_url, img_file_id = gdoc.create_doc(title, full_text, f'{img_file_name}.png')
        st.markdown(f"See the audio transcript, summary, and analyses in this [Google Doc]({doc_url}).")

        # os.remove(img_file_name)
        # os.remove(f'{img_file_name}.png')
        # _ = delete_gdrive_img_file(img_file_id)



        # TMP
#         transcript = """
#         See full transcript
# thinking of other solutions and two, they are incapable of seeing better solutions.
#
# So they really lock in on that one solution.
#
# So when you say you're an ideas guy, I like to joke, no, you're not, you're an idea guy,
#
# because I am too, which is to say the tendency of the human brain is to fixate on the first solution that comes to mind. And yet there's very little research, almost none that suggests that there's any kind of quality and time association, meaning the best ideas don't come first. In fact,
#
# there's a fascinating piece of research called the creative cliff illusion, where the researchers demonstrated that the typical person, they have this expectation that your creativity will precipitously decline at some point to cliff. The reason they call it the illusion though,
#
# is because it's actually not true. Your creativity doesn't decline hardly at all,
#
# let alone precipitously. And in fact, there are some people for whom there's actually a creative ramp where creativity increases over time. You know who those people are?
#
# Tell me. They're the people who expect they'll keep having good ideas.
#
# So the mindset of expect, okay, I'm seeing how you're building your answer. So what is that mindset that helps us create more and more ideas and not be blinded by the first one that pops into our head? Exactly. It's shifting orientation. And that's really at the heart of ideal flow.
#
# The human tendency is to fixate on the right answer. And very few problems we face in business or in life have a single right answer. It's not like math. I mean, and by the way, even advanced math doesn't have a single right answer. It blows your mind. But most people think, can I just look in the back of the textbook and see that I get it right? And that's the wrong way to approach like what the subject line of this email should be. There's no right answer. How I open this presentation, there's no right answer. How I give this piece of feedback. So forget even new products and new services. If you think about the problems most managers or professionals face, they're problems of I'm trying to solve this thing right now. And if they're"""
#         st.session_state['transcript'] = transcript
#     if transcript:
#         st.subheader("Transcript:")
#         with st.expander("See full transcript"):
#             st.write(f'{st.session_state["transcript"]}')
#         st.download_button(
#             label="Download transcript",
#             data=transcript,
#             file_name="meeting-aid-transcript.txt",
#             mime="text/plain"
#         )
#     else:
#         st.write("No transcript")
#     # st.session_state.button_1 = False
#
#     with st.spinner(f"Generating Summary... 💫"):
#         summary = make_summary(st.session_state['transcript'])
#         # st.balloons()
#     if summary:
#         st.subheader("Summary:")
#         st.write(summary)
#
#     with st.spinner(f"Generating Questions and Action Items... 💫"):
#         action_items = make_questions_action_items(summary)
#     if action_items:
#         st.subheader('Results')
#         st.write(action_items)

    # Display the graph
    # graph = make_graph(summary)
    # graph.render('idea-flow-2', format='png', view=False)
    # st.graphviz_chart(graph)

    #
    # # Replace the placeholder with some text:
    # st.subheader("Graph")
    # # placeholder = st.empty()
    # # placeholder.text("Graph")
    # graph = make_graph(summary)
    # st.graphviz_chart(graph)

    # pdf = FPDF('P', 'mm', 'A4')
    # pdf.add_page()
    # pdf.set_font(family='Times', size=16)
    # pdf.cell(40, 50, txt=summary)

    # def create_download_link(val, filename):
    #     b64 = base64.b64encode(val)  # val looks like b'...'
    #     return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

    # pdf = FPDF('P', 'mm', 'letter')
    # pdf.add_page()
    # pdf.set_font('Arial', '', 8)
    # pdf.multi_cell(0, 5, summary, 0, 1)
    # pdf.header('abcd')
    # pdf.multi_cell(0, 5,
    #                'Surbhi Mall, 105, Eva, Waghawadi Rd., opp. akshwarwadi temple, Hill Drive, Bhavnagar, Gujarat 364002',
    #                0, 1)
    #
    # html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test_pdf")
    # st.markdown(html, unsafe_allow_html=True)

else:
    st.warning("Please upload an audio file on the left.")




# with col2:
#     # summary = st.text_input("Enter summary")
#
#     if st.button("Generate Summary"):
#
#         # st.session_state.button_2 = False
# else:
#     st.warning('⚠ Please upload your audio file 😯')



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
#
# col1, col2 = st.columns(2)
# # generate_transcript = st.button("Generate Transcript")
# if 'button_1' not in st.session_state:
#     st.session_state.button_1 = False
# if 'button_2' not in st.session_state:
#     st.session_state.button_2 = False
#
# if 'transcript' not in st.session_state:
#     st.session_state['transcript'] = ''
# if 'summary' not in st.session_state:
#     st.session_state['summary'] = ''
#
#
# def cb1():
#     st.session_state.button_1 = True
#     st.write(f'"{st.session_state["transcript"]}"')
#
#
# def cb2():
#     st.session_state.button_2 = True