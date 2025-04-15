from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_BASE")
)

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

@app.post("/generate-js")
async def generate_js(request: Request):
    data = await request.json()
    instruction = data.get("instruction", "")

    prompt =f"""
                Convert the following instruction into pure browser JavaScript that works on mobile Safari or Chrome.

                INSTRUCTION: "{instruction}"

                ⚠️ IMPORTANT:
                - ONLY return executable JavaScript code. NO markdown. NO explanation. NO comments.
                - Do NOT wrap with ```javascript or any backticks.
                - Do NOT include comments or extra output — JUST the code.

                Example Output (good):
                document.querySelector('input[name="email"]').value = "user@example.com";
                document.querySelector('button[type="submit"]').click();

                Now return the JavaScript code only:
            """


    res = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a browser automation expert."},
            {"role": "user", "content": prompt}
        ]
    )

    js_code = res.choices[0].message.content.strip().strip("```javascript").strip("```")
    return { "js_code": js_code }
