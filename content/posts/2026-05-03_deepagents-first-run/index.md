---
title: "DeepAgents: Testing a journal club agent"
subtitle: "A first-run of a simple AI Agent for researching a journal club article."
summary: "I document my first trial run of a non-trivial agent with a multi-step task. The aim of the project is to develop an AI agent to assist in preparing for an academic journal club. In this initial run, I explore the DeepAgents library's capabilities by making a simple request to download a journal article and convert it to Markdown format."
tags: ["Programming", "ML/AI"]
categories: ["Dev"]
date: 2026-05-03T00:00:00-08:00
lastmod: 2026-05-03T00:00:00-08:00
featured: false
draft: false
showHero: true
---

> This post is the second in a series on using DeepAgents, LangChain, and similar open-source, free libraries to build my own LLM tools.
> See ['DeepAgents: Getting Started']({{<ref "posts/2026-04-20_deepagents-getting-started">}}). for a my quickstart guide for running DeepAgent locally.

## Project background

This post kicks off the documentation of my first real project with the DeepAgents library: an agent for helping research in preparation of an academic journal club.
Briefly, a traditional journal club is a meeting where a research group will conduct a deep dive on an individual or few related recent academic publications.
Generally, one team member volunteers to lead the discussion, assuming the responsibility to have a comprehensive understanding of the paper.
The goal of this AI agent is to assist with this background preparation.

To begin, I am exploring the capabilities of the DeepAgents library.
In particular, I want to know how much guidance and oversight I, the developer, need to provide.
Do I need to provide tools for each part of the process, or can the DeepAgents harness and the flexibility of LLMs take care of this?

## Setup

### DeepAgent

#### Tools

I provided two tools to the DeepAgent: one for internet search and another to encourage "thinking."

The internet search tools uses Tavily to perform the search, then manually fetches the content of the website and converts it to Markdown.
Tavily has other AI options that may be worth investigating as I continue development, but for now it is just used for search.
I am using the free Researcher plan and have barely made a dent in my budget.

I took the second tool from the ['Deep Research'](https://github.com/langchain-ai/deepagents/tree/main/examples/deep_research) example.
I don't really understand who it works, but the creators of DeepAgents claim it improves performance.
The docstring instructs the agent to "Use this tool after each search to analyze results and plan next steps systematically. This creates a deliberate pause in the research workflow for quality decision-making."

#### Prompt

I derived the prompt from the one provided by the 'Deep Research' example.
It is rather long, so I only provide some of the customizations I made.

I start the prompt by telling the agent what it is:

```markdown
You are an emergency medicine doctor preparing for a journal club in an emergency department of a hospital in California, USA.
The journal club is attended by other medical doctors, residents, and students trained in emergency medicine.

Generally, you will be tasked with researching a single publication, but you may also be given a few to research together.
```

This is a very specific background at the moment – I will make this configurable in the future.
Right now, my plan is to have a Markdown file that will act as a model configuration where the user can provide this kind of background.

I then provide the agent with instructions on what to include in a journal club:

```markdown
## Report Writing Guidelines

A final report shall be created as '/final_report.md'.
The following is how the report should be structured:

1. Introduction
  - Key background that is required for understanding the paper.
  - What lead the authors to pursuing this research topic? Is there a gap in the field? Are there particular papers that logically lead to this one?
  - What is the background of the lead author(s) and the anchor author?
2. Results
  - For each section of the Results:
    - Identify the key findings and note which figures and data support the claim
    - What is the research question or hypothesis?
  - Indicate how one finding leads to the next experiment or question the authors pursued.
3. Conclusion
  - Key findings and takeaways
  - Gaps in the study
  - Limitations of the study
  - Next steps
4. Citations
  - Only include the most informative and relevant papers for future research.
```

Finally, I modified and tweaked the rest of the 'Deep Researcher' prompt to be more specific to literature research, academia, and science.

#### Backend

The default backend of DeepAgents is the [`StateBackend`](https://docs.langchain.com/oss/python/deepagents/backends#statebackend-ephemeral) which provides a virtual, ephemeral filesystem for the agent to use.
I want the journal club agent to be able to write documents, so I swapped this for the [`FilesystemBackend`](https://docs.langchain.com/oss/python/deepagents/backends#filesystembackend-local-disk).
This backend provides a safe location in which the agent can read and write – essentially a real, sand-boxed directory on my computer.

```python
backend = FilesystemBackend(root_dir="./agent-workspace/", virtual_mode=True)
```

#### Agent

Finally, I consturcted the agent with the simple interface that hides all of the complexity encoded in the DeepAgents library:

```python
create_deep_agent(
    model=chat_model,
    tools=[tavily_search, think_tool],
    system_prompt=instructions,
    subagents=[research_sub_agent],
    backend=backend,
)
```

### LLM

The LLM I am using is ["qwen3.6"](https://ollama.com/library/qwen3.6) served locally by Ollama.
This is a recent, frontier model, but I haven't done any experimentation with other models.
Given the runtime (see below), I will explore the use of smaller models.

## Task

### Input

For this demo, I used [my first publication](https://www.jbc.org/article/S0021-9258(20)39070-0/fulltext) because 1) I know the material, and 2) it is open-access, that is, it is not hidden behind a paywall.
The prompt I used was:

```python
result = agent.invoke(
    input={
        "messages": [
            {
                "role": "user",
                "content": "Download the scientific publication at this URL https://www.jbc.org/article/S0021-9258(20)39070-0/fulltext and parse it to Markdown. Save the result to a file 'paper.md'. Do not read the content of the paper or do anything to it. For now, just download the paper and convert it to markdown. Please state which tools you use and provide information on the types of inputs and outputs.",
            }
        ]
    }
)
```

I specifically instructed the agent to *not* perform additional research on the paper, just to download the publication and convert it to Markdown.
Even this simple task took over 28 minutes.
Below I go into more detail on the process the agent took.

### Result

Overall, the agent was successful: it produced a file "paper.md" with the Markdown text of my paper.
It also, as instructed, reported its use of the tools.
Below is the final message returned by the agent:

```markdown
The paper has been successfully downloaded and saved to /paper.md.

----------------------------------------------------------------------------

Tools Used:


 Tool           Type            Input                 Output
 ──────────────────────────────────────────────────────────────────────────
 tavily_search  Search & fetch  query parameter (URL  Full webpage content
                                or keyword search)    as Markdown text
 write_file     File I/O        file_path, content    Creates/overwrites
                                                      file on disk
 ls             File I/O        path                  Lists files in
                                                      directory
 read_file      File I/O        file_path, optional   File contents as text
                                offset/limit
 task           Agent spawner   description           Structured result
                                (instructions),       from sub-agent
                                subagent_type         execution


Workflow Summary:

 1 tavily_search — Fetched the paper content via its PMC identifier
   (PMC5836128). This tool searches the web and returns full webpage content
   as Markdown. The original JBC URL redirected to the PMC open-access
   version.
 2 write_file — Wrote the cleaned Markdown content to /paper.md.
 3 ls / read_file — Verified the file exists and confirmed its contents
   begin correctly.

Paper Saved:

 • Title: Toxoplasma gondii disrupts β1 integrin signaling and focal
   adhesion formation during monocyte hypermotility
 • Journal: The Journal of Biological Chemistry, Vol. 293, Issue 9, 2018
 • Authors: Joshua H Cook, Norikiyo Ueno, Melissa B Lodoen
 • DOI: 10.1074/jbc.M117.793281 | PMCID: PMC5836128
```

### Analysis of agent chain

I won't provide the full text of the agent's workflow, but instead have summarized the steps below:

1. The agent makes two tool cals:
    1. Called a tool to create a To-Do list with the following steps:
       a. "Save research request" (status: "in_progress")
       b. "Fetch the JBC paper from the URL" (status: "pending")
       c. "Convert the fetched content to Markdown and save to paper.md" (status: "pending")
    2. Call to the tool "write_file" to write the research request to markdown file "research_request.md" in the backend filesystem directory.
2. The tools make the To-Do list and the "research_request.md" file.
3. The agent calls the tool to update the To-Do list to mark the first as completed and the second as in-progress.
4. Creates a subagent to get the paper with the tool `tavily_search`.
5. The subagent reports back with the result of the paper request and the tool output.
6. The agent uses the `ls` tool to see if the output "paper.md" exists and the `read_file` tool to read in the Markdown file.
7. The agent updates the To-Do list to every step as complete.
8. The agent provides a summary output message to the user (above).

Overall, the sequence of events was:

1. HumanMessage
1. AIMessage
1. ToolMessage
1. ToolMessage
1. AIMessage
1. ToolMessage
1. AIMessage
1. ToolMessage
1. AIMessage
1. ToolMessage
1. ToolMessage
1. AIMessage
1. ToolMessage
1. AIMessage

## Conclusion

Overall, I'm very impressed with the agent, especially for how simple the code was.
It would be interesting to see how far it could get with performing the full research workflow as-is, but given the runtime for just this simple process, I think it would take way to long.
I think there are some easy adjustments to make already, but I should first focus on profiling the runtime to get that into a more reasonable range.
I discuss some of this below.

### Next steps

I first want to see how I can get more insight into where the time is being used.
Is it just waiting for Ollama to return or is the DeepAgent doing more work?
Based on that information, how can I reduce the runtime of the agent.

My suspicion is that the main bottleneck is that the "qwen3.6" model I am using is too large to run efficiently on my MacBook.
I will want to experiment with simple models and using the more complex models, especially those with image interpretation capabilities, as specialized subagents.
For example, I could see specifying "qwen3.6" for interpreting figures or summarizing papers.
Based on my experience with Cursor for work, it should be feasible to use a complex model for plan creation and simpler models for execution and subagents.

There are also some changes I want to make to the agent flow:

- Can I have the search_tool write the Markdown to file instead of returning a string? Will that improve performance by not requiring the markdown to be loaded into the model's context.
- Have the agent get approval for the plan before execution.
- Add to the system prompt to instruct the agent to recommend next steps and follow-ups to the user.
- Make a helper function to save the full chain of the agent execution to file
