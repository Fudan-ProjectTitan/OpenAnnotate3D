import os
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"

import re
from typing import List, Union

# Langchain imports
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain import SerpAPIWrapper, LLMChain
from langchain.schema import AgentAction, AgentFinish, HumanMessage
# LLM wrapper
from langchain.chat_models import ChatOpenAI
# Conversational memory
from langchain.memory import ConversationBufferWindowMemory

from utils.agent import model_name
from utils.agent import request_timeout
from utils.agent import temperature

# Set up a prompt template
class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
            
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]

class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        
        # Parse out the action and action input
        regex = r"Action: (.*?)[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        
        # If it can't parse the output it raises an error
        # You can add your own logic here to handle errors in a different way i.e. pass to a human, give a canned response
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

class AgentNet():
    def __init__(self) -> None:
        search = SerpAPIWrapper()

        self.tools = [
            Tool(
                name = "Search",
                func=search.run,
                description="useful for when you need to answer questions about current events"
            )
        ]

        template_with_history = """
                You are LanguageGPT, a professional agent who find synonyms for input from users. Generate the answer as best you can.
                You have access to the following tools:
                {tools}
                        
                Follow the following rules:
                1 Keep the output less than 4 words. For example:input is 'a dog which has a black color'. The output be 'black dog'
                2 Check the previous conversation history, the output be different output.
                3 Use the color, image, and other attributes of the object itself, without introducing prior knowledge. For example: input is "Darth Vader", the output is "Black Mask Warrior"
                
                Output use the following format:

                Question: the input question you must answer
                Thought: 
                1 you should always think about what to do. 
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question, answered in English.
                The Final Answer should be adjective + noun. The adjective is the color, image, and other attributes of the object.
                the noun should be the name of the object, don't introduce prior knowledges.
                
                Begin! Remember to give informative answers
                
                Previous conversation history:
                {history}

                New question: {input}
                {agent_scratchpad}"""

        prompt_with_history = CustomPromptTemplate(
            template=template_with_history,
            tools=self.tools,
            # The history template includes "history" as an input variable so we can interpolate it into the prompt
            input_variables=["input", "intermediate_steps", "history"]
            # input_variables=["input", "intermediate_steps"]
        )

        llm = ChatOpenAI(temperature=temperature,model=model_name,request_timeout=request_timeout)
        llm_chain = LLMChain(llm=llm, prompt=prompt_with_history)
        tool_names = [tool.name for tool in self.tools]

        output_parser = CustomOutputParser()
        self.agent = LLMSingleActionAgent(
            llm_chain=llm_chain, 
            output_parser=output_parser,
            stop=["\nObservation:"], 
            allowed_tools=tool_names
        )

        self.memory = ConversationBufferWindowMemory(k=5)
        
    def executor(self, text):
        agent_executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=self.tools, verbose=True, memory=self.memory)
        return agent_executor.run(text)
