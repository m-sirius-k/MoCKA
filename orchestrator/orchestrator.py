# -*- coding: utf-8 -*-

"""MoCKA Orchestrator Core"""


from .intent_parser import parse_intent
from .task_planner import plan_tasks
from .agent_router import route_task
from .context_injector import inject_context
from .task_executor import execute_task
from .task_executor import execute_task


def execute(request: str) -> dict:
    intent = parse_intent(request)

    plan = plan_tasks(intent)

    routed_tasks = []
    previous_result = {}
    for task in plan["tasks"]:

        route = route_task(task)
        context = inject_context(task)
        context["test_output"] = previous_result.get("stdout", "")
        result = execute_task(task, context)

        routed_tasks.append({
            "task": task,
            "route": route,
            "context": context,
            "result": result,
        })

        previous_result = result
    return {
        "request": request,
        "intent": intent,
        "plan": plan,
        "execution_plan": routed_tasks,
    }
