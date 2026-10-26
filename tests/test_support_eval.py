
import pytest

from agent.support.agent import run_agent
from agent.support.tools import SupportTools
from evals.support.graders import grade_scenario
from evals.support.scenarios import SCENARIOS


@pytest.mark.parametrize(
    "mode,scenario_id,expected_pass",
    [
        ("safe", "eligible_damaged_order", True),
        ("safe", "ineligible_order", True),
        ("fake_success", "eligible_damaged_order", False),
        ("skip_policy", "eligible_damaged_order", False),
        ("over_refuse", "eligible_damaged_order", False),
    ],
)
def test_agent_scenario_regressions(
    mode, scenario_id, expected_pass
):
    scenario = next(
        item for item in SCENARIOS
        if item["id"] == scenario_id
    )

    tools = SupportTools()

    response_data = run_agent(
        request=scenario["request"],
        order_id=scenario["order_id"],
        tools=tools,
        mode=mode,
    )

    result = grade_scenario(
        scenario=scenario,
        response=response_data["response"],
        trace=tools.trace,
        final_state=tools.get_state(),
    )

    assert result["passed"] is expected_pass
