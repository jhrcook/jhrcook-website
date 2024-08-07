---
title: "Sudoku Solver"
summary: "A web application that solves [Sudoku puzzles] using linear integer programming."
tags: ["Python", "programming", "app", "data analysis"]
categories: ["Data Science"]
date: 2020-12-31T08:37:28-08:00
---

{{< button href="https://streamlit-sudoku-solver.herokuapp.com/" target="_blank" rel="noopener noreferrer" >}}
  {{< icon "link" >}} Web App
{{< /button >}}
&ensp;
{{< button href="https://github.com/jhrcook/streamlit-sudoku" target="_blank" rel="noopener noreferrer" >}}
  {{< icon "github" >}} Source
{{< /button >}}

A web application that solves [Sudoku puzzles](https://en.wikipedia.org/wiki/Sudoku).
The user inputs the known values in the grid, clicks the *Solve* button, and the solution is displayed below almost instantly.
The web application is built using [Streamlit](https://www.streamlit.io/) and the solving engine uses the optimization library ['Pyomo'](https://www.pyomo.org/).

<img src="assets/demo.gif" width="95%">
