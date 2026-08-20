from agent import chatbot, get_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import streamlit as st
from chat_name_agent import summerize_agent


def create_thread_id():
    return str(uuid.uuid4())

def add_thread_id(thread_id):
    if thread_id not in st.session_state['thread_history']:
        st.session_state['thread_history'].append({'thread_id': thread_id, 'name': None})

def get_chat_name(thread_id):

    thread = next(
        (
            thread
            for thread in st.session_state['thread_history']
            if thread['thread_id'] == thread_id
        ),
        None
    )

    if thread is None:
        return "New Chat"

    if thread['name'] is not None:
        return thread['name']

    state = chatbot.get_state(
        config= {'configurable': {'thread_id': thread_id}}
    )

    messages = state.values.get("messages")

    if not messages:
        return "New Chat"

    first_human_message = messages[0].content

    if first_human_message is None:
        return "New Chat"

    response = summerize_agent.invoke({
        'content': first_human_message
    })

    chat_name = response['name']

    thread['name'] = chat_name
    return chat_name

def add_message(role, content):
    message = {'role':role, 'content': content}
    st.session_state['message_history'].append(message)

def load_conversations(thread_id):
    state = chatbot.get_state(
        config= {'configurable': {'thread_id': thread_id}}
    )

    if not state or not state.values:
        return []

    return state.values.get("messages", [])

def reset_chat():

    st.session_state['thread_id'] = create_thread_id()
    st.session_state['message_history'] = []
    add_thread_id(st.session_state['thread_id'])

st.title("Chat Bot")

if "message_history" not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_history' not in st.session_state:
    st.session_state['thread_history'] = get_threads()

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = create_thread_id()
    add_thread_id(st.session_state['thread_id'])

st.sidebar.title("Recent Chats")

if st.sidebar.button("+ New Chat"):
    reset_chat()
    st.rerun()

for thread in st.session_state['thread_history'][::-1]:

    thread_id = thread['thread_id']
    if st.sidebar.button(
        get_chat_name(thread_id),
        key= thread_id
    ):

        st.session_state['thread_id'] = thread_id
        messages = load_conversations(thread_id)

        temp_message_list = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'

            elif isinstance(message, AIMessage):
                role = 'assistant'

            else: 
                continue

            temp_message_list.append({'role': role, 'content': message.content})

        st.session_state['message_history'] = temp_message_list
        st.rerun()

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Enter Something...")

if user_input:

    add_message('user', user_input)
    with st.chat_message("user"):
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {
                    'messages':[HumanMessage(content= user_input)]
                },
                config= {'configurable': {'thread_id': st.session_state['thread_id']}},
                stream_mode= 'messages'
            )
        )

    add_message('assistant', ai_message)