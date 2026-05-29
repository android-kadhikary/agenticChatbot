from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq 
from langchain_core.messages import BaseMessage, HumanMessage
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import InMemorySaver # this one is stores in RAM, refresh is deleting all
from langgraph.graph.message import add_messages 
import sqlite3

from langgraph.prebuilt import ToolNode, tools_condition 
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
import requests
import random


#Load the LLM 
load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')

#create Tools

#tool 1 , pre build tool (langgraph pre build)
# search_tool = DuckDuckGoSearchRun(region='us-en') 
search_tool = TavilySearchResults(max_results=3)


#tool 2
@tool
def calculate(a: float, operator: str, b: float) -> str:
    """
    Perform a basic calculation.
    Args:
        a: First number
        operator: One of '+', '-', '*', '/'
        b: Second number
    """
    if operator == '+': return str(a + b)
    if operator == '-': return str(a - b)
    if operator == '*': return str(a * b)
    if operator == '/': 
        return str(a / b) if b != 0 else "Error: Division by zero"
    return "Error: Invalid operator"

#tool 3
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=1LK20DLIO0OCIXWK"
    r = requests.get(url)
    return r.json()

tools_list = [search_tool,calculate,get_stock_price]
llm_with_tool = llm.bind_tools(tools_list)

#define State Class for langgrapg state 
class ChatState(TypedDict):
    #state will remove the last value and update with new value for every node execution.
    #While both use the Annotated pattern to define a "reducer" (a function that tells the state how to merge new data with old data), 
    #how the list of messages is updated when a node returns a value.

    messages : Annotated[list[BaseMessage], add_messages]

#Create the chatbot node and get message, invoke the input message , get response, and return to the state
#Node 1
def chat_node(state:ChatState):
    """LLM node that may answer or request a tool call."""
    message = state['messages']

    #sent to llm
    # response = llm.invoke(message)
    # with tool_list
    response = llm_with_tool.invoke(message) # LLM with all the tood info
    #return return
    return {'messages': [response]}
#Node 2
tool_node = ToolNode(tools_list)


#Create Checkpoint for persistance, for storing the super steps output to a checkpoint
# checkpointer=InMemorySaver()

conn=sqlite3.connect(database='chatbot_streamlit.db',check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)


#build the graph with node and adges
graph = StateGraph(ChatState)
graph.add_node('chat_node',chat_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, 'chat_node')
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')
graph.add_edge('chat_node', END)


#compile the graph with checkpoint , i.e. sqlite
chatbot= graph.compile(checkpointer=checkpointer)

#display the message history

# CONFIG={'configurable':{'thread_id':'thread_1'}}
# response = chatbot.invoke({'messages':[HumanMessage(content="what is my name?")]}, config=CONFIG)
# print(chatbot.get_state(config=CONFIG).values['messages'])
# print(response)

#Helper Method
def retrieve_all_thread():
    all_threads=set()
    #checkpointer.list(None) # this is a generator output
    for ckeckpoint in checkpointer.list(None):
        all_threads.add(ckeckpoint.config['configurable']['thread_id'])
    return list(all_threads)