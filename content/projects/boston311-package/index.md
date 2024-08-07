---
title: "boston311"
summary: "Python package for interfacing with Boston 311 API."
authors: ["admin"]
tags: ["Python", "programming", "package"]
categories: ["Dev"]
date: 2021-08-15T08:00:00-00:00
draft: false
---

{{< button href="https://github.com/jhrcook/boston311" target="_blank" rel="noopener noreferrer" >}}
  {{< icon "github" >}} Source
{{< /button >}}
&ensp;
{{< button href="https://jhrcook.github.io/boston311" target="_blank" rel="noopener noreferrer" >}}
  {{< icon "circle-info" >}} Doc
{{< /button >}}
&ensp;
{{< button href="https://pypi.org/project/boston311/0.1.1/" target="_blank" rel="noopener noreferrer" >}}
  {{< icon "link" >}} PyPI
{{< /button >}}

I recently made a request to have some graffiti removed by the city of Boston and used their 311 service for reporting non-emergency crimes. I found it an interesting service and decided to look closer into it. They provide an free API for the service, so I decided to make this Python package to interface with the API.

Below are features of this package:

1. Get a collection of all services offered by Boston 311.
2. Get a collection of all service requests with some useful filters.
3. Get information for a specific service request.

All underlying data models were **parsed and validated with ['pydantic'](https://pydantic-docs.helpmanual.io/)** so there is increased type safety and helpful hints for your IDE.

**Use the links at the top of the page to check out the source code, documentation, or find the package on PyPI.**
