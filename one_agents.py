from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm # 用于多模型支持
from utils.config_loader import ConfigLoader
from prompts.prompts import input_process_prompt, scheduler_prompt, customer_portrait_prompt, customer_behavior_prompt, collaborate_prompt, follow_up_prompt, get_collaborate_prompt, send_file_prompt, one_to_N_prompt
from tools.callbacks import check_prompt_protection, dynamic_one_to_N_agent_instruction_before_model
from tools.input_process import image_comprehension, video_comprehension, read_file, get_detailed_time
from tools.core_logic import select_file
from utils.db_queries import select_collaborate_matters, select_product
from utils.db_insert import insert_customer_behavior
from utils.db_queries import update_customer_portrait
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


one_to_N_agent = LlmAgent(
    model=qwen_model,
    name="one_to_N_agent",
    description="公司的销售人员，负责与客户进行沟通，并根据客户的需求，回复客户信息。完成销售任务。",
    instruction=one_to_N_prompt,
    tools=[image_comprehension, video_comprehension,read_file,get_detailed_time,update_customer_portrait,insert_customer_behavior, select_collaborate_matters, select_file, select_product],
    before_model_callback=dynamic_one_to_N_agent_instruction_before_model,
    before_agent_callback=check_prompt_protection,
)



# input_process_agent = Agent(

if __name__ == "__main__":
    print(qwen_base_url)
    print(qwen_api_key)