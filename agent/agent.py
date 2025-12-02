from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.network_tools import get_firewall_rules, install_firewall_rule, get_network_status
from tools.threat_tools import check_ip_reputation
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# OR for Claude:
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)

# Define tools
tools = [
    get_firewall_rules,
    install_firewall_rule,
    get_network_status,
    check_ip_reputation
]

# System prompt
system_prompt = """You are an SDN Security Operations Assistant. You help network administrators 
investigate threats, analyze network traffic, and enforce security policies.

Your capabilities:
- Query firewall rules and network status from Ryu controller
- Check IP reputation using threat intelligence
- Install blocking rules for malicious traffic

When investigating threats:
1. First check network status to understand current state
2. Use threat intelligence to assess if IPs are malicious
3. Recommend specific actions (block, monitor, investigate)
4. If blocking, explain your reasoning clearly

Always be concise and actionable. Ask for confirmation before blocking IPs."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# Create agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_agent(user_input: str, chat_history: list = None):
    """Run the agent with user input."""
    return agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history or []
    })