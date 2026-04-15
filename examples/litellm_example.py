"""
LiteLLM example using pretty-please.

Requires: pip install litellm pretty-please
"""

from pretty_please.adapters.litellm import completion

# Curt prompt — will be transformed to "Please, explain gradient descent."
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain gradient descent."}],
)

print(response.choices[0].message.content)
