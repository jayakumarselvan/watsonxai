from google.adk import Agent, Workflow, Event
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel


# 1. Define schemas for data transitions
class GeneratedCity(BaseModel):
    city_name: str


class CityTime(BaseModel):
    time_info: str  # time information
    city: str  # city name


# 2. Define the Agents
city_generator_agent = LlmAgent(
    model=LiteLlm(model="watsonx/meta-llama/llama-3-3-70b-instruct"),
    name="city_generator_agent",
    instruction="""Return the name of a random city.
      Return only the name, nothing else.""",
    output_schema=GeneratedCity,
)

city_report_agent = LlmAgent(
    model=LiteLlm(model="watsonx/meta-llama/llama-3-3-70b-instruct"),
    name="city_report_agent",
    input_schema=CityTime,
    instruction="""Output following line:
    It is {CityTime.time_info} in {CityTime.city} right now.""",
    # REMOVED output_schema=str so it emits unstructured text/string safely
)


# 3. Define the processing functions
def lookup_time_function(node_input: GeneratedCity):
    """Simulate returning the current time in the specified city."""
    return CityTime(time_info="10:10 AM", city=node_input.city_name)


def completed_message_function(node_input: str):
    return Event(
        message=f"{node_input}\n WORKFLOW COMPLETED.",
    )


# 4. Assemble the Workflow
root_agent = Workflow(
    name="root_agent",
    edges=[
        (
            "START",
            city_generator_agent,
            lookup_time_function,
            city_report_agent,
            completed_message_function,
        )
    ],
)
