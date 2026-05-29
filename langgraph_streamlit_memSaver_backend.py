from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq 
from langchain_core.messages import BaseMessage, HumanMessage
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver # this one is stores in RAM, refresh is deleting all
from langgraph.graph.message import add_messages 
import sqlite3
import os

# 1. Load environment variables from the .env file immediately
load_dotenv()

# Get the key from the environment (loaded from .env)
groq_api_key = os.getenv("GROQ_API_KEY")

# Check if the key was loaded successfully
if not groq_api_key:
    # If the key isn't found in .env or environment, print a helpful message and exit
    print("Error: GROQ_API_KEY not found. Please ensure it is set in your .env file.")
    llm = None
else:
    # 2. Initialize the ChatGroq LLM
    # max_tokens : parameter sets the maximum length,
    #The sum of your input tokens (prompt, RAG context, and history) plus the max_tokens (output limit) 
    # cannot exceed the model's total context window (e.g., $8,000$ or $128,000$ tokens, depending on the model). 
    
    # temperature :controls the randomness and creativity of the model's output.
    #The model is deterministic and focused. It always picks the most probable next word, 
    # provides factual outputs.Factual Q&A, Summarization, Code Generation, Technical Documentation.


    try:
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            # model_name="llama3-8b-8192",
            # model_name="mixtral-8x7b-32768",
            # model_name="gemma2-9b-it", 
            temperature=0.1, 
            max_tokens=1024
        )
        print("Groq LLM initialized successfully!")
    except Exception as e:
        print(f"Initialization Error: {e}")
        llm = None

class ChatState(TypedDict):
    #state will remove the last value and update with new value for every node execution.
    #While both use the Annotated pattern to define a "reducer" (a function that tells the state how to merge new data with old data), 
    #how the list of messages is updated when a node returns a value.

    messages : Annotated[list[BaseMessage], add_messages]


#Load the LLM as ChatOpenAI
# load_dotenv()
# llm = ChatOpenAI(model='gpt-4o-mini')

#Create the chatbot node and get message, invoke the input message , get response, and return to the state
def chat_node(state:ChatState):
    #uswr query from state
    message = state['messages']

    #sent to llm
    response = llm.invoke(message)

    #return return
    return {'messages': [response]}


#Create Checkpoint for persistance, for storing the super steps output to a checkpoint
checkpointer=InMemorySaver()


#build the graph with node and adges
graph = StateGraph(ChatState)
graph.add_node('chat_node',chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)


#compile the graph with checkpoint
chatbot= graph.compile(checkpointer=checkpointer)

#display the message history

CONFIG={'configurable':{'thread_id':'thread_1'}}
response = chatbot.invoke({'messages':[HumanMessage(content="what is my name?")]}, config=CONFIG)
print(chatbot.get_state(config=CONFIG).values['messages'])
print(response)