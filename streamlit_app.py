import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import HumanMessage

# FIX: Change the import path for InvalidArgument to the correct location
try:
    from google.api_core.exceptions import InvalidArgument 
except ImportError:
    # Fallback/error handling if the google-api-core package is missing
    InvalidArgument = Exception
    st.error("Missing dependency: Please run 'pip install google-api-core' in your terminal.")


# Load environment variables (like GEMINI_API_KEY) from .env file
load_dotenv()

# --- Configuration ---
# Set page config at the very beginning
st.set_page_config(page_title="Gemini Q&A Demo", layout="centered")
st.header("Langchain Gemini Application")

# Initialize session state for storing history/results
if 'response_text' not in st.session_state:
    st.session_state['response_text'] = ""

# --- DIAGNOSTIC FUNCTION ---
# We keep caching on for this function as it's only a local check
@st.cache_data(show_spinner=False)
def check_api_key_status():
    """Checks the status of the GEMINI_API_KEY."""
    # Try getting key from Streamlit secrets first, then environment variable
    key = None
    if "GEMINI_API_KEY" in st.secrets:
        key = st.secrets["GEMINI_API_KEY"]
    else:
        key = os.getenv("GEMINI_API_KEY")
        
    if key and key != "YOUR_ACTUAL_KEY_HERE":
        st.success("✅ GEMINI_API_KEY detected and loaded.")
    else:
        st.warning("⚠️ GEMINI_API_KEY not found. Please ensure it is set in your .env file.")

# --- LLM Function with Caching (DISABLED FOR DEBUGGING) ---

# Commented out @st.cache_data to ensure we see fresh results and errors immediately
# @st.cache_data 
def get_gemini_response(prompt: str, temperature: float, max_tokens: int) -> str:
    """Invokes the Gemini API and returns the response content."""
    
    # Try getting key from Streamlit secrets first, then environment variable
    gemini_key = None
    if "GEMINI_API_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_key = os.getenv("GEMINI_API_KEY") 
    
    if not gemini_key:
        # This error is caught by check_api_key_status, but remains here as a fallback
        return "Error: GEMINI_API_KEY environment variable not set."

    try:
        # Initialize LLM model 
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key, 
            temperature=temperature,
            max_output_tokens=max_tokens 
        )
        
        # Use st.spinner for a loading indicator during the API call
        with st.spinner("Asking Gemini..."):
            response = llm.invoke([
                HumanMessage(content=prompt)
            ])
            return response.content

    except InvalidArgument as e:
        # ❗ RETURN THE ERROR MESSAGE DIRECTLY ❗
        # This ensures the API key error is displayed to the user.
        return f"API FAILURE: Invalid/Expired Key. Details: {e}"
    except Exception as e:
        return f"AN UNEXPECTED ERROR OCCURRED: {e}"

# --- Streamlit UI and Logic ---

# Display the key status check at the top
check_api_key_status()

# 1. Input Fields
input_text = st.text_input("Input your question here:", key="input")

# Use slightly higher tokens and the same temperature 0.7 
# (You can try setting temperature=0.9 for more creativity)
DYNAMIC_MAX_TOKENS = 500 
DYNAMIC_TEMPERATURE = 0.7

# 2. Submit Button Logic (Conditional Execution)
submit = st.button("Ask the question")

if submit and input_text:
    # Call the LLM function with the new, higher token limit
    result = get_gemini_response(input_text, 
                                 temperature=DYNAMIC_TEMPERATURE, 
                                 max_tokens=DYNAMIC_MAX_TOKENS)
    
    # Store the result in session state to maintain display across reruns
    st.session_state['response_text'] = result
    st.session_state['last_question'] = input_text

# 3. Display Output
if st.session_state['response_text']:
    st.subheader("The Answer")
    if st.session_state.get('last_question'):
        st.info(f"Question: {st.session_state['last_question']}")
    
    # Use st.markdown to display either the successful answer OR the error string
    st.markdown(st.session_state['response_text'])