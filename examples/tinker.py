from __future__ import annotations

import asyncio
import json
import logging
import os

import logfire
from agents import Agent
from agents import Runner
from agents import function_tool
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field


logging.getLogger().setLevel(logging.DEBUG)

logfire.configure()
logfire.instrument_openai_agents()
# Load environment variables
load_dotenv()

model = os.getenv("MODEL_CHOICE", "gpt-4o-mini")


# --- Models for structured outputs ---


class FlightRecommendation(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: float
    direct_flight: bool
    recommendation_reason: str


class HotelRecommendation(BaseModel):
    name: str
    location: str
    price_per_night: float
    amenities: list[str]
    recommendation_reason: str


class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    budget: float
    activities: list[str] = Field(description="List of recommended activities")
    notes: str = Field(description="Additional notes or recommendations")


# --- Tools ---


@function_tool
def get_weather_forecast(city: str, date: str) -> str:
    """Get the weather forecast for a city on a specific date."""
    # In a real implementation, this would call a weather API
    weather_data = {
        "New York": {"sunny": 0.3, "rainy": 0.4, "cloudy": 0.3},
        "Los Angeles": {"sunny": 0.8, "rainy": 0.1, "cloudy": 0.1},
        "Chicago": {"sunny": 0.4, "rainy": 0.3, "cloudy": 0.3},
        "Miami": {"sunny": 0.7, "rainy": 0.2, "cloudy": 0.1},
        "London": {"sunny": 0.2, "rainy": 0.5, "cloudy": 0.3},
        "Paris": {"sunny": 0.4, "rainy": 0.3, "cloudy": 0.3},
        "Tokyo": {"sunny": 0.5, "rainy": 0.3, "cloudy": 0.2},
    }

    if city in weather_data:
        conditions = weather_data[city]
        # Simple simulation based on probabilities
        highest_prob = max(conditions, key=conditions.get)
        temp_range = {
            "New York": "15-25°C",
            "Los Angeles": "20-30°C",
            "Chicago": "10-20°C",
            "Miami": "25-35°C",
            "London": "10-18°C",
            "Paris": "12-22°C",
            "Tokyo": "15-25°C",
        }
        return f"The weather in {city} on {date} is forecasted to be {highest_prob} with temperatures around {temp_range.get(city, '15-25°C')}."
    else:
        return f"Weather forecast for {city} is not available."


@function_tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for flights between two cities on a specific date."""
    # In a real implementation, this would call a flight search API
    flight_options = [
        {"airline": "SkyWays", "departure_time": "08:00", "arrival_time": "10:30", "price": 350.00, "direct": True},
        {"airline": "OceanAir", "departure_time": "12:45", "arrival_time": "15:15", "price": 275.50, "direct": True},
        {
            "airline": "MountainJet",
            "departure_time": "16:30",
            "arrival_time": "21:45",
            "price": 225.75,
            "direct": False,
        },
    ]

    return json.dumps(flight_options)


@function_tool
def search_hotels(city: str, check_in: str, check_out: str, max_price: float | None = None) -> str:
    """Search for hotels in a city for specific dates within a price range."""
    # In a real implementation, this would call a hotel search API
    hotel_options = [
        {
            "name": "City Center Hotel",
            "location": "Downtown",
            "price_per_night": 199.99,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
        },
        {
            "name": "Riverside Inn",
            "location": "Riverside District",
            "price_per_night": 149.50,
            "amenities": ["WiFi", "Free Breakfast", "Parking"],
        },
        {
            "name": "Luxury Palace",
            "location": "Historic District",
            "price_per_night": 349.99,
            "amenities": ["WiFi", "Pool", "Spa", "Fine Dining", "Concierge"],
        },
    ]

    # Filter by max price if provided
    if max_price is not None:
        filtered_hotels = [hotel for hotel in hotel_options if hotel["price_per_night"] <= max_price]
    else:
        filtered_hotels = hotel_options

    return json.dumps(filtered_hotels)


# --- Specialized Agents ---

flight_agent = Agent(
    name="Flight Specialist",
    handoff_description="Specialist agent for finding and recommending flights",
    instructions="""
    You are a flight specialist who helps users find the best flights for their trips.

    Use the search_flights tool to find flight options, and then provide personalized recommendations
    based on the user's preferences (price, time, direct vs. connecting).

    Always explain the reasoning behind your recommendations.

    Format your response in a clear, organized way with flight details and prices.
    """,
    model=model,
    tools=[search_flights],
    output_type=FlightRecommendation,
)

hotel_agent = Agent(
    name="Hotel Specialist",
    handoff_description="Specialist agent for finding and recommending hotels and accommodations",
    instructions="""
    You are a hotel specialist who helps users find the best accommodations for their trips.

    Use the search_hotels tool to find hotel options, and then provide personalized recommendations
    based on the user's preferences (location, price, amenities).

    Always explain the reasoning behind your recommendations.

    Format your response in a clear, organized way with hotel details, amenities, and prices.
    """,
    model=model,
    tools=[search_hotels],
    output_type=HotelRecommendation,
)

# --- Main Travel Agent ---

travel_agent = Agent(
    name="Travel Planner",
    instructions="""
    You are a comprehensive travel planning assistant that helps users plan their perfect trip.

    You can:
    1. Provide weather information for destinations
    2. Create personalized travel itineraries
    3. Hand off to specialists for flights and hotels when needed

    Always be helpful, informative, and enthusiastic about travel. Provide specific recommendations
    based on the user's interests and preferences.

    When creating travel plans, consider:
    - The weather at the destination
    - Local attractions and activities
    - Budget constraints
    - Travel duration

    If the user asks specifically about flights or hotels, hand off to the appropriate specialist agent.
    """,
    model=model,
    tools=[get_weather_forecast],
    handoffs=[flight_agent, hotel_agent],
    output_type=TravelPlan,
)


# --- Main Function ---


async def main():
    # Example queries to test different aspects of the system
    queries = [
        "I need a flight from New York to Chicago tomorrow",
        "Find me a hotel in Paris with a pool for under $300 per night",
    ]

    for query in queries:
        print("\n" + "=" * 50)
        print(f"QUERY: {query}")

        result = await Runner.run(travel_agent, query)

        print("\nFINAL RESPONSE:")

        # Format the output based on the type of response
        if hasattr(result.final_output, "airline"):  # Flight recommendation
            flight = result.final_output
            print("\n✈️ FLIGHT RECOMMENDATION ✈️")
            print(f"Airline: {flight.airline}")
            print(f"Departure: {flight.departure_time}")
            print(f"Arrival: {flight.arrival_time}")
            print(f"Price: ${flight.price}")
            print(f"Direct Flight: {'Yes' if flight.direct_flight else 'No'}")
            print(f"\nWhy this flight: {flight.recommendation_reason}")

        elif hasattr(result.final_output, "name") and hasattr(result.final_output, "amenities"):  # Hotel recommendation
            hotel = result.final_output
            print("\n🏨 HOTEL RECOMMENDATION 🏨")
            print(f"Name: {hotel.name}")
            print(f"Location: {hotel.location}")
            print(f"Price per night: ${hotel.price_per_night}")

            print("\nAmenities:")
            for i, amenity in enumerate(hotel.amenities, 1):
                print(f"  {i}. {amenity}")

            print(f"\nWhy this hotel: {hotel.recommendation_reason}")

        elif hasattr(result.final_output, "destination"):  # Travel plan
            travel_plan = result.final_output
            print(f"\n🌍 TRAVEL PLAN FOR {travel_plan.destination.upper()} 🌍")
            print(f"Duration: {travel_plan.duration_days} days")
            print(f"Budget: ${travel_plan.budget}")

            print("\n🎯 RECOMMENDED ACTIVITIES:")
            for i, activity in enumerate(travel_plan.activities, 1):
                print(f"  {i}. {activity}")

            print(f"\n📝 NOTES: {travel_plan.notes}")

        else:  # Generic response
            print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
