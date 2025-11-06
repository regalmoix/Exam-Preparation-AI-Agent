from __future__ import annotations

import asyncio

from openai import AsyncOpenAI


# Initialize the OpenAI client
client = AsyncOpenAI()


async def conversation_example():
    """Multi-turn conversation"""

    conversation = [{"role": "system", "content": "You are a helpful assistant."}]

    # First turn
    conversation.append({"role": "user", "content": "My name is Alice and I love Python."})

    response1 = await client.chat.completions.create(model="gpt-4o-mini", messages=conversation)

    # Add assistant's response to history
    conversation.append({"role": "assistant", "content": response1.choices[0].message.content})

    # Second turn - referencing previous context
    conversation.append({"role": "user", "content": "What's my name and favorite programming language?"})

    response2 = await client.chat.completions.create(model="gpt-4o-mini", messages=conversation)

    print(response2.choices[0].message.content)
    # Output: "Your name is Alice and your favorite programming language is Python!"


# Run the example
if __name__ == "__main__":
    asyncio.run(conversation_example())
