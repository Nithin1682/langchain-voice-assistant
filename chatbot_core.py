# chatbot_core.py
import os, getpass
from datetime import datetime
import timetable_tool
import pyperclip

from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, BaseMessage, trim_messages
)
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing import Sequence
from typing_extensions import Annotated, TypedDict

# 1. API key
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")

# 2. Initialize the LLM for text tasks
model = init_chat_model("gemma2-9b-it", model_provider="groq")

# 3. Prompt template with markdown timetable
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Reply in {language}."),
    ("system", "Here is the user's weekly timetable in markdown format:\n\n{timetable_md}"),
    ("system", "Today is {today}. Current date/time: {datetime} (24-hour)."),
    MessagesPlaceholder(variable_name="messages"),
])

# 4. Trimmer
trimmer = trim_messages(
    max_tokens=1024,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str

workflow = StateGraph(state_schema=State)

def call_model(state: State):
    last = state["messages"][-1]
    tid = state.get("configurable", {}).get("thread_id", "default")

    if isinstance(last, HumanMessage):
        intent = detect_intent(last.content)
        if intent == "save my timetable":
            return {"messages": [AIMessage(content=timetable_tool.save_timetable_image())]}
        if intent == "delete my timetable":
            out = timetable_tool.delete_timetable()
            memory.delete_thread(tid)
            return {"messages": [AIMessage(content=out)]}
        if intent == "check_grammar":
            text = pyperclip.paste().strip()
            result = check_grammar(text)
            return {"messages": [AIMessage(content=result)]}
        if intent == "suggest_emoji":
            text = pyperclip.paste().strip()
            result = suggest_emoji(text)
            return {"messages": [AIMessage(content=result)]}
        # Else, fallback to general model handling

    # fallback: inject markdown
    trimmed = trimmer.invoke(state["messages"])
    timetable_md = timetable_tool.load_timetable_json(raw=False)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_name = datetime.now().strftime("%A")

    prompt = prompt_template.invoke({
        "timetable_md": timetable_md,
        "datetime": now_str,
        "today": today_name,
        "language": state.get("language", "English"),
        "messages": trimmed
    })
    resp = model.invoke(prompt)
    return {"messages": [resp]}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# inject initial date/time

def enrich_with_datetime(thread_id: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.invoke(
        {"messages": [SystemMessage(content=f"Current date/time: {now}")]},
        {"configurable": {"thread_id": thread_id}}
    )

# plain-chat

def plain_chat(thread_id: str):
    enrich_with_datetime(thread_id)
    print(f"Starting chat session: {thread_id} (type 'exit' to quit)\n")
    cfg = {"configurable": {"thread_id": thread_id}}
    while True:
        ui = input("You: ").strip()
        if ui.lower() == "exit":
            break
        out = app.invoke({"messages": [HumanMessage(content=ui)]}, cfg)
        print("Assistant:", out["messages"][-1].content, "\n")

# intent & utilities unchanged

def detect_intent(user_input: str) -> str:
    prompt = [
        SystemMessage(content="""You are an intent classifier.

Given a user input, respond with the most appropriate intent from this list:
- save my timetable
- delete my timetable
- check_grammar
- suggest_emoji
- none

Your response should be only one word: the intent itself. If you're not sure, respond with 'none'."""),
        HumanMessage(content=f"Input: {user_input}\nIntent:")
    ]
    result = model.invoke(prompt).content.strip().lower()
    return result if result in {"save my timetable", "delete my timetable", "check_grammar", "suggest_emoji"} else "none"



def check_grammar(text: str) -> str:
    prompt = [
        SystemMessage(content="You are a grammar correction assistant. If errors, return corrected sentence; else return the same."),
        HumanMessage(content=text)
    ]
    return model.invoke(prompt).content.strip()


def suggest_emoji(sentence: str) -> str:
    prompt = [
        SystemMessage(content="You are an emoji suggester. Respond with one or two emojis only."),
        HumanMessage(content=sentence)
    ]
    return model.invoke(prompt).content.strip()

if __name__ == "__main__":
    session = input("Enter thread ID (e.g., 'default'): ")
    plain_chat(session)