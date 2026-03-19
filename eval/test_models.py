"""Quick test: which models are alive on Azure Foundry?"""
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

MODELS = ["claude-haiku-4-5", "Phi-4", "gpt-5-nano", "gpt-5-mini"]

async def test_model(client, model):
    msg = [{"role": "user", "content": "Say TRUE or FALSE: does x*y=y*x imply x=x?"}]
    # Try max_completion_tokens first (reasoning models)
    try:
        resp = await client.chat.completions.create(
            model=model, messages=msg, max_completion_tokens=512,
        )
        print(f"  {model}: OK (reasoning) -> {resp.choices[0].message.content[:80]!r}")
        return True
    except Exception:
        pass
    # Try max_tokens (non-reasoning models)
    try:
        resp = await client.chat.completions.create(
            model=model, messages=msg, max_tokens=512,
        )
        print(f"  {model}: OK (standard) -> {resp.choices[0].message.content[:80]!r}")
        return True
    except Exception as e:
        print(f"  {model}: FAIL -> {e!r}")
        return False

async def main():
    client = AsyncOpenAI(
        base_url=os.getenv("AZURE_FOUNDRY_BASE_URL"),
        api_key=os.getenv("AZURE_INFERENCE_CREDENTIAL"),
    )
    print("Testing models...")
    for m in MODELS:
        await test_model(client, m)

if __name__ == "__main__":
    asyncio.run(main())
