"""
OpenAI SDK example using pretty-please.

Requires: pip install openai pretty-please
"""

from pretty_please.adapters.openai import PrettyOpenAIClient

client = PrettyOpenAIClient()

# Curt prompt — will be transformed to "Please, write a haiku..."
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Write a haiku about debugging at 2am."}
    ],
)

print(response.choices[0].message.content)
