from __future__ import annotations

import asyncio

from agents import Agent
from agents import Runner
from agents import function_tool
from pydantic import BaseModel


# Step 1: Define the tool output structure
class Weather(BaseModel):
    city: str
    temperature: str
    conditions: str


# Step 2: Create a tool using the @function_tool decorator
@function_tool
def get_weather(city: str) -> Weather:
    """
    Get the current weather for a given city.

    Args:
        city: Name of the city to get weather for

    Returns:
        Weather information including temperature and conditions
    """
    # In real life, this would call a weather API
    return Weather(city=city, temperature="20°C", conditions="Sunny")


# Step 3: Create an agent with the tool
weather_agent = Agent(
    name="Weather Assistant",
    instructions="You are a helpful weather assistant. Use the get_weather tool to provide weather information.",
    tools=[get_weather],  # Give the agent access to the tool
)


# Step 4: Run the agent
async def main():
    result = await Runner.run(weather_agent, "What's the weather like in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
