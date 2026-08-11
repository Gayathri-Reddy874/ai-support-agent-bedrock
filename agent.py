import os
from dotenv import load_dotenv
import json

from tools import (
    create_ticket,
    get_faq_answer,
    detect_intent,
    send_email
)

load_dotenv()

MODEL_ID = os.getenv("MODEL_ID")

SYSTEM_PROMPT = (
    "You are a helpful, concise customer support assistant for an e-commerce company. "
    "Answer only the user's current question, using the recent conversation for context. "
    "Do not repeat earlier answers or list unrelated topics. Keep responses under 150 words."
)


# ------------------ PROMPT BUILDING ------------------
def build_prompt(user_input, history=None):
    """
    Builds a prompt that includes recent conversation turns so the LLM has
    short-term memory, instead of seeing only the latest message in isolation.
    `history` is a list of {"role": "You"/"Agent", "message": "..."} dicts,
    already trimmed to a reasonable window by the caller.
    """
    history = history or []

    convo_lines = []
    for turn in history:
        speaker = "User" if turn.get("role") == "You" else "Assistant"
        convo_lines.append(f"{speaker}: {turn.get('message', '')}")
    convo_text = "\n".join(convo_lines)

    if convo_text:
        return f"{SYSTEM_PROMPT}\n\n{convo_text}\nUser: {user_input}\nAssistant:"
    return f"{SYSTEM_PROMPT}\n\nUser: {user_input}\nAssistant:"


# ------------------ BEDROCK CALL ------------------
def invoke_bedrock(client, prompt):
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 300,
        "temperature": 0.5
    })

    try:
        response = client.invoke_model(
            modelId=MODEL_ID,
            body=body
        )

        result = json.loads(response['body'].read())

        if "generation" in result:
            return result["generation"]

        elif "outputs" in result:
            return result["outputs"][0]["text"]

        else:
            return "⚠️ Unexpected response format"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ------------------ MAIN AGENT ------------------
def agent_response(client, user_input, history=None):
    """
    Routing order (fixed):
      1. Intent detection first — EMAIL / TICKET keywords take priority so a
         message like "Send an email regarding refund" is routed to the email
         handler instead of being swallowed by the refund FAQ.
      2. FAQ — fast keyword answers for anything not already routed above.
      3. LLM fallback — only for genuinely open-ended queries, now with
         recent conversation history included for context.
    """

    # ✅ Step 1: Intent detection (email / ticket routing takes priority)
    intent = detect_intent(user_input)

    if intent == "EMAIL":
        return send_email(user_input)

    if intent == "TICKET":
        return create_ticket(user_input)

    # ✅ Step 2: FAQ (fast + free) — only reached for non-email/ticket queries
    faq = get_faq_answer(user_input)
    if faq:
        return faq

    # ✅ Step 3: LLM fallback, now with short-term conversation memory
    prompt = build_prompt(user_input, history)
    final_response = invoke_bedrock(client, prompt)

    if not final_response or final_response.strip() == "":
        return "⚠️ No response generated"

    return final_response
