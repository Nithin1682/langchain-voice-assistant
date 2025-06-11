import os, getpass
from datetime import datetime
import timetable_tool

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

# 2. Initialize the LLM
model = init_chat_model("gemma2-9b-it", model_provider="groq")

# 3. Prompt template with full-timetable injection
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the provided timetable to answer questions about classes. Reply in {language}."),
    ("system", "Here is the user's weekly timetable in markdown format. All times are in 24-hour format:\n\n{timetable_md}"),
    ("system", "Today is {today}. Current date/time is {datetime} (24-hour format)."),
    MessagesPlaceholder(variable_name="messages"),
])

# 4. Trimmer to keep under token limit
trimmer = trim_messages(
    max_tokens=1024,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# 5. State schema
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str

# 6. Build workflow
workflow = StateGraph(state_schema=State)

def call_model(state: State):
    last = state["messages"][-1]
    thread_id = state.get("configurable", {}).get("thread_id", "default")

    if isinstance(last, HumanMessage):
        user_input = last.content
        intent = detect_intent(user_input)

        if intent == "save_timetable":
            result = timetable_tool.save_timetable_gui()
            return {"messages": [AIMessage(content=result)]}

        if intent == "delete_timetable":
            result = timetable_tool.delete_timetable()
            memory.delete_thread(thread_id)
            return {"messages": [AIMessage(content=result)]}

    # LLM fallback
    trimmed       = trimmer.invoke(state["messages"])
    timetable_md  = timetable_tool.get_timetable_markdown()
    now_str       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_name    = datetime.now().strftime("%A")

    prompt = prompt_template.invoke({
        "timetable_md": timetable_md,
        "datetime":     now_str,
        "today":        today_name,
        "language":     state.get("language", "English"),
        "messages":     trimmed,
    })
    response = model.invoke(prompt)
    return {"messages": [response]}



workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# 7. Compile with memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 8. Inject initial date/time

def enrich_with_datetime(thread_id: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = SystemMessage(content=f"Current date/time: {now}")
    app.invoke({"messages": [msg]}, {"configurable": {"thread_id": thread_id}})

# 9. Plain‐text chat

def plain_chat(thread_id: str):
    enrich_with_datetime(thread_id)
    print(f"Starting chat session: {thread_id} (type 'exit' to quit)\n")
    cfg = {"configurable": {"thread_id": thread_id}}
    while True:
        ui = input("You: ").strip()
        if ui.lower() == "exit":
            break
        human_msg = HumanMessage(content=ui)
        out = app.invoke({"messages": [human_msg]}, cfg)
        print("Assistant:", out["messages"][-1].content, "\n")

def detect_intent(user_input: str) -> str:
    intent_prompt = [
        SystemMessage(content="You are an intent classifier. Given a user input, return only one of the following intents: save_timetable, delete_timetable, check_grammar,suggest_emoji, none."),
        HumanMessage(content=f"Input: {user_input}\nIntent:")
    ]
    response = model.invoke(intent_prompt)
    return response.content.strip().lower()

def check_grammar(text: str) -> str:
    grammar_prompt = [
        SystemMessage(content="You are a grammar correction assistant. If the sentence has grammar mistakes, return a corrected version. If it's already correct, return the same sentence."),
        HumanMessage(content=text)
    ]
    response = model.invoke(grammar_prompt)
    return response.content.strip()

def suggest_emoji(sentence: str) -> str:
    prompt = [
        SystemMessage(content="You are an emoji suggester. Given a user sentence, reply with one or two emojis that best express its meaning or emotion. Do not include any other text."),
        HumanMessage(content=sentence)
    ]
    response = model.invoke(prompt)
    return response.content.strip()



if __name__ == "__main__":
    session = input("Enter thread ID (e.g., 'default'): ")
    plain_chat(session)