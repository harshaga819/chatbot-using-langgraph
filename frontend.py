import streamlit as st
from backend import chat_reply, retrive_old_chats
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import uuid

# ***************************functions********************************************************
def thread_id_generator():
    thread_id= uuid.uuid4()
    return thread_id

def new_chat():
    id= thread_id_generator()
    st.session_state['thread_id']= id
    st.session_state['message_history']= []
    add_thread_id(st.session_state['thread_id'])

def add_thread_id(thread_id):
    if thread_id not in st.session_state['chat_history']:
        st.session_state['chat_history'].append(thread_id)

def conversation_loading(thread_id):
    state= chat_reply.get_state(config= {"configurable": {"thread_id": thread_id}})
    if not state.values:
        return []
    return state.values['messages']

#********************************Session State************************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = retrive_old_chats()

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = thread_id_generator()

add_thread_id(st.session_state['thread_id'])


#***************************SideBar***********************************************************

st.sidebar.title("Private ChatBot")

if st.sidebar.button("Upload PDF"):
    pass

if st.sidebar.button("New Chat"):
    new_chat()

st.sidebar.header("My Conrevsation")
n=0
for thread_id in st.session_state['chat_history'][::-1]:
    n+= 1
    if st.sidebar.button(f'chat-{n}'):
        st.session_state['thread_id']= thread_id
        messages= conversation_loading(thread_id)

        temp_messages= []

        for message in messages:
            if isinstance(message, HumanMessage):
                role= 'user'
            else:
                role= 'assistant'
            temp_messages.append({'role': role, 'content': message.content})
        
        st.session_state['message_history']= temp_messages


#********************************Conversation History*****************************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])


#*********************************Chat input**************************************************

human_message = st.chat_input('Type here..')

if human_message:

    st.session_state['message_history'].append({'role': 'user', 'content': human_message})
    with st.chat_message('user'):
        st.write(human_message)

    config1= {"configurable":{"thread_id":st.session_state['thread_id']}}

    with st.chat_message('assistant'):
        def ai_only_stream():
            for chunk, metadata in chat_reply.stream(
                {"messages":[HumanMessage(content=human_message)]},
                 config = config1,
                 stream_mode= 'messages',
            ):
                if isinstance(chunk, AIMessage):
                    yield chunk.content
        
        ai_message= st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

