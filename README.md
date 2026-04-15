# pretty-please 🙏🏼

> Politely injects **PLEASE** into your LLM prompts. Because manners matter (kind of).

`pretty-please` is a tiny, zero-dependency Python library that intercepts your prompts before they reach an LLM and gives them a light politeness pass. It works as a drop-in wrapper around the Anthropic and OpenAI SDKs, as a LiteLLM callback, and as a Claude Code `UserPromptSubmit` hook.

```python
from pretty_please.core import transform

transform("List the planets.")
# → "Please, list the planets."

transform("I need help improving this function.")
# → "I need help improving this function, please."

transform("Please could you explain this?")
# → "Please could you explain this?"  (already polite, untouched)
```

---

## Does this actually work?

**Honest answer: sort of, and it depends on the model.**

The research on this is genuinely interesting:

- **Yin et al. (2024) — "Should We Respect LLMs? Investigating Social Primitives in Human-LLM Interactions"** ([arXiv:2402.14531](https://arxiv.org/abs/2402.14531)) found that *rudeness* reliably hurts performance across a range of tasks — rude prompts produced measurably worse outputs. Adding *please* or other polite framing had a **modest and inconsistent** effect on frontier models like GPT-4, but a **more notable positive effect on smaller models**.

- The takeaway: don't be rude to your LLM (it actually hurts), and being polite doesn't hurt and may help — especially if you're using a smaller or fine-tuned model.

`pretty-please` mostly guards against the downside (accidental curtness/rudeness) rather than promising a magic uplift. Think of it as defensive prompt hygiene.

---

## Installation

```bash
pip install pretty-please
```

With SDK extras:

```bash
pip install "pretty-please[anthropic]"
pip install "pretty-please[openai]"
pip install "pretty-please[litellm]"
```

---

## Usage

### Core (no dependencies)

```python
from pretty_please.core import detect_tone, transform

detect_tone("Fix this bug.")       # → "curt"
detect_tone("Could you help me?")  # → "polite"
detect_tone("I need a summary.")   # → "neutral"

transform("Fix this bug.")         # → "Please, fix this bug."
transform("I need a summary.")     # → "I need a summary, please."
transform("Please help me.")       # → "Please help me."  (unchanged)
```

### Anthropic SDK

```python
from pretty_please.adapters.anthropic import PrettyAnthropicClient

client = PrettyAnthropicClient()  # same args as anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarize this article."}],
    # ↑ becomes "Please, summarize this article." under the hood
)
```

### OpenAI SDK

```python
from pretty_please.adapters.openai import PrettyOpenAIClient

client = PrettyOpenAIClient()  # same args as openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku about deadlines."}],
)
```

### LiteLLM

```python
from pretty_please.adapters.litellm import install
install()  # register the callback once at startup

import litellm
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain gradient descent."}],
)
```

### Claude Code hook

Install the hook into your `~/.claude/settings.json`:

```bash
pretty-please install-hook
# or
python -m pretty_please.adapters.claude_code.install
```

From then on, every prompt you type in Claude Code will be politely transformed before it's sent. The hook is a `UserPromptSubmit` hook — it runs transparently in the background.

---

## How it works

Tone is detected by a small set of rules (no ML, no external deps):

| Tone | Signal | Transform |
|------|--------|-----------|
| **polite** | contains *please / could / would / kindly / can you* | pass through unchanged |
| **curt** | short imperative verb, no modal, or profanity/ALL CAPS | prepend `"Please, "` |
| **neutral** | everything else | append `", please"` |

---

## Contributing

This project is a work in progress and contributions are very welcome! Open an issue or PR at [github.com/msrdic/pretty-please](https://github.com/msrdic/pretty-please).

---

## License

MIT
