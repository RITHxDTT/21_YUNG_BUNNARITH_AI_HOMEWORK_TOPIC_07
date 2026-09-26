from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from harness import AgentHarness
from database.schemas import UserRole
from llm_tools import TOOLS


# =========================================================
# Configuration
# =========================================================

MODEL_NAME = "llama3.2:3b"
MAX_ITERATIONS = 5
MAX_TOOL_CALLS = 5


# =========================================================
# System Prompt
# =========================================================

SYSTEM_PROMPT = """
You are a simple shopping assistant.

You can use these tools:

1. search_products_tool
   Search products by product name or category.

2. check_stock_tool
   Check the current stock of a product.

3. delete_product_tool
   Delete a product from the system.
   This is a destructive action.

Rules:

- Use tools when product information is required.
- Never invent product information.
- Never invent stock information.
- Never claim that a product was deleted unless the tool confirms it.
- Read every tool result carefully.
- After receiving a tool result, decide whether another tool is needed.
- If the user's goal is satisfied, give the final answer.
- Do not repeatedly call tools when you already have enough information.
"""


# =========================================================
# LLM
# =========================================================

model = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
)

bound_model = model.bind_tools(TOOLS)


# =========================================================
# Agent State
# =========================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    iteration: int
    tool_call_count: int
    user_role: str


# =========================================================
# Agent Node
# =========================================================

def agent_node(state: AgentState):

    print("\n[AGENT] Thinking...")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = bound_model.invoke(messages)

    new_iteration = state["iteration"] + 1

    if response.tool_calls:

        tool_call = response.tool_calls[0]

        print(
            f"[AGENT] Requested tool: "
            f"{tool_call['name']}"
        )

        print(
            f"[AGENT] Arguments: "
            f"{tool_call['args']}"
        )

    else:
        print("[AGENT] Final answer generated.")

    return {
        "messages": [response],
        "iteration": new_iteration,
    }


# =========================================================
# Routing
# =========================================================

def route_after_agent(state: AgentState):

    if state["iteration"] >= MAX_ITERATIONS:
        print("\n[SAFETY] Maximum iterations reached.")
        return END

    last_message = state["messages"][-1]

    if (
        isinstance(last_message, AIMessage)
        and last_message.tool_calls
    ):
        return "execute_tool"

    return END


# =========================================================
# Tool Name Mapping
# =========================================================

TOOL_NAME_MAP = {
    "search_products_tool": "search_products",
    "check_stock_tool": "check_stock",
    "delete_product_tool": "delete_product",
}


# =========================================================
# Execute Tool Node
# =========================================================

def execute_tool_node(state: AgentState):

    last_message = state["messages"][-1]

    if not isinstance(last_message, AIMessage):
        return {}

    if not last_message.tool_calls:
        return {}

    # Execute one tool call per iteration
    tool_call = last_message.tool_calls[0]

    llm_tool_name = tool_call["name"]
    arguments = tool_call["args"]
    tool_call_id = tool_call["id"]

    print("\n[HARNESS] Received tool request.")
    print(f"[HARNESS] Tool: {llm_tool_name}")
    print(f"[HARNESS] Arguments: {arguments}")

    # Convert LLM tool name to internal tool name
    internal_tool_name = TOOL_NAME_MAP.get(llm_tool_name)

    # =====================================================
    # Unknown Tool
    # =====================================================

    if internal_tool_name is None:

        result = {
            "success": False,
            "error": f"Unknown tool: {llm_tool_name}",
        }

    else:

        role = UserRole(state["user_role"])

        harness = AgentHarness(
            user_role=role,
            max_tool_calls=MAX_TOOL_CALLS,
        )

        harness.tool_call_count = state["tool_call_count"]

        # =================================================
        # Get Tool Risk
        # =================================================

        risk = harness.get_risk(internal_tool_name)

        print(
            f"[HARNESS] Risk: "
            f"{risk.value if risk else 'UNKNOWN'}"
        )

        # =================================================
        # Validate Before Execution
        # =================================================

        validation = harness.validate(
            internal_tool_name,
            arguments,
        )

        if not validation["success"]:

            print(
                "[HARNESS] Validation or permission failed."
            )

            result = validation

        # =================================================
        # WRITE / DESTRUCTIVE → HITL
        # =================================================

        elif harness.needs_approval(internal_tool_name):

            print(
                "[HARNESS] Human approval required."
            )

            approval = interrupt(
                {
                    "type": "approval_required",
                    "tool": internal_tool_name,
                    "risk": risk.value,
                    "arguments": arguments,
                    "message": (
                        f"Tool '{internal_tool_name}' "
                        f"is classified as {risk.value}."
                    ),
                }
            )

            # Human approved
            if approval is True:

                print(
                    "[HITL] Human APPROVED action."
                )

                result = harness.execute(
                    tool_name=internal_tool_name,
                    arguments=arguments,
                )

            # Human rejected
            else:

                print(
                    "[HITL] Human REJECTED action."
                )

                result = {
                    "success": False,
                    "tool": internal_tool_name,
                    "risk": risk.value,
                    "error": "Operation rejected by human.",
                }

        # =================================================
        # READ_ONLY → Execute Directly
        # =================================================

        else:

            print(
                "[HARNESS] Approval not required."
            )

            result = harness.execute(
                tool_name=internal_tool_name,
                arguments=arguments,
            )

    print(f"[HARNESS] Result: {result}")

    tool_message = ToolMessage(
        content=str(result),
        tool_call_id=tool_call_id,
    )

    return {
        "messages": [tool_message],
        "tool_call_count": state["tool_call_count"] + 1,
    }
# =========================================================
# Build LangGraph
# =========================================================

builder = StateGraph(AgentState)

builder.add_node(
    "agent",
    agent_node,
)

builder.add_node(
    "execute_tool",
    execute_tool_node,
)


# START → Agent

builder.add_edge(
    START,
    "agent",
)


# Agent → Tool OR END

builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "execute_tool": "execute_tool",
        END: END,
    },
)


# Tool Result → Agent Again

builder.add_edge(
    "execute_tool",
    "agent",
)


# Compile Graph


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


# =========================================================
# Run Agent
# =========================================================

def run_agent(
    user_request: str,
    user_role: UserRole = UserRole.CUSTOMER,
):

    config = {
        "configurable": {
            "thread_id": "shopping-agent-session"
        }
    }

    initial_state = {
        "messages": [
            HumanMessage(content=user_request)
        ],
        "iteration": 0,
        "tool_call_count": 0,
        "user_role": user_role.value,
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    # -----------------------------------------------------
    # Check for Human Approval
    # -----------------------------------------------------

    while "__interrupt__" in result:

        interrupts = result["__interrupt__"]

        if not interrupts:
            break

        interrupt_data = interrupts[0].value

        print("\n" + "=" * 60)
        print("HUMAN APPROVAL REQUIRED")
        print("=" * 60)

        print(
            f"Tool: "
            f"{interrupt_data.get('tool')}"
        )

        print(
            f"Arguments: "
            f"{interrupt_data.get('arguments')}"
        )

        print(
            f"Warning: "
            f"{interrupt_data.get('message')}"
        )

        answer = input(
            "\nApprove this action? (yes/no): "
        ).strip().lower()

        approved = answer in [
            "yes",
            "y",
        ]

        result = graph.invoke(
            Command(resume=approved),
            config=config,
        )

    # -----------------------------------------------------
    # Final Answer
    # -----------------------------------------------------

    final_message = result["messages"][-1]

    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)

    print(final_message.content)

    return result

    initial_state = {
        "messages": [
            HumanMessage(content=user_request)
        ],
        "iteration": 0,
        "tool_call_count": 0,
        "user_role": user_role.value,
    }

    result = graph.invoke(initial_state)

    final_message = result["messages"][-1]

    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)

    print(final_message.content)

    return result