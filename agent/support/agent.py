from agent.support.tools import SupportTools

def run_agent(
    request: str,
    order_id: str,
    tools: SupportTools,
    mode: str = "safe",
):
    """
    Run a customer-support agent.

    Modes other than 'safe' deliberately simulate common agent failures.
    They let us verify that the evaluation harness catches those failures.
    """

    if mode == "fake_success":
        return {
            "response": f"Your refund for {order_id} has been issued.",
        }

    order_result = tools.lookup_order(order_id)

    if not order_result["found"]:
        return {"response": "I couldn't find that order."}

    if mode == "over_refuse":
        return {
            "response": "Sorry, I cannot issue refunds.",
        }

    if mode != "skip_policy":
        policy = tools.check_refund_policy(order_id)

        if not policy["eligible"]:
            return {
                "response": (
                    f"I cannot issue this refund: {policy['reason']}."
                ),
            }

    # Deliberate bug: this mode attempts a refund without checking policy.
    order = order_result["order"]
    refund = tools.issue_refund(order_id, order["amount"])

    if refund["success"]:
        return {
            "response": (
                f"Your refund of ₹{refund['amount']} has been issued."
            ),
        }

    return {
        "response": f"The refund could not be issued: {refund['reason']}.",
    }