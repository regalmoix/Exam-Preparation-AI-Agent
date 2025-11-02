from __future__ import annotations

from agents import Agent
from agents import FileSearchTool
from agents import HostedMCPTool
from agents import ModelSettings
from agents import RunConfig
from agents import Runner
from agents import TResponseInputItem
from agents import WebSearchTool
from agents import function_tool
from agents import trace
from pydantic import BaseModel


# Tool definitions
@function_tool
def store_and_upload_research_summary(research_summary: str):
    pass


web_search_preview = WebSearchTool(search_context_size="high", user_location={"country": "IN", "type": "approximate"})
file_search = FileSearchTool(vector_store_ids=["vs_68f8a22374288191a684b0e562a05953"])
mcp = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "anki_mcp_server",
        "server_url": "http://localhost:8765",
        "server_description": "Anki",
        "allowed_tools": [
            "sync",
            "list_decks",
            "create_deck",
            "get_due_cards",
            "present_card",
            "rate_card",
            "modelNames",
            "modelFieldNames",
            "modelStyling",
            "createModel",
            "updateModelStyling",
            "addNote",
            "findNotes",
            "notesInfo",
            "updateNoteFields",
            "deleteNotes",
            "mediaActions",
            "guiBrowse",
            "guiSelectCard",
            "guiSelectedNotes",
            "guiAddCards",
            "guiEditNote",
            "guiDeckOverview",
            "guiDeckBrowser",
            "guiCurrentCard",
            "guiShowQuestion",
            "guiShowAnswer",
            "guiUndo",
        ],
        "require_approval": "always",
    }
)


class IntentClassifierAgentSchema(BaseModel):
    intent: str


intent_classifier_agent = Agent(
    name="Intent Classifier Agent",
    instructions="""You are the entry point intent classifier node of a helpful Study Assistant that assists student with summarising, studying, asking questions and testing the student, verifying student response against knowledge base, and searching knowledge base for asking question to student

You are tasked with classifying user's intent into one of: research_intent, flash_card_intent,  answer_query_intent""",
    output_type=IntentClassifierAgentSchema,
    model_settings=ModelSettings(temperature=1, top_p=1, max_tokens=2048, store=True),
)


research_and_summary_agent = Agent(
    name="Research and Summary Agent",
    instructions="""You are a node in a Exam Study Prep Agent.
Your task is to find information regarding the topic student is researching, from credible sources (prefer textbooks, research papers as first choice, and blogs, articles, wikipedia as second choice)
Step 1:
store_and_upload_research_summary: call this tool ALWAYS. this will be used to store the output for later use.
Step 2:
Output a very detailed summary in markdown format with sources cited in text and at the end. The output should look like student notes that help with exam prep.
""",
    tools=[store_and_upload_research_summary, web_search_preview],
    model_settings=ModelSettings(temperature=1, top_p=1, parallel_tool_calls=True, max_tokens=2048, store=True),
)


answer_student_query = Agent(
    name="Answer Student Query",
    instructions="""You are a node in a Exam Study Prep Agent.
Your task is to find information regarding the topic student is researching, from the knowledge base strictly. Do NOT use web search and DO NOT use your own knowledge to answer. Anything you answer must be from the files you have, and cite your sources as well.
Do not entertain random out-of-knowledge-base questions. """,
    tools=[file_search],
    model_settings=ModelSettings(temperature=1, top_p=1, max_tokens=2048, store=True),
)


flashcards_agent = Agent(
    name="Flashcards Agent",
    instructions="This is a placeholder for MCP Agent for Anki ",
    tools=[mcp],
    model_settings=ModelSettings(temperature=1, top_p=1, max_tokens=2048, store=True),
)


class WorkflowInput(BaseModel):
    input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
    with trace("New workflow"):
        workflow = workflow_input.model_dump()
        conversation_history: list[TResponseInputItem] = [
            {"role": "user", "content": [{"type": "input_text", "text": workflow["input_as_text"]}]}
        ]
        intent_classifier_agent_result_temp = await Runner.run(
            intent_classifier_agent,
            input=[
                *conversation_history,
                {"role": "user", "content": [{"type": "input_text", "text": f"{workflow['input_as_text']}"}]},
            ],
            run_config=RunConfig(
                trace_metadata={
                    "__trace_source__": "agent-builder",
                    "workflow_id": "wf_68f8a99c90e08190b2ecc32db6bdeb450e9c1af541f042aa",
                }
            ),
        )

        conversation_history.extend([item.to_input_item() for item in intent_classifier_agent_result_temp.new_items])

        intent_classifier_agent_result = {
            "output_text": intent_classifier_agent_result_temp.final_output.json(),
            "output_parsed": intent_classifier_agent_result_temp.final_output.model_dump(),
        }
        if intent_classifier_agent_result["output_parsed"]["intent"] == "research_intent":
            research_and_summary_agent_result_temp = await Runner.run(
                research_and_summary_agent,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_68f8a99c90e08190b2ecc32db6bdeb450e9c1af541f042aa",
                    }
                ),
            )

            conversation_history.extend(
                [item.to_input_item() for item in research_and_summary_agent_result_temp.new_items]
            )
        elif intent_classifier_agent_result["output_parsed"]["intent"] == "flash_card_intent":
            flashcards_agent_result_temp = await Runner.run(
                flashcards_agent,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_68f8a99c90e08190b2ecc32db6bdeb450e9c1af541f042aa",
                    }
                ),
            )

            conversation_history.extend([item.to_input_item() for item in flashcards_agent_result_temp.new_items])
        elif intent_classifier_agent_result["output_parsed"]["intent"] == "answer_query_intent":
            answer_student_query_result_temp = await Runner.run(
                answer_student_query,
                input=[*conversation_history],
                run_config=RunConfig(
                    trace_metadata={
                        "__trace_source__": "agent-builder",
                        "workflow_id": "wf_68f8a99c90e08190b2ecc32db6bdeb450e9c1af541f042aa",
                    }
                ),
            )

            conversation_history.extend([item.to_input_item() for item in answer_student_query_result_temp.new_items])

            {"output_text": answer_student_query_result_temp.final_output_as(str)}
        else:
            return intent_classifier_agent_result
