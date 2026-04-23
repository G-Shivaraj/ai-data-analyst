# agent/core_agent.py
import re
import os
import plotly.express as px
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Load the API key from the .env file
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def process_query(df, query):
    """
    Takes a Pandas DataFrame and a user query.
    Returns either a string (answer) or a Plotly figure object.
    """
    
    # 1. Initialize the LLM via OpenRouter
    llm = ChatOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        #model="meta-llama/llama-3.1-8b-instruct", 
        model="openai/gpt-4o-mini",
        temperature=0.0 # Set to 0 for maximum strictness in following instructions
    )
    
    # 2. Stricter Prompt Engineering
    PREFIX = """
    You are an expert Data Analyst working with a pandas dataframe.
    
    RULE 1: For general questions (like calculations, averages, or data summaries), use your tools to find the answer, and output the final result as a NATURAL LANGUAGE TEXT STRING. DO NOT wrap your final answer in ```python blocks.
    
    RULE 2: CRITICAL - If and ONLY if the user explicitly asks for a chart, plot, or graph, you MUST output ONLY the Python code to generate it using plotly.express. 
    Assign the chart object to a variable named exactly 'fig'. Do NOT include `fig.show()`.
    Wrap the code in standard python markdown blocks like this:
    ```python
    import plotly.express as px
    fig = px.bar(df, x='col1', y='col2')
    ```
    """
    
    # 3. Create the LangChain Agent
    agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=True, 
        allow_dangerous_code=True, 
        prefix=PREFIX,
        agent_type="openai-tools" # Kept this, removed the deprecated handle_parsing_errors
    )

    try:
        # 4. Invoke the agent
        response = agent.invoke(query)
        output = response["output"]

        # 5. Stricter Output Router
        # Now it only triggers the chart logic if there is a python block AND it imports plotly (px)
        if "```python" in output and "px" in output:
            
            code_match = re.search(r"```python(.*?)```", output, re.DOTALL)
            if code_match:
                code_str = code_match.group(1).strip()
            else:
                code_str = output.replace("```", "").strip() 

            local_vars = {"df": df, "px": px}
            exec(code_str, globals(), local_vars)
            
            if 'fig' in local_vars:
                return local_vars['fig']
            else:
                return "I generated the chart code, but couldn't render it."
        
        # If no chart code was detected, return the text answer normally
        return output

    except Exception as e:
        # Add this print statement to see the REAL error in your terminal
        print(f"--- DEBUG ERROR --- \n{repr(e)}\n-------------------")
        return f"Oops! The AI encountered an error while processing that: {str(e)}"
    
def generate_dashboard(df):
    """
    Asks the LLM to generate 5 distinct charts as an automated dashboard.
    Returns a list of Plotly figure objects.
    """

    llm = ChatOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        #model="meta-llama/llama-3.1-8b-instruct", 
        model="openai/gpt-4o-mini",
        temperature=0.1 # Set to 0 for maximum strictness in following instructions
    )
    
    PREFIX = """
    You are an expert Data Scientist. 
    Analyze the provided pandas dataframe and generate 5 distinct, highly informative, and visually attractive charts using plotly.express.
    
    CRITICAL RULES:
    1. You MUST create exactly 5 different Plotly figure objects. Make them diverse and colourful (e.g., bar, scatter plot, pie, line, histogram).
    2. You MUST assign these 5 figures to a Python list named exactly 'figs'. (e.g., `figs = [fig1, fig2, fig3, fig4, fig5]`)
    3. Do NOT use `fig.show()`.
    4. Output ONLY the raw Python code wrapped in ```python blocks. Do not add any conversational text.
    """
    
    agent = create_pandas_dataframe_agent(
        llm, df, verbose=True, allow_dangerous_code=True, prefix=PREFIX, agent_type="openai-tools"
    )

    try:
        response = agent.invoke("Analyze the data and generate the 5 dashboard charts.")
        output = response["output"]

        if "```python" in output and "px" in output:
            code_match = re.search(r"```python(.*?)```", output, re.DOTALL)
            code_str = code_match.group(1).strip() if code_match else output.replace("```", "").strip() 

            local_vars = {"df": df, "px": px}
            exec(code_str, globals(), local_vars)
            
            # Extract the 'figs' list created by the LLM
            if 'figs' in local_vars and isinstance(local_vars['figs'], list):
                return local_vars['figs']
            
        return [] # Return empty list if it failed to make the charts
    except Exception as e:
        print(f"--- DASHBOARD ERROR --- \n{repr(e)}\n-------------------")
        return []
    
    