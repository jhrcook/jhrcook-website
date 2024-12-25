---
title: "Adding execution environment metadata to a Jupyter notebook with 'watermark'"
subtitle: "How this simple tool can automagically add time stamps, library versions, git information, and more to a Jupyter notebook at runtime."
summary: "This is a short post to introduce a tool for Jupyter notebooks called 'watermark.' I use it to add metadata about the execution environment to my notebooks with a simple IPython magic command."
tags: ["data analysis", "python"]
categories: ["tools"]
date: 2024-12-25T09:00:00-05:00
lastmod: 2024-12-25T09:00:00-05:00
featured: false
draft: false
showHero: true
---

This is a brief write-up to introduce a delightful tool for Jupyter notebooks, ['watermark.'](https://github.com/rasbt/watermark)

{{< github repo="rasbt/watermark" >}}

Per the project's README, 'watermark' is "An [IPython magic extension](https://ipython.readthedocs.io/en/stable/interactive/magics.html) for printing date and time stamps, version numbers, and hardware information."
You simply add a couple of lines of code to a Jupyter notebook to automatically include key metadata of it's execution.
Below is an example output (from a notebook exported to Markdown and rendered on GitHub):

![Watermark demo](./watermark-demo.jpg)

There are various configuration options for the tool (and it can be used as an imported library in the Python session itself), but I personally decided to just find something that works for me and add it as a snippet in Visual Studio Code:

```json
{
 "notebook watermark": {
  "prefix": "watermark",
  "body": [
   "%load_ext watermark",
   "%watermark -d -u -v -iv -b -h -m",
  ],
  "description": "Standard watermark incantation."
 },
 ...
}
```

'watermark' is a simple, focused tool I use in all my Jupyter notebooks.
I hope you found this quick post useful and have a very merry Christmas!
