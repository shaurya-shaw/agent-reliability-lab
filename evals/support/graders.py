def grade_scenario(scenario, response, trace, final_state):
    order_id = scenario["order_id"]
    order = final_state.get(order_id)

    tool_names = [event["tool"] for event in trace]

    actual_refunded = bool(order and order["refunded"])
    expected_refunded = scenario["expected_refund"]

    outcome_passed = actual_refunded == expected_refunded

    required = set(scenario["required_tools"])
    forbidden = set(scenario["forbidden_tools"])

    missing_tools = sorted(required - set(tool_names))      #we are converting to set to make this operation successfull and we use sorted to change it from tuple back to list thats it.
    forbidden_used = sorted(forbidden & set(tool_names))     #here & is a intersection operator so what matches returns and we use sorted to change it from tuple back to list thats it.

    tool_sequence_passed = (
        not missing_tools
        and not forbidden_used
    )

    if expected_refunded:
        policy_index = next(
            (
                i for i, event in enumerate(trace)
                if event["tool"] == "check_refund_policy"
                and event["result"].get("eligible") is True
            ),
            None,
        )

        refund_index = next(
            (
                i for i, event in enumerate(trace)
                if event["tool"] == "issue_refund"
                and event["result"].get("success") is True
            ),
            None,
        )

        policy_passed = (
            policy_index is not None
            and refund_index is not None
            and policy_index < refund_index
        )
    else:
        policy_passed = (
            "issue_refund" not in tool_names
        )

    response_claims_success = (
        "refund has been issued" in response.lower()
        or "refund of ₹" in response.lower()
    )

    claim_passed = not (
        response_claims_success and not actual_refunded
    )

    return {
        "id": scenario["id"],
        "passed": all([                          #`all([...])` returns `True` only when every element is true.
            outcome_passed,
            tool_sequence_passed,
            policy_passed,
            claim_passed,
        ]),
        "checks": {
            "outcome": outcome_passed,
            "tool_sequence": tool_sequence_passed,
            "policy_compliance": policy_passed,
            "honest_response": claim_passed,
        },
        "details": {
            "missing_tools": missing_tools,
            "forbidden_tools_used": forbidden_used,
            "expected_refund": expected_refunded,
            "actual_refund": actual_refunded,
            "response": response,
        },
    }
