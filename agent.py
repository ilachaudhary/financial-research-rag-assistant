"""
Interactive agentic CLI over the 10-K RAG system, powered by Groq (free tier).

Usage:
    python agent.py
"""
import json
from groq import Groq

import config
from tools import TOOL_SCHEMAS, AVAILABLE_FUNCTIONS

SYSTEM_PROMPT = """You are a financial research analyst assistant with access to
the 10-K filings of Apple (AAPL), Tesla (TSLA), Nvidia (NVDA), and Microsoft (MSFT).

- Use the search_10k tool whenever you need facts from a filing. Never guess numbers.
- If comparing companies, call search_10k separately for each ticker.
- Always cite which company/year/section a fact came from.
- If the retrieved context doesn't answer the question, say so honestly.
"""


def run_agent():
    client = Groq(api_key=config.GROQ_API_KEY)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("10-K Research Agent (type 'exit' to quit)\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        messages.append({"role": "user", "content": user_input})

        # Agentic tool-use loop
        for _ in range(5):  # cap iterations to avoid infinite loops
            response = client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.2,
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append(msg)
                for call in msg.tool_calls:
                    fn_name = call.function.name
                    args = json.loads(call.function.arguments)
                    result = AVAILABLE_FUNCTIONS[fn_name](**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    })
                continue  # let the model see tool results and respond/continue
            else:
                print(f"\nAgent: {msg.content}\n")
                messages.append({"role": "assistant", "content": msg.content})
                break


if __name__ == "__main__":
    run_agent()
