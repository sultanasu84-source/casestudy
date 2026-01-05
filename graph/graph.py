from langgraph.graph import StateGraph, END,START
from graph.state import State

from nodes.intent import intent_node
from nodes.validation import validation_node
from nodes.analysis import *
from nodes.suggestions import suggestion_generator
from nodes.scoring import scoring_node
from nodes.report import final_report_builder

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


