from dotenv import load_dotenv
import getpass
import os
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings 
from pinecone import Pinecone
from langchain import hub
import streamlit as st

from gtts import gTTS
from langgraph.graph import StateGraph, END
from IPython.display import Image, display

from pages.Slang import slang_main
from pages.Vocabulary import vocab_main

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


llm = init_chat_model("gpt-4o-mini", model_provider="openai")

### State

from typing import TypedDict, List, Dict

class State(TypedDict):
    spa_lyrics: str
    literal_translation: str
    adapted_translation: str
    slang_notes: List[Dict[str, str]]
    tutor_notes: str
    audio_path: str

### Node

# Transalator node
def translate_to_eng(state: State) -> State:
    system_message_content = (f"""
    Translate the following Spanish lyrics into English. Keep the meaning, tone, and style suitable for a song lyric. Here are the lyrics:
    {state['spa_lyrics']}
    """)

    prompt = [SystemMessage(system_message_content)]
    response = llm.invoke(prompt)
    state['literal_translation'] = response.content
    return state

# Culture Node
def cultural_adapt(state: State) -> State:
    system_message_content = f"""Adapt this English translation to sound natural, keeping cultural nuance:
    Here is the lyrics
    {state['literal_translation']}"""
    response = llm.invoke([HumanMessage(system_message_content)])
    state["adapted_translation"] = response.content
    return state

# Slang node
def slang_capture(state: State) -> State:
    system_message_content = (f"""
    Identify any slang or informal expressions in this piece of Spanish lyrics:
    \n
    {state['spa_lyrics']}
    \n
    For each slang term, provide:
    - The term
    - Its literal meaning
    - The region or dialect where it's commonly used
    - An example sentence
    \n
    If none, say "No slang found."
    """)
    prompt = [SystemMessage(system_message_content)]
    response = llm.invoke(prompt)
    state['slang_notes'] = response.content
    return state


# Tutor node
def vocab_tutor(state: State) -> State:
    system_message_content = f""" Explain the Spanish lyrics step by step in English, focusing on grammar, idioms, and meaning. Refer to the Slang Notes if there's any.
    /n
    Lyrics: {state['spa_lyrics']}
    Translation: {state['adapted_translation']}
    Slang Notes: {state['slang_notes']}"""
    response = llm.invoke([HumanMessage(system_message_content)])
    state['tutor_notes'] = response.content
    return state

# Audio node
def audio(state: State) -> State:
    tts = gTTS(state["adapted_translation"], lang="en")
    audio_path = "output.mp3"
    tts.save(audio_path)
    state["audio_path"] = audio_path
    return state


### Graph
graph_builder = StateGraph(State)
graph_builder.add_node('translation', translate_to_eng)
graph_builder.add_node('culture', cultural_adapt)
graph_builder.add_node('slang', slang_capture)
graph_builder.add_node('tutor', vocab_tutor)
graph_builder.add_node('audio', audio)

graph_builder.set_entry_point('translation')
graph_builder.add_edge("translation", "culture")
graph_builder.add_edge("culture", "slang")
graph_builder.add_edge("slang", "tutor")
graph_builder.add_edge("tutor", "audio")
graph_builder.add_edge("audio", END)


graph = graph_builder.compile()

# display(Image(graph.get_graph().draw_mermaid_png()))



# main_page = st.Page(spa_main, title="Spanish Song Translator", icon="🤖")
# slang_page = st.Page(slang_main, title="Slang Notes", icon="✏️")
# vocab_page = st.Page(vocab_main, title="Vocabulary Notes", icon="📖")

# pg = st.navigation([main_page, slang_page, vocab_page])
# pg.run()

st.set_page_config(
    page_title="Spanish Song Translator",
    page_icon="🤖" 
)
# slang_page = st.Page(slang_main, title="Slang Notes", icon="✏️")
# vocab_page = st.Page(vocab_main, title="Vocabulary Notes", icon="📖")

st.title("Spanish Song Translator")

st.text_area("Enter the spanish lyrics:",key="lyrics")

if st.button("Translate!"):
  state = {'spa_lyrics': st.session_state.lyrics}

  results = graph.invoke(state)

  st.subheader("Literal English Translation")
  st.write(results['literal_translation'])

  st.subheader("Cultural-adapted English Translation")
  st.write(results['adapted_translation'])
  
  st.subheader("Slang Tutor")
  st.write(results['slang_notes'])

  st.subheader("Vocabulary Builder")  
  st.write(results['tutor_notes'])

  st.subheader("Audio")
  st.audio(results['audio_path'])
