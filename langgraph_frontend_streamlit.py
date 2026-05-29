#install langgraph, langchain, streamlit
#main components of Streamlit, chat_message, chat_input
from langgraph_backend import chatbot, retrieve_all_thread
import streamlit as st
from langchain_core.messages import HumanMessage
import uuid
# st.session_state['count']=0
if 'count' not in st.session_state:
    st.session_state['count']=0
# print(f"run count :{st.session_state['count']}")

#LLM model
model='Groq'

# 1) create new thread id for each new chat
def generate_thread_id(): 
    thread_id=uuid.uuid4()
    return thread_id

# create new chat on click " new chat button"
# 1) generate new thread id, 2) save it in session, 3)reset message history
def reset_chat():
    thread_id= generate_thread_id()
    st.session_state['thread_id']= thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

#list of all thread ids
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def display_conversation(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages']

# streamlit.session_state is a dictionary,set one key name as 'message_history' 
# and contains a list, 
# that is message history, this stores the messages from last run, not reset.
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]


#2) create dynamic thread id for each session
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# add all the thread ids to the chat_thread
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrieve_all_thread() #if db is configured, then get the messages from db

add_thread(st.session_state['thread_id'])

# 3) Streamlit UI setup
st.set_page_config(page_title='Agentic Rag Application', layout='wide')
st.title(f"Groq-Powered count {st.session_state['count']}")
st.caption(f"powered by {model}")
st.sidebar.title("LangGraphchatbot")

if st.sidebar.button("Start New Chat"):
    reset_chat()

st.sidebar.header("Conversation Details")
for thread_id in st.session_state['chat_thread'][::-1]:
    # st.sidebar.text(f"Thread id :{thread_id}")
    if st.sidebar.button(f"Thread id :{thread_id}"):
        st.session_state['thread_id']=thread_id
        each_thread_messages=display_conversation(thread_id)
        temp_messsages=[]
        for thread_message in each_thread_messages:
            if isinstance(thread_message,HumanMessage):
                role= 'user'
            else:
                role= 'assistant'
            temp_messsages.append({'role':role, 'content': thread_message.content})
        st.session_state['message_history']=temp_messsages


for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

set_count:int=st.session_state['count']+1
st.session_state['count']=set_count
print(f"st.session_state['count']{st.session_state['count']}")

input= st.chat_input('Type here :')

if input:
    
    st.session_state['message_history'].append({'role':'user', 'content':input})
    with st.chat_message('user'):
        st.text(f'{input}')

    #create thread
    # CONFIG={'configurable':{'thread_id':st.session_state['thread_id']}}

    #config for lsngsmith thread

    CONFIG={
        'configurable':{'thread_id':st.session_state['thread_id']},
        "metadata": {
            "thread_id":st.session_state["thread_id"]
        },
        "run_name": "chat_bot_v1"
        }

    #Initiate the state message with the user input, and invoke the chatbot workflow with config
    initial_state={'messages' : [HumanMessage(content=input)]}
    # response= chatbot.invoke(initial_state, config=CONFIG) # this chatbot is from backend.py file
    
    response= chatbot.stream(initial_state, config=CONFIG,stream_mode='messages') # this chatbot is from backend.py file
    
    # assistant_ans=response['messages'][-1].content
    # assistant_ans=f'Welcome {input} !!!'
    # st.session_state['message_history'].append({'role':'assistant', 'content':assistant_ans})    
    with st.chat_message('assistant'):
        # st.text(assistant_ans)
        ai_message=st.write_stream(message_chunk.content for message_chunk,metadata in response)
    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})

print("end of run")
#initialize the session state for chat history and ingestion status

