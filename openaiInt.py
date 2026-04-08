from openai import OpenAI
from fastapi import FastAPI

client = OpenAI()
app = FastAPI()

@app.post("/chat")
async def chat(input: str, model: str = "gpt-5.4"):
    response = client.responses.create( model=model, input=input)
    return {"response": response.text}
