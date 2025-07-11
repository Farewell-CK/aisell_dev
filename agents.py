from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm # 用于多模型支持
from utils.config_loader import ConfigLoader
from prompts.prompts import input_process_prompt, scheduler_prompt, customer_portrait_prompt, customer_behavior_prompt, collaborate_prompt, follow_up_prompt, get_collaborate_prompt, send_file_prompt
from tools.callbacks import check_prompt_protection, dynamic_chat_agent_instruction_before_model
from tools.input_process import speech_to_text, image_comprehension, video_comprehension
from tools.core_logic import select_file
from utils.db_queries import select_collaborate_matters
from utils.db_insert import insert_customer_behavior, insert_customer_portrait

config = ConfigLoader()

qwen_base_url = config.get_api_key('qwen', 'base_url')
qwen_api_key = config.get_api_key('qwen', 'api_key')

ernie_base_url = config.get_api_key('ernie', 'base_url')
ernie_api_key = config.get_api_key('ernie', 'api_key')

qwen_model = LiteLlm(
    model="openai/qwen-max-latest",
    base_url=qwen_base_url,
    api_key=qwen_api_key
)

ernie_model = LiteLlm(
    model="openai/ernie-4.5-turbo-128k",
    base_url=ernie_base_url,
    api_key=ernie_api_key
)

input_process_agent = LlmAgent(
    model=qwen_model,
    name="input_process_agent",
    description="对用户输入进行预处理，将用户输入的各类信息（文本、图片、视频）统一转换为标准化的结构化数据格式，然后传递给下一个team_work_agent智能体进行处理。",
    instruction=input_process_prompt,
    tools=[speech_to_text, image_comprehension, video_comprehension],
    before_agent_callback=check_prompt_protection,
)

customer_portrait_agent = LlmAgent(
    model=qwen_model,
    name="customer_portrait_agent",
    description="根据历史聊天记录和用户发送的最新信息 生成或更新客户画像。",
    instruction=customer_portrait_prompt,
    tools=[insert_customer_portrait],
)

customer_behavior_agent = LlmAgent(
    model=qwen_model,
    name="customer_behavior_agent",
    description="根据历史聊天记录和客户发送的最新信息，生成或更新客户行为。",
    instruction=customer_behavior_prompt,
    tools=[insert_customer_behavior],
)

# 协作事项可以调整，1、不发送通知，最终汇总到chat_agent中；2、发送通知，chat_agent中不发送协作事项
collaborate_agent = LlmAgent(
    model=qwen_model,
    name="collaborate_agent",
    description="根据聊天内容，判断触发哪种协作事项。",
    instruction=collaborate_prompt,
    tools=[select_collaborate_matters],
)

## 跟单事项
follow_up_agent = LlmAgent(
    model=qwen_model,
    name="follow_up_agent",
    description="根据聊天内容，判断其是否触发跟单事项。",
    instruction=follow_up_prompt,
    # tools=[follow_up_notification],
)

## 对应的角色提示词，需要拼接，去数据库中获取
chat_agent = LlmAgent(
    model=ernie_model,
    name="chat_agent",
    description="总结团队的意见，根据客户的输入，回复客户信息。",
    instruction="初始化提示词，将被动态更新。",
    before_model_callback=dynamic_chat_agent_instruction_before_model,
    # before_agent_callback=dynamic_chat_agent_instruction_callback,
)

# scheduler_agent = LlmAgent(
#     model=qwen_model,
#     name="scheduler_agent",
#     description="调度器，根据'input_process_agent'对客户输入的预处理结果，决定是否需要调用其他agent",
#     instruction=scheduler_prompt,
# )
send_file_agent = LlmAgent(
    model=qwen_model,
    name="send_file_agent",
    description="根据聊天内容，调用send_file工具，查询相关文件。并判断是否需要发送文件。把文件的url返回给chat_agent。",
    instruction=send_file_prompt,
    tools=[select_file],
)

## 团队并行执行
team_work_agent = ParallelAgent(
    sub_agents=[collaborate_agent, follow_up_agent, customer_portrait_agent, customer_behavior_agent, send_file_agent],
    name="team_work_agent",
    description="运行多个可以同时执行的agent，并行执行的目的是为了提高效率，减少等待时间。并将各个agent的执行结果汇总，交给'chat_agent'。",
)

root_agent = SequentialAgent(
    sub_agents=[input_process_agent, team_work_agent, chat_agent],
    name="root_agent",
    description="根节点，负责调度其他agent，并行执行。",
)



# input_process_agent = Agent(

if __name__ == "__main__":
    print(qwen_base_url)
    print(qwen_api_key)