from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

def load_model():
    google_api_key = os.getenv('GOOGLE_API_KEY')
    base_url = os.getenv('GOOGLE_BASE_URL')
    gemini = OpenAI(api_key=google_api_key, base_url=base_url)
    model_name = "gemini-2.5-flash"
    return gemini, model_name

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


class Me:

    def __init__(self):
        val  = load_model()
        self.openai = val[0]
        self.modelname = val[1]
        self.name = "Abhishek Saxena"
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(model=self.modelname, messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    # Build a small Gradio Blocks chat UI that adapts Gradio's (user,bot)
    # history tuples into the message format expected by `Me.chat`.
    def gradio_history_to_messages(chat_history):
        """Normalize Gradio chat history into a list of message dicts:
        - Accepts chat_history as list of tuples [(user, bot), ...] (older style)
        - Or as list of message dicts [{'role':..., 'content':...}, ...] (new style)
        Returns list of dicts with 'role' and 'content'.
        """
        messages = []
        if not chat_history:
            return messages
        # If history already in message-dict format
        if isinstance(chat_history, list) and len(chat_history) > 0 and isinstance(chat_history[0], dict):
            # assume it's already [{'role':..,'content':...}, ...]
            return chat_history

        # Otherwise assume list of pairs/tuples: (user_msg, bot_msg)
        for pair in chat_history:
            try:
                user_msg, bot_msg = pair if len(pair) >= 2 else (pair[0], None)
            except Exception:
                # Fallback: if it's a single string, treat as user message
                if isinstance(pair, str):
                    messages.append({"role": "user", "content": pair})
                    continue
                continue
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if bot_msg:
                messages.append({"role": "assistant", "content": bot_msg})
        return messages

    def submit_fn(message, chat_history):
        # Normalize incoming chat_history into message dicts for the model
        history_msgs = gradio_history_to_messages(chat_history)
        reply = me.chat(message, history_msgs)
        # Build new history in Gradio "messages" format (list of dicts)
        new_history = history_msgs[:] if history_msgs else []
        new_history.append({"role": "user", "content": message})
        new_history.append({"role": "assistant", "content": reply})
        # Return the messages list (what Gradio expects) and clear the textbox
        return new_history, ""

    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        txt = gr.Textbox(placeholder="Type a message and press enter")
        txt.submit(submit_fn, inputs=[txt, chatbot], outputs=[chatbot, txt])

    demo.launch()
    