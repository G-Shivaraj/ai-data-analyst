import streamlit as st
from utils.data_handler import load_and_summarize_csv
from agent.core_agent import process_query, generate_dashboard # Import the new function

st.set_page_config(page_title="AI Data Analyst", page_icon="📊", layout="wide")

# Initialize Session State
if "df" not in st.session_state:
    st.session_state.df = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dashboard_figs" not in st.session_state:
    st.session_state.dashboard_figs = [] # Store the dashboard charts here

with st.sidebar:
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None and st.session_state.df is None:
        df, summary = load_and_summarize_csv(uploaded_file)
        if df is not None:
            st.session_state.df = df
            st.success("File ready!")
            
            # --- NEW: Generate Dashboard Automatically ---
            with st.spinner("🤖 AI is building your automated dashboard... please wait."):
                st.session_state.dashboard_figs = generate_dashboard(st.session_state.df)
                
            with st.expander("View AI Schema Context"):
                st.code(summary)
        else:
            st.error(summary)
            
    if st.session_state.df is not None:
        if st.button("Clear Data & Chat"):
            st.session_state.df = None
            st.session_state.messages = []
            st.session_state.dashboard_figs = []
            st.rerun()

st.title("📊 AI Data Analyst")

if st.session_state.df is not None:
    
    # --- NEW: Render the Dashboard ---
    if st.session_state.dashboard_figs:
        st.subheader("Executive Dashboard")
        
        # Create a 2-column grid for the charts
        cols = st.columns(2)
        for i, fig in enumerate(st.session_state.dashboard_figs):
            # Place charts alternating between the two columns
            cols[i % 2].plotly_chart(fig, use_container_width=True)
            
        st.divider() # Draw a line to separate the dashboard from the chat

    # Chat History
    st.subheader("Ask Data Questions")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["type"] == "text":
                st.markdown(msg["content"])
            elif msg["type"] == "plot":
                st.plotly_chart(msg["content"], use_container_width=True)

    # Chat Input
    if prompt := st.chat_input("Ask a deeper question or request a specific chart..."):
        st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                response = process_query(st.session_state.df, prompt)
                
                if isinstance(response, str):
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "type": "text", "content": response})
                else: 
                    st.plotly_chart(response, use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "type": "plot", "content": response})
else:
    st.info("👈 Please upload a CSV file in the sidebar to get started.")