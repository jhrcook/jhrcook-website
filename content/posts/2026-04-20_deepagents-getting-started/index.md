---
title: "DeepAgents: Getting Started"
subtitle: "Getting started with the DeepAgents library to run LLM agents locally.."
summary: "..."
tags: ["Programming", "ML/AI"]
categories: ["Dev"]
date: 2026-04-20T00:00:00-08:00
lastmod: 2026-04-20T00:00:00-08:00
featured: false
draft: false
showHero: true
---

> I aim for this to be a series on using DeepAgents, LangChain, and similar open-source, free libraries to build my own LLM tools.

## Introduction

I became interested in the [DeepAgents](https://docs.langchain.com/oss/python/deepagents/overview) library after learning about it on the [*Talk Python to Me*](https://talkpython.fm/) podcast episode ["Deep Agents: LangChain's SDK for Agents That Plan and Delegate."](https://talkpython.fm/episodes/show/543/deep-agents-langchains-sdk-for-agents-that-plan-and-delegate)
Aiding in my goal of writing more blog posts this year, I hope for this to become a bit of an ongoing series as I explore the vast world of open-source, free-to-use LLM tools.
I have [firsthand experience using modern AI tools]({{<ref "posts/2026-03-08_one-week-with-cursor">}}) at work, namely [Cursor](https://cursor.com/), and have been very impressed by their capabilities.

In this post, I begin my exploration of DeepAgents, a library built atop [LangChain](https://docs.langchain.com/), to build AI agents.
I'll show you how to get started with a simple researcher agent running locally.

## Code

### Setup

#### Ollama to run local models

To begin, I ran my AI model locally using [Ollama](https://ollama.com/).
I installed this via [homebrew](https://brew.sh/) on my MacBook Pro and started the server:

```bash
brew install ollama
ollama serve
```

From the Ollama [Models](https://ollama.com/search) tab, I chose to use [qwen3.6](https://ollama.com/library/qwen3.6).
I do not have a strong understanding of the pros and cons of modern frontier models, so this may be a point of future improvements and optimizations as I learn.
Note that the first time using a model, Ollama will need to download it.
This can take a few minutes.

```bash
ollama run qwen3.6
```

This can also be initiated from Python via the Ollama Python SDK.
I will perhaps explore this in the future so that everything can be orchestrated from Python.

#### Travily

There are many services for performing internet searches, but the DeepAgents documentation recommended [Tavily](https://www.tavily.com).
It took just a couple of minutes to register an account and get a free API key.
There is a usage limit for the free tier, but in my testing it seems generous and should be sufficient for experimentation.
Again, a more thorough survey of the options could be a good point of improvement in the future (I could have my researcher agent do this for me!).

I saved the API key to a YAML secrets file for easy ingestion into Python:

```yaml
api_keys:
  "tavily": "API-KEY"

```

#### DeepAgents

From there, I just ran the demo [Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart) code from DeepAgents.
I chose to run the code in a Jupyter notebook so I could explore the intermediates and interact with the model.

Begin by importing the necesssary libraries:

```python
from pathlib import Path
from typing import Literal

import yaml
from deepagents import create_deep_agent
from IPython.display import Markdown, display
from rich import print as rprint
from tavily import TavilyClient
```

and reading in the Tavily API key:

```python
with Path("secrets.yaml").open() as f:
    secrets = yaml.safe_load(f)["api_keys"]
```

We then make a "tool" that our agent can use.
This is just a wrapper around the search function of a Travily client.
Wrapping it in a function serves a few purposes:

1. It limits the scope of the search functionality of the Trivaly client by restricting the access of arguments.
2. It provides type information for the inputs and outputs.
3. Allows us to add documentation for the AI model in the function's docstring.

Again, I took this directly from the Quickstart guide.
I will explore other internet search tools in the future.

```python
tavily_client = TavilyClient(api_key=secrets["tavily"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict:
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
```

Next, we create a an agent.
This include a prompt for the agent to be an "expert researcher" and we tell it about it's internet search tool.

```python
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model="ollama:qwen3.6", tools=[internet_search], system_prompt=research_instructions
)
```

Finally, we can interact with our agent:

```bash
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Tell me about the new 5-base sequencing from Illumina.",
            }
        ]
    }
)
display(Markdown(result["messages"][-1].content))
```

The following (between the horizontal breaks) is directly from the model, formatting and all:

---

Illumina's **5-base solution** is a multiomic sequencing technology announced in 2025. Here's what it is and why it matters:

## What It Is

The 5-base solution is a novel chemistry and workflow that enables **simultaneous detection of genomic variants and DNA methylation** from a single sample in a single assay. It effectively sequences five DNA bases — A, T, G, C, and 5mC (5-methylcytosine) — all in the same sequencing read.

## The Core Innovation

At its heart is a **bespoke, in-house engineered enzyme** that directly and selectively converts methylated cytosines (5mC) into thymine. Unlike traditional bisulfite conversion (which degrades DNA and requires harsh conditions) or Illumina's existing EM-seq chemistry (which requires two separate library preparations), this 5-base conversion is:

- **A single-step process** — no dual library prep
- **Non-damaging to DNA** — preserves library complexity
- **Highly specific** — conversion accuracy of ~95% for methylated control DNA, with unmethylated background at <1%

## Key Benefits

- **One assay, dual insights** — eliminates the need for two separate library preparations, saving time, cost, and sample
- **Streamlined workflow** — library prep takes ~6 hours from DNA to sequencing
- **Higher mapping efficiency** — more useful reads per sequencer output, since you don't lose reads to dual-prep artifacts
- **Integrated analysis** — powered by custom DRAGEN algorithms and Illumina Connected Multiomics visualization tools

## Why It Matters

Traditionally, studying both genetic variants (SNPs, indels) and epigenetic modifications (methylation) required parallel workflows on the same or different samples, increasing cost and complexity. The 5-base solution consolidates this into a single pipeline — a significant advance for studies where sample material is limited (e.g., rare disease research, circulating tumor DNA, clinical samples).

The technology was announced at Illumina's ASHG 2025 showcase, with presentations covering applications ranging from rare disease detection to colorectal cancer detection through rectal mucus sampling.

---

## Next steps

I'm very excited to see what I can build with the DeepAgents library.

The obvious next step is to continue reading the docuemntation to familialize myself with this capabilities.
Namely, I want to better understand the steps of the agent as I think optimizing and enhancing this process will open the door to more powerful features.

Otherwise, as I noted in a few places in this post, researching the broader environment of tools will be necessary.
This includes other internet searching SDKs, which AI models to employ, and other tools I can provide to my agents.
