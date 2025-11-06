from __future__ import annotations

import asyncio
import json

from agents import Agent
from agents import Runner
from agents import function_tool
from pydantic import BaseModel


# Tool 1: Weather forecast
@function_tool
def get_weather_forecast(city: str, date: str) -> str:
    """Get weather forecast for a city on a specific date."""
    weather_db = {"Tokyo": "Sunny, 20-25°C", "Paris": "Rainy, 15-18°C", "New York": "Cloudy, 18-22°C"}
    return f"Weather in {city} on {date}: {weather_db.get(city, 'Data not available')}"


# Tool 2: Flight search
@function_tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights."""
    flights = [
        {"airline": "SkyWays", "time": "08:00", "price": 350, "direct": True},
        {"airline": "OceanAir", "time": "14:30", "price": 280, "direct": False},
    ]
    return json.dumps(flights)


# Tool 3: Hotel search
@function_tool
def search_hotels(city: str, max_price: float = 500.0) -> str:
    """Search for hotels in a city."""
    hotels = [
        {"name": "City Center Hotel", "price": 199, "rating": 4.5},
        {"name": "Riverside Inn", "price": 149, "rating": 4.2},
    ]
    filtered = [h for h in hotels if h["price"] <= max_price]
    return json.dumps(filtered)


# Structured output
class TravelPlan(BaseModel):
    destination: str
    travel_dates: str
    weather_summary: str
    flight_recommendation: str
    hotel_recommendation: str
    estimated_budget: float


# Create the travel agent
travel_agent = Agent(
    name="Travel Planner",
    instructions="""
    You are a comprehensive travel planning assistant.

    When helping users plan trips:
    1. Ask about destination, dates, and budget if not provided
    2. Check weather using get_weather_forecast
    3. Search flights using search_flights
    4. Find hotels using search_hotels
    5. Create a complete travel plan with recommendations

    Always explain your recommendations and consider the user's budget!
    """,
    tools=[get_weather_forecast, search_flights, search_hotels],
    output_type=TravelPlan,
    model="gpt-4o-mini",
)


async def main():
    result = await Runner.run(travel_agent, "I want to travel to Tokyo next month. My budget is $2000.")

    plan: TravelPlan = result.final_output

    print(f"\n✈️ TRAVEL PLAN TO {plan.destination.upper()} ✈️")
    print(f"📅 Dates: {plan.travel_dates}")
    print(f"🌤️  Weather: {plan.weather_summary}")
    print(f"✈️ Flight: {plan.flight_recommendation}")
    print(f"🏨 Hotel: {plan.hotel_recommendation}")
    print(f"💰 Budget: ${plan.estimated_budget}")


if __name__ == "__main__":
    asyncio.run(main())
