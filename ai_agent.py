# To run - pipenv run python ai_agent.py
# Phase1:
# step 1: Setup API keys for Groq, openAI & Tavily

from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages.ai import AIMessage
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def response_from_ai_agents(llm_id, query, allow_search, system_prompt, provider):

    # step 2: Setup LLM & Tools
    # openai_llm = ChatOpenAI(model="gpt-4o-mini")
    # groq_llm = ChatGroq(model="llama-3.3-70b-versatile")
    # setting up search engine using tavily
    # search_tool = TavilySearch(max_results=2)

    # step 3: setup AI agent using langgraph and search tool functionalities
    if provider == "Groq":
        llm = ChatGroq(model=llm_id)
    elif provider == "OpenAI":
        llm = ChatOpenAI(model=llm_id)

    tools = [TavilySearch(max_results=2)] if allow_search else []
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    # query = "Tell me about the latest news about mid east war"
    state = {"messages": query}
    response = agent.invoke(state)
    # print(response)
    # we are filtering only messages from output
    messages = response.get("messages")
    # further filtering for AI messages (among AI messages & Human messages)
    ai_message = [
        message.content for message in messages if isinstance(message, AIMessage)]
    return ai_message[-1]
