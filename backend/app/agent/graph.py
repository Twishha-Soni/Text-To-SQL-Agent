from langgraph.graph import END, START, StateGraph

from app.agent.nodes.head import head
from app.agent.nodes.sub_agent import sub_agent_node
from app.agent.state import AgentState


def build_graph():
    workflow = StateGraph(AgentState)

    # add nodes
    workflow.add_node("head", head)
    workflow.add_node("sub_agent_node", sub_agent_node)

    # set edges
    workflow.add_edge(START, "head")
    workflow.add_edge("head", "sub_agent_node")
    workflow.add_edge("sub_agent_node", END)

    return workflow.compile()


agent = build_graph()