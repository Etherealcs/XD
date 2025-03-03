from langchain.agents import create_openai_functions_agent, AgentExecutor, create_react_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.tools import create_retriever_tool

def create_agent(input_prompt:str,retriever,llm):
    if retriever==None:
        prompt = ChatPromptTemplate.from_messages([
            (
            "system", input_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])
        agent_executor = prompt | llm | StrOutputParser()
    else:
        prompt = ChatPromptTemplate.from_messages([
            (
            "system", input_prompt),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])
        retriever_tool = create_retriever_tool(
            retriever,
            "retriever_tool",
            "Search for information . For any questions , you must use this tool!",
        )
        tools = [retriever_tool]
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor

def create_tongyi_react_agent(retriever,llm):
    template = '''Answer the following questions as best you can. You have access to the following tools:

                {tools}

                Use the following format:
                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tool_names}],or search chat_history
                Action Input: the input to the action
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat up to 2 times)
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question

                Begin!

                Rule：{prompt}
                Question: {input}
                Chat_history:{chat_history}
                Thought:{agent_scratchpad}'''
    prompt = PromptTemplate.from_template(template)

    retriever_tool = create_retriever_tool(
        retriever,
        "retriever_tool",
        "Search for information . For any questions , you may use this tool!",
    )
    tools = [retriever_tool]

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    return agent_executor