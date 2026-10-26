from dotenv import load_dotenv
load_dotenv()
import json
import os
from google import genai
from google.genai import types
from agent.support.tools import SupportTools

SYSTEM_INSTRUCTION = """
You are a customer-support agent.

Rules:
1. Look up the order before making decisions.
2. Check the refund policy before attempting a refund.
3. Never claim a refund succeeded unless the refund tool confirms it.
4. Never invent order information or tool results.
5. Explain refusals clearly and politely.
6. Use only the supplied tools for order operations.
7. Do not attempt to bypass the refund policy.
"""

TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="lookup_order",
        description="Look up an order by its order ID.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"],
        },
    ),
    types.FunctionDeclaration(
        name="check_refund_policy",
        description="Check whether an order qualifies for a refund.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"],
        },
    ),
    types.FunctionDeclaration(
        name="issue_refund",
        description="Issue an eligible refund for the exact approved amount.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "integer"},
            },
            "required": ["order_id", "amount"],
        },
    ),
]

TOOL = types.Tool(function_declarations=TOOL_DECLARATIONS)


def run_gemini_agent(
    request: str,
    order_id: str,
    tools: SupportTools,
    model: str = "gemini-3.8-flash",
    max_tool_rounds: int = 8,
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Set it in your environment."
        )

    client = genai.Client(api_key=api_key)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=(
                        f"Customer request: {request}\n"
                        f"Order ID: {order_id}"
                    )
                )
            ],
        )
    ]

    # Only these known Python functions may be executed.
    tool_functions = {
        "lookup_order": tools.lookup_order,
        "check_refund_policy": tools.check_refund_policy,
        "issue_refund": tools.issue_refund,
    }

    for _ in range(max_tool_rounds):
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[TOOL],
                temperature=0,
            ),
        )

        if not response.candidates:
            raise RuntimeError("Gemini returned no candidates.")

        candidate = response.candidates[0]
        contents.append(candidate.content)

        function_calls = [
            part.function_call
            for part in (candidate.content.parts or [])
            if part.function_call is not None
        ]

        if not function_calls:
            text = response.text
            if not text:
                raise RuntimeError(
                    "Gemini returned neither a tool call nor text."
                )
            return {"response": text}

        tool_results = []

        for call in function_calls:
            name = call.name
            args = dict(call.args or {})

            function = tool_functions.get(name)
            if function is None:
                result = {
                    "error": f"Tool not permitted: {name}"
                }
            else:
                try:
                    # Require the model to use the scenario's order.
                    if args.get("order_id") != order_id:
                        result = {
                            "error": "Order ID does not match this request."
                        }
                    else:
                        result = function(**args)
                except (TypeError, ValueError, KeyError) as exc:
                    result = {
                        "error": f"Invalid tool arguments: {exc}"
                    }

            tool_results.append(
                types.Part.from_function_response(
                    name=name,
                    response={"result": result},
                )
            )

        contents.append(
            types.Content(
                role="tool",
                parts=tool_results,
            )
        )

    raise RuntimeError(
        f"Gemini exceeded {max_tool_rounds} tool rounds."
    )
