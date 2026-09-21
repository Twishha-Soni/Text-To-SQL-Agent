from langgraph.graph import END, START, StateGraph

from app.agent.sub_agent_1.state import SubGraphAgentState
from app.agent.sub_agent_1.nodes.retrieve import retrieve
from app.agent.sub_agent_1.nodes.generate import generate
from app.agent.sub_agent_1.nodes.validate import validate
from app.agent.sub_agent_1.nodes.execute import execute
from app.agent.sub_agent_1.nodes.correct import correct
from app.agent.sub_agent_1.nodes.clarify import clarify
from app.agent.sub_agent_1.nodes.explain import explain

from app.agent.sub_agent_1.routing import route_after_correct, route_after_execute, route_after_generate, route_after_validate


def build_sub_graph():
    workflow = StateGraph(SubGraphAgentState)

    # add nodes
    workflow.add_node('retrieve', retrieve)
    workflow.add_node('generate', generate)
    workflow.add_node('validate', validate)
    workflow.add_node('execute', execute)
    workflow.add_node('correct', correct)
    workflow.add_node('clarify', clarify)
    workflow.add_node('explain', explain)

    # set edges
    workflow.add_edge(START, 'retrieve')
    workflow.add_edge('retrieve', 'generate')

    workflow.add_conditional_edges(
        'generate', route_after_generate, {'validate': 'validate', 'clarify': 'clarify'}
    )
    workflow.add_conditional_edges(
        'validate', route_after_validate, {'execute': 'execute', 'correct': 'correct'}
    )
    workflow.add_conditional_edges(
        'execute', route_after_execute, {'explain': 'explain', 'correct': 'correct'}
    )
    workflow.add_conditional_edges(
        'correct', route_after_correct, {'validate': 'validate', 'clarify': 'clarify'}
    )

    workflow.add_edge('explain', END)
    workflow.add_edge('clarify', END)

    return workflow.compile()

sub_agent = build_sub_graph()