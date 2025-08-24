from turtle import onclick
from dotenv import load_dotenv
import getpass
import os
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings 
from pinecone import Pinecone
from langchain import hub
from pydantic_core.core_schema import NoneSchema
import streamlit as st
from typing import TypedDict, List, Dict
from gtts import gTTS
from langgraph.graph import StateGraph, END
from IPython.display import Image, display

from pages.Slang import slang_main
from pages.Vocabulary import vocab_main
import json
import re
import pandas as pd


### Todo:
### 1. Make this an interactive chatbox style translator (especiall for the culture adaption part)
### 2. Add a RAG feature
### 3. Make the vocabulary list append istead of being overwritten
### 4. Adjust the position of the clear button
### 5. Button in vocabulary builder shows up the same time as the notes table

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


llm = init_chat_model("gpt-4o-mini", model_provider="openai")

### State



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
    # system_message_content = f""" Explain the Spanish lyrics step by step in English, focusing on grammar, idioms, and meaning. Refer to the Slang Notes if there's any.
    # \n
    # Lyrics: {state['spa_lyrics']}
    # Translation: {state['adapted_translation']}
    # Slang Notes: {state['slang_notes']}"""

    system_message_content = f"""Analyze the following Spanish lyrics and provide only a structured JSON object. 
    Do not include any explanations or text outside the JSON. The JSON should be an array where each element represents a word, starting with index 0 for the first word, 1 for the second, and so on.
    \n
    Instructions:
    - For each word in the lyrics that is **not a common stop word**, provide:
    \n
    - "Word": the original Spanish word
    \n
    - "POS": the part of speech
    \n
    - "Meaning": English translation or meaning
    \n
    - "Lemma": the dictionary form of a word
    \n
    - "Tense": if the word is a verb, include its tense; otherwise, null
    \n
    - "Conjugations": common conjugations if applicable; otherwise, "N/A"
    \n
    - "Example": a sentence in Spanish using the word in context
    \n
    Lyrics: "{state['spa_lyrics']}"""

    response = llm.invoke([HumanMessage(system_message_content)])
    # state['tutor_notes'] = response.content


    raw_output = response.content

    cleaned = re.sub(r"```json|```", "", raw_output).strip()

    # try:
    #     parsed = json.loads(cleaned.strip())
    #     if "Lyrics Analysis" in parsed:
    #         structured_output = parsed["Lyrics Analysis"]
    #     else:
    #         structured_output = parsed
    # except json.JSONDecodeError as e:
    #     structured_output = {"error": f"Failed to parse JSON: {e}", "raw": raw_output}
        
    try:
        parsed = json.loads(cleaned.strip())
        structured_output = parsed
    except json.JSONDecodeError as e:
        structured_output = {"error": f"Failed to parse JSON: {e}", "raw": raw_output}

    state["tutor_notes"] = structured_output
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


### Initialize state varaibles
if "lyrics" not in st.session_state:
    st.session_state.lyrics = ""

if "last_translation" not in st.session_state:
    st.session_state.last_translation = None

if "slang_notes" not in st.session_state:
    st.session_state.slang_notes = []

if "tutor_notes" not in st.session_state:
    st.session_state.tutor_notes = []

if "session_clear" not in st.session_state:
    st.session_state.session_clear = False

# Reset all
def clear_all():
    st.session_state.lyrics = ""
    st.session_state.last_translation = None
    st.session_state.slang_notes = []
    st.session_state.tutor_notes = []
    # st.session_state.session_clear = False

def change_session_state():
    if st.session_state.session_clear:
        st.session_state.session_clear = False

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

st.text_area("Enter the spanish lyrics:",key="lyrics", on_change=change_session_state)

if st.button("Translate!", type='primary'):
    state = {'spa_lyrics': st.session_state.lyrics}

    results = graph.invoke(state)

    # Save results to the last state so that it's not cleared
    st.session_state.last_translation = results

if st.button("Clear All Histories!", type='secondary', on_click=clear_all):
    st.session_state.session_clear = True

if st.session_state.last_translation and not st.session_state.session_clear:
    saved_results = st.session_state.last_translation

    st.subheader("Literal English Translation")
    st.write(saved_results['literal_translation'])

    st.subheader("Cultural-adapted English Translation")
    st.write(saved_results['adapted_translation'])
    
    st.subheader("Slang Tutor")
    st.write(saved_results['slang_notes'])

    st.subheader("Vocabulary Builder")  
    st.write(saved_results['tutor_notes'])

    st.subheader("Audio")
    st.audio(saved_results['audio_path'])


    # tutor_notes = saved_results['tutor_notes']
    
    tutor_notes_raw = saved_results['tutor_notes']
    if isinstance(tutor_notes_raw, str):
        try:
            tutor_notes = json.loads(tutor_notes_raw)
        except json.JSONDecodeError:
            st.error("Failed to parse tutor notes JSON.")
            tutor_notes = []
    else:
        tutor_notes = tutor_notes_raw


    if isinstance(tutor_notes, list):
        for word_info in tutor_notes:
            st.session_state.tutor_notes.append({
                "Word": word_info.get("Word"),
                "Part of Speech": word_info.get("POS"),
                "Meaning": word_info.get("Meaning"),
                "Lemma": word_info.get("Lemma"),
                "Tense": word_info.get("Tense"),
                "Conjugations": word_info.get("Conjugations"),
                "Example": word_info.get("Example"),
            })
    
    # if "tutor_notes" not in st.session_state or not st.session_state.tutor_notes:
    #     st.info("No new vocabularies yet. Go to the Translator page first.")
    # else:
    #     df = pd.DataFrame(st.session_state.tutor_notes)
    #     st.dataframe(df)


# if st.button("Clear!", type='secondary', on_click=clear_lyrics):
#     st.session_state.last_translation = None
#     st.session_state.session_clear = True