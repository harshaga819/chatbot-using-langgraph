import streamlit as st
from backend import chat_reply, retrive_old_chats
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import uuid
from retriever_manager import upload_file, process_website

# ***************************functions********************************************************

# It generate new thread id
def thread_id_generator():
    thread_id= uuid.uuid4()
    return thread_id

# It create new chat and reset all the message history, add chat name 
def new_chat():
    thread_id= thread_id_generator()
    st.session_state['thread_id']= thread_id
    st.session_state['message_history']= []
    add_thread_id(st.session_state['thread_id'], len(st.session_state["chat_names"]) + 1)

# It adds the thread id in chat_history list and also add the chat name in chat_names disc
def add_thread_id(thread_id, chat_number):
    if thread_id not in st.session_state['chat_history']:
        st.session_state['chat_history'].append(thread_id)
        st.session_state['chat_names'][thread_id]= f"chat-{chat_number}"

# It load the conversation history
def conversation_loading(thread_id):
    state= chat_reply.get_state(config= {"configurable": {"thread_id": thread_id}})
    if not state.values:
        return []
    return state.values['messages']

# It display the popup screen and takes website url as input and process it 
@st.dialog("Chat with Website")
def website_popup():
    url = st.text_input("Website URL", placeholder="https://example.com")

    if st.button("Process Website"):
        if not url.startswith(("http://", "https://")):
            st.error("Please enter a valid URL.")
            st.session_state.show_popup = False
            st.rerun()
        try:
            with st.spinner("Processing website..."):
                process_website(url=url, thread_id=str(st.session_state["thread_id"]))

            st.success("Website processed successfully.")

            st.session_state.show_popup = False
            st.rerun()
        except Exception as e:
            st.error(str(e))


#********************************Session State************************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = retrive_old_chats()

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = thread_id_generator()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

if "chat_names" not in st.session_state:
    st.session_state["chat_names"] = {}

for i, thread_id in enumerate(st.session_state["chat_history"], start=1):
    if thread_id not in st.session_state["chat_names"]:
        st.session_state["chat_names"][thread_id] = f"Chat-{i}"

add_thread_id(st.session_state['thread_id'], len(st.session_state["chat_names"]) + 1)

threads = st.session_state["chat_history"][::-1]
selected_thread = None


st.title("   Agentic RAG ChatBot")

#***************************SideBar***********************************************************

st.sidebar.title("Your Own Chatbot")

if st.sidebar.button("Chat with website"):
    new_chat()
    st.session_state.show_popup = True

if st.session_state.show_popup:
    website_popup()

if st.sidebar.button("New Chat"):
    new_chat()

thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})

uploaded_pdf= st.sidebar.file_uploader("Upload a PDF for this chat", type=["pdf"], key=f"uploader_{st.session_state['thread_id']}")

if uploaded_pdf: 
    if uploaded_pdf.name in thread_docs:
        st.sidebar.info(f"`{uploaded_pdf.name}` already processed for this chat.")
    else:
        with st.sidebar.status("Indexing PDF…", expanded=True) as status_box:
            summary = upload_file(uploaded_pdf.getvalue(), thread_id=thread_key, filename=uploaded_pdf.name,)
            thread_docs[uploaded_pdf.name] = summary
            status_box.update(label="PDF indexed", state="complete", expanded=False)


st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_history'][::-1]:

    title = st.session_state["chat_names"][thread_id]

    if st.sidebar.button(title):
        st.session_state['thread_id']= thread_id
        messages= conversation_loading(thread_id)

        temp_messages= []

        for message in messages:
            if isinstance(message, HumanMessage):
                role= 'user'
                temp_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                if message.content:
                    temp_messages.append({"role": "assistant", "content": message.content})
            elif isinstance(message, ToolMessage):
            # Ignore tool outputs
                continue
        
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
                {"messages":[HumanMessage(content=human_message)],
                 "thread_id": str(st.session_state["thread_id"]),},
                 config = config1,
                 stream_mode= 'messages',
            ):
                if isinstance(chunk, AIMessage):
                    yield chunk.content
        
        ai_message= st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

