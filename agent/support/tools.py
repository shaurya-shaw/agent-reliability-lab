from copy import deepcopy

INITIAL_ORDERS = {
    "ORD-101": {
        "order_id": "ORD-101",
        "customer_id": "CUST-1",
        "amount": 5000,
        "status": "delivered",
        "damaged": True,
        "refundable": True,
        "refunded": False,
    },
    "ORD-102": {
        "order_id": "ORD-102",
        "customer_id": "CUST-2",
        "amount": 2500,
        "status": "delivered",
        "damaged": False,
        "refundable": False,
        "refunded": False,
    },
}


class SupportTools:
    def __init__(self):
        self.orders = deepcopy(INITIAL_ORDERS)
        self.trace = []

    def _record(self, tool, arguments, result):
        self.trace.append({
            "tool": tool,
            "arguments": deepcopy(arguments),
            "result": deepcopy(result),
        })
        return result

    def lookup_order(self, order_id):
        order = self.orders.get(order_id)

        result = (
            {"found": True, "order": deepcopy(order)}
            if order
            else {"found": False, "order": None}
        )

        return self._record(
            "lookup_order",
            {"order_id": order_id},
            result,
        )

    def check_refund_policy(self, order_id):
        order = self.orders.get(order_id)

        if order is None:
            result = {"eligible": False, "reason": "Order not found"}
        elif order["refunded"]:
            result = {"eligible": False, "reason": "Already refunded"}
        elif not order["refundable"]:
            result = {"eligible": False, "reason": "Policy does not allow refund"}
        else:
            result = {
                "eligible": True,
                "refund_amount": order["amount"],
                "reason": "Order qualifies for a refund",
            }

        return self._record(
            "check_refund_policy",
            {"order_id": order_id},
            result,
        )

    def issue_refund(self, order_id, amount):
        order = self.orders.get(order_id)

        if order is None:
            result = {"success": False, "reason": "Order not found"}
        elif order["refunded"]:
            result = {"success": False, "reason": "Already refunded"}
        elif not order["refundable"] or amount != order["amount"]:
            result = {"success": False, "reason": "Refund rejected"}
        else:
            order["refunded"] = True
            result = {
                "success": True,
                "order_id": order_id,
                "amount": amount,
            }

        return self._record(
            "issue_refund",
            {"order_id": order_id, "amount": amount},
            result,
        )

    def get_state(self):
        """Independent view of the system after execution."""
        return deepcopy(self.orders)
