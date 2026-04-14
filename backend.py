# Phase 2- setup backend with FASTAPI
# Step1: Setup Pydantic model
from urllib import response
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from ai_agent import response_from_ai_agents


class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[str]
    allow_search: bool


# step2- setup AI agent from FrontendRequest
allowed_model_names = ["llama-3.3-70b-versatile",
                       "meta-llama/llama-prompt-guard-2-22m", "gpt-4o-mini"]
app = FastAPI(title="LangGraph AI Agent")


@app.post("/chat")
def chat_endpoint(request: RequestState):
    # Validate model
    if request.model_name not in allowed_model_names:
        return {"error": "Invalid model, Select valid AI model"}

    try:
        llm_id = request.model_name
        query = request.messages
        system_prompt = request.system_prompt
        allow_search = request.allow_search
        provider = request.model_provider

        response = response_from_ai_agents(
            llm_id, query, allow_search, system_prompt, provider
        )

        return response

    except Exception as e:
        print("Primary failed:", e)

        try:
            fallback = response_from_ai_agents(
                "llama-3.3-70b-versatile",
                query,
                allow_search,
                system_prompt,
                "Groq"
            )
            return fallback

        except Exception as e2:
            return {
                "error": "Both OpenAI and Groq failed",
                "details": str(e2)
            }


# step 3 - run spp & explore UI docs
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999)
