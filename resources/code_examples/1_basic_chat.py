from __future__ import annotations

import asyncio

from openai import AsyncOpenAI


# Initialize the OpenAI client
client = AsyncOpenAI()


async def basic_chat():
    """Simple chat completion example"""

    # Create a conversation
    messages = [
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "What is 25 * 4?"},
    ]

    # Call the API
    response = await client.chat.completions.create(
        model="gpt-4o-mini",  # The model to use
        messages=messages,
        temperature=0.7,  # Creativity (0=focused, 1=creative)
    )

    # Extract the response
    answer = response.choices[0].message.content
    print(f"AI: {answer}")


# Run the example
if __name__ == "__main__":
    asyncio.run(basic_chat())
