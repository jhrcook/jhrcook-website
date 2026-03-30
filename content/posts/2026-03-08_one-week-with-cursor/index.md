---
title: "One week with Cursor"
subtitle: "My thoughts after one week of thoroughly using Cursor AI coding environment on real projects at work."
summary: "My thoughts after one week of thoroughly using Cursor AI coding environment on real projects at work."
tags: ["Programming", "ML/AI"]
categories: ["Dev"]
date: 2026-03-30T00:00:00-08:00
lastmod: 2026-03-30T00:00:00-08:00
featured: false
draft: false
showHero: true
---

The head of my department recently devoted half of an hour-long town hall to demonstrate several colleagues using [Cursor](https://cursor.com), an AI agent–based software development environment, on real projects.
Generally skeptical of the hype surrounding large language model–centric tools, I took this as a sign to finally give it a serious try.
What follows are my impressions after a week of using Cursor daily on real, production-level work.

## Getting started

Installation was fast and painless. Cursor is a fork of Visual Studio Code, the IDE I already use for nearly everything, so the environment felt instantly familiar.
To get up to speed, I watched a recording of a presentation that Cursor’s team gave to Illumina employees during their pilot program.
The main takeaway was simple but powerful: use Plan Mode.

### Understanding *Plan Mode*

[Plan Mode](https://cursor.com/blog/plan-mode) is where Cursor really differentiates itself from a regular code editor with autocomplete.
You start by giving the agent instructions for what you’d like to build. Instead of immediately generating code, it produces a plan — a structured markdown file summarizing the goal and outlining step-by-step actions to achieve it.

The logic here is that the plan acts like a contract: it keeps the AI focused on your objective and reduces “drift” during implementation.
A typical plan might include:

- A summary of the overall task (“Add automated file validation to ingestion pipeline”).
- A list of explicit implementation steps (*e.g.*, create a validator class, integrate it into an existing module, update tests).
- Optional clarifying questions or suggestions.

Once the plan looks good, I hit Build, and an AI agent executes each step automatically.
I can also request changes to the plan before execution, which has been useful for refining finer details.
When the build completes, I review the results using git diffs directly inside Cursor.
Most of the time, the changes are clean enough to commit after minimal tweaks.

### Collaboration through questions

Another feature I immediately appreciated was agent-assisted clarification.
When Cursor is uncertain about how to proceed, it doesn’t guess – it asks.
Sometimes it presents multiple-choice options (“Do you prefer to implement this with a class-based or functional approach?”), while other times it simply asks for more context.
I’ve started prompting it to offer design options by default, which lets me keep my initial instructions broad and avoid micromanaging every decision.
This back-and-forth feels a lot like mentoring a junior developer who’s knowledgeable, fast, and focussed.

## General impressions

There’s no shortage of think pieces and demo videos about AI coding tools, so I'll be brief.
A**fter using Cursor hands-on for a week, my summary is simple: it’s really good.**
The interface feels thoughtfully designed, not a post-hoc infusion of AI into a pre-existing tool.
Plan Mode works as designed and is effective int turning my objectives into implementation.
*In short, and more importantly, it doesn’t disrupt my workflow – **it amplifies it.***

## Productivity

The most striking difference I’ve noticed isn’t the code quality, it’s how I feel after working intensely.
I follow the Time Block system advocated by Cal Newport, where I schedule every part of the day in 15- or 30-minute increments.
This helps me see how much time I truly spend in deep, focused work versus shallow tasks.

Normally, I can perform about 4–5 hours of deep work in a day before fatigue sets in.
Coding is cognitively demanding: juggling details, context-switching between documentation and implementation, solving edge cases, etc.
It’s fun but draining.

Last week, using Cursor, I was still doing 6–7 hours of focused development per day, but ended each day feeling surprisingly clear-headed.
I wasn’t dragging myself through the finish line Friday afternoon.
Instead, I wrapped up with energy left for my weekend.

### Why it matters

I could have done nearly everything Cursor did myself, and at first, I treated it like an intelligent autocomplete.
But the key difference was mental load.
Cursor offloaded a large share of micro-decisions and repetitive labor – things like building classes, remembering syntax details, or Googling an API pattern I’ve used before but since forgotten.

While the agent executed, I was free to think at a higher level: what to build next, how components fit together, and which features would provide the most value.
That freed mental bandwidth is what makes deep work sustainable.
Cursor didn’t just make me faster, it staved off fatigue by offloading implementation details, conserving the energy and focus it requires.

## Closing thoughts

After just one week, I’m both impressed and cautiously optimistic.
Tools like Cursor seem to be evolving from *assistants* into *partners*.
If this level of performance holds steady, I can easily see Cursor becoming something I use daily.
**For now, what excites me most is its potential for sustainable productivity: the ability to do more meaningful work each day without burning out.**
If that continues, I’ll gladly keep Cursor in my workflow.
