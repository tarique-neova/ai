import streamlit as st
from streamlit_chat import message
import bot
import base64

# page_bg_color = '''
# <style>
# [data-testid="stAppViewContainer"] {
#     background-color: #f0f2f6; 
# }
# [data-testid="stHeader"] {
#     background: rgba(0, 0, 0, 0);
# }
# .ea3mdgi6 {
#     background: rgba(0, 0, 0, 0) !important;
# }
# </style>
# '''

# st.markdown(page_bg_color, unsafe_allow_html=True)

st.title("Create Cloud Resoucres with AI..!")

# Initialize session state to store user inputs and responses
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Function to get user input from the chat box
def get_text():
    input_text = st.chat_input("Write your message here...", key="input")
    return input_text

# Get user input
user_input = get_text()

# If there is a user input, get the bot's response and update the session state
if user_input:
    output = bot.chat_with_user(user_input)
    output = output.lstrip("\n")
    st.session_state['history'].append({"user": user_input, "bot": output})

# Display chat history
for chat in st.session_state['history']:
    message(chat["user"], is_user=True)
    message(chat["bot"])


