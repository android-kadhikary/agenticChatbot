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

class ChatState(TypedDict):
    #state will remove the last value and update with new value for every node execution.
    #While both use the Annotated pattern to define a "reducer" 
    # (a function that tells the state how to merge new data with old data), 
    #how the list of messages is updated when a node returns a value.

    messages : Annotated[list[BaseMessage], add_messages]


#Load the LLM 
load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')

#Create the chatbot node and get message, invoke the input message , get response, and return to the state
def chat_node(state:ChatState):
    #uswr query from state
    message = state['messages']

    #sent to llm
    response = llm.invoke(message)

    #return return
    return {'messages': [response]}


#Create Checkpoint for persistance, for storing the super steps output to a checkpoint
# checkpointer=InMemorySaver()

conn=sqlite3.connect(database='chatbot_streamlit.db',check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)


#build the graph with node and adges
graph = StateGraph(ChatState)
graph.add_node('chat_node',chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)


#compile the graph with checkpoint
chatbot= graph.compile(checkpointer=checkpointer)

#display the message history

# CONFIG={'configurable':{'thread_id':'thread_1'}}
# response = chatbot.invoke({'messages':[HumanMessage(content="what is my name?")]}, config=CONFIG)
# print(chatbot.get_state(config=CONFIG).values['messages'])
# print(response)

def retrieve_all_thread():
    all_threads=set()
    #checkpointer.list(None) # this is a generator output
    for ckeckpoint in checkpointer.list(None):
        all_threads.add(ckeckpoint.config['configurable']['thread_id'])
    return list(all_threads)