from __future__ import annotations

import asyncio

from agents import Agent
from agents import Runner
from pydantic import BaseModel
from pydantic import Field


class CityInfo(BaseModel):
    """Structured information about a city"""

    city: str = Field(description="The city name")
    country: str = Field(description="The country name")
    population: int = Field(description="Population count")
    famous_for: list[str] = Field(description="List of things the city is famous for")
    fun_fact: str = Field(description="An interesting fact")


# Create an agent with structured output
agent = Agent(
    name="City Expert",
    instructions="Provide detailed city information.",
    output_type=CityInfo,  # Force structured output
)


async def main():
    # The response will be a CityInfo object, not text!
    result = await Runner.run(agent, "Tell me about Paris")
    city_data: CityInfo = result.final_output

    print(city_data)
    print("----------------------------------------")
    print(f"{city_data.city}, {city_data.country}")
    print(f"Population: {city_data.population:,}")
    print(f"Famous for: {', '.join(city_data.famous_for)}")
    print(f"Fun fact: {city_data.fun_fact}")


if __name__ == "__main__":
    asyncio.run(main())
