"""
Anthropic SDK example using pretty-please.

Requires: pip install anthropic pretty-please
"""

from pretty_please.adapters.anthropic import PrettyAnthropicClient

client = PrettyAnthropicClient()

# Curt prompt — will be transformed to "Please, list three interesting facts..."
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "List three interesting facts about octopuses."}
    ],
)

print(response.content[0].text)
