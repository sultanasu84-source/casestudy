from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END,START
from graph.state import State
from graph import graph

import streamlit as st
from nodes.intent import intent_node
from nodes.validation import validation_node
from nodes.analysis import *
from nodes.suggestions import suggestion_generator
from nodes.scoring import scoring_node
from nodes.report import final_report_builder
from typing import Annotated
from operator import add

import streamlit as st
import os



graph = StateGraph(State)

# ---------- Nodes ----------
graph.add_node("intent", intent_node)
graph.add_node("validation", validation_node)
graph.add_node("router" , lambda state:state)
graph.add_node("full_general", full_general_analysis)
graph.add_node("full_aspect", full_aspect_analysis)
graph.add_node("function_general", function_general_analysis)
graph.add_node("function_aspect", function_aspect_analysis)
graph.add_node("suggestions", suggestion_generator)
graph.add_node("scoring", scoring_node)
graph.add_node("final_report", final_report_builder)


graph.add_edge(START,"intent")
graph.add_edge("intent", "validation")
graph.add_edge("validation" ,"router")
graph.add_conditional_edges(
    "validation",              
    analysis_router,       
    {
        "full_general": "full_general",
        "full_aspect": "full_aspect",
        "function_general": "function_general",
        "function_aspect": "function_aspect",
    }
)

graph.add_edge("full_general", "suggestions")
graph.add_edge("full_aspect", "suggestions")
graph.add_edge("function_general", "suggestions")
graph.add_edge("function_aspect", "suggestions")
graph.add_edge("suggestions","scoring")
graph.add_edge("scoring","final_report")
graph.add_edge("final_report",END)




app = graph.compile()


st.set_page_config(page_title="Code Review Bot", layout="wide")

st.title("🧠 Code Review Assistant")

# -----------------------
# User inputs
# -----------------------

user_message = st.text_area(
    "📝 User Request",
    placeholder="e.g. Review only the function login_user focusing on security",
    height=100
)

uploaded_file = st.file_uploader(
    "📂 Upload Code File (.py)",
    type=["py"]
)

analyze = st.button("🚀 Analyze")

# -----------------------
# Run analysis
# -----------------------
if analyze:
    if not user_message or not uploaded_file:
        st.error("Please provide both a user message and a code file.")
    else:
        code_text = uploaded_file.read().decode("utf-8")

        state: State = {
            "user_message": user_message,
            "code_text": code_text,

            "scope": "",
            "aspects": [],
            "function_name": None,
            "request": {},

            "code_to_analyze": "",
            "is_valid": True,
            "validation_error": None,

            "risks": [],
            "suggestions": [],
            "score": 0,
            "final_report": ""
        }

        with st.spinner("Analyzing code..."):
            result = app.invoke(state)
            if not result.get("is_valid", True):
              st.error(result["validation_error"])
              st.stop()

        st.success("Analysis completed!")

        st.subheader("🧾 Final Report")
        st.markdown(result["final_report"])
