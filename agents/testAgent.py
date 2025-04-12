from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType

def get_mind_tip(mood: str):
    return f"Try meditating or taking a walk. You said you're feeling {mood}."

tools = [
    Tool(name="MindTip", func=get_mind_tip, description="Provides mental health tips.")
]

llm = ChatOpenAI(temperature=0)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

print(agent.run("I'm feeling overwhelmed today."))
