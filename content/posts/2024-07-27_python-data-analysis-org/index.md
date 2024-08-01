---
title: "How I use Python to organize my data analyses"
subtitle: "A description of how I structure my data analyses with Python to increase flexibility, bug-detection, and ease-of-use."
summary: "This is a description of how I use Python in my data analyses, a system that has evolved over 7 years of a computational biology Ph.D. and working in industry."
tags: ["data analysis", "python"]
categories: ["data science"]
date: 2024-07-27T08:09:00-05:00
lastmod: 2024-07-27T08:09:00-05:00
featured: false
draft: false
showHero: true
---

## Introduction

Over the 7 years as a computational biologist in academia and industry, the structure and organization of my data analysis projects has evolved.
I need to perform interactive analyses in notebooks, execute command line tools, submit jobs to a high-performance computing (HPC) cluster, and anything else required to get answers to questions my team needs to advance a work stream.
Importantly, the must be documented, trustworthy, and reproducible.
Thus, my system has adapted to these constraints and challenges over the years, and below, I describe my Python package-centric method developed to meet these needs.

## My system

The system I employ is centered around creating and developing a Python package *within* the analysis – that is, each analysis gets its own Python package that is developed and used during the research process.
The *how's* and *why's* of this are explained below.

### Virtual environment

Creating a virtual environment for a project is generally good practice and essential for the system described here.
Working on my company's HPC cluster, I don't have full control over software installation including the versions of Python, so I use ['conda'](https://docs.conda.io/en/latest/) (well actually ['mamba'](https://mamba.readthedocs.io/en/latest/index.html), but really ['micromamba'](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) because I don't need all of the features) to create the virtual environment and install my desired version of Python.[^1]
'Conda' allows for the installation of not just Python libraries, but other software packages that I may need (e.g. sequence alignment tools that are often written in C).

[^1]: Of course, Docker could be used here, but it is not installed on my company's HPC cluster (nor on Harvard Medical School's when I was doing my Ph.D.) so I've never had the opportunity to try. Anyway, since it is a walled-garden, I'm not sure how well it would behave with external dependencies such as other data directories, ['module' systems](https://hpc-wiki.info/hpc/Modules), or task schedulers (e.g. [Slurm](https://slurm.schedmd.com/overview.html) or [SGE](https://docs.oracle.com/cd/E19279-01/820-3257-12/n1ge.html)).

By default 'conda' keeps virtual environments in a single location and users reference them by name.
I instead prefer to have the virtual environment physically within the project, so I use a command like the following to create a virtual environment:

```bash
micromamba env create -p "./.venv" -c conda-forge "python=3.11"
micromamba activate -p "./.venv"
```

Within the 'conda' environment, I then use ['uv'](https://astral.sh/blog/uv) to install Python libraries.
Briefly, 'uv' is a drop-in replacement (more or less) for 'pip,' but is *insanely* fast.
It also comes with `compile` and `sync` tools that help with environment management over the project's lifetime.

```bash
micromamba install -c conda-forge "uv"
uv pip install ... # whatever libraries you like
```

{{< alert "circle-info" >}}
**Tip:** Install ['ruff'](https://docs.astral.sh/ruff/) in the virtual environment and use it to format your code.
It is so fast and efficient, I set it as the tool to be used during "format-on-save" in my IDE without any noticeable slowdown.
{{< /alert >}}

### The project's Python package

Once a virtual environment is available, I then create a Python package specifically for this project.
While it sounds like a heavy lift, a Python package can be as simple as a directory with a "\_\_init\_\_.py" file.
There are many advanced features that can be used with a library, but I have found that starting simple and experimenting with these features over time keeps it from becoming overwhelming.

For fun, I usually name the package something completely arbitrary.
Lately, I've been naming them after [common fly fishing fly patterns](https://www.flytyer.com/15-trout-flies-must-tie/).

```bash
mkdir hares_ear
touch hares_ear/__init__.py
```

A comprehensive description of Python packaging is beyond the scope of this post, but using a tool like ['flit'](https://flit.pypa.io/en/stable/) can help with getting started.
Since I don't publish these packages to a packaging index (e.g. [PyPI](https://pypi.org)), I don't use tools like 'flit' anymore, instead I usually just copy a "pyproject.toml" file (more on this below) from a previous analysis and updating it for the current one.

After making the package's directory, I'll create the "pyproject.toml", the file that declares the metadata for the package.
Again, I won't go into all of the details, but below is an example of some basic metadata:

```toml
[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "hares_ear"
authors = [{name = "Joshua Cook", email = "my-email@mail.com" }]
classifiers = ["Private :: Do Not Upload"]
dynamic = ["version", "description"]
dependencies = [
    "jupyterlab", "matplotlib", "polars", ...
]

[project.optional-dependencies]
dev = [
    "ruff", "mypy", "ptpython", ...
]
```

The purpose of most of the sections are clear from their name.
The `dependencies` is a list of Python packages to be installed along with this package.
In addition, optional dependencies can be included with keywords during the install by creating sections within `[project.optional-dependencies]`.
In the example above, I added the optional `dev` which results in the installation of developer tools that are not required for the analysis, but are nice to have while working on it.

The next step is to install this package into the project's virtual environment.
**The key is to install it as "editable"** so that changes to the package are immediately available without having to re-install every time.

```bash
uv pip install -e '.[dev]'
```

It's really that simple.
Now the any code in "hares_ear/" can be used anywhere in the project (really anywhere as long as the virtual environment is activated).

```bash
python
>>> import hares_ear
```

**Now is a good time to switch from the "how" to the "why" – I think the above provides sufficient detail of the structure of the system to now describe *why* I create and install a Python package this way.**

The main reason for creating and installing a specific Python package for each analysis is that it will contain the "business logic" of the project in a single, reusable location.
The business logic in this case refers to standard procedures or data (e.g. constants or key file paths) that will be used throughout the project and need to be consistent in every use.
Keeping the business logic ["DRY"](https://en.wikipedia.org/wiki/Don't_repeat_yourself) is not just convenient, but *critical* to maintaining consistent practices throughout a data analysis.
(I discuss this more [below](#dont-repeat-yourself-dry).)

As an almost-trivial example, I often create a specific plot style for a project to maintain the consistency of figures.
I can place this code into a `set_style()` function in a `plots` module in my package to be called at the top of my analyses.

Alternatively, there could be a set of filtering and processing operations that you apply to certain data types that you want to use throughout a project.
Instead of copying a code block from one notebook to another (which I have seen many colleagues do), this logic can be refactored into a function and placed in a module of the package to be called from anywhere.
Further, this function can be parameterized with good default values to make it more general while keeping the logic in a single, known location.
Providing the function a descriptive name and a docstring are added benefits of this system that increase trust in the system and enhance reusability.

### Modules

A module in a package is a ".py" file within the package (these can be further organized into directories within the package, too).
You can add any module you think is useful for your project.
They are convenient for organization, but also assist in enforcing separation of concerns.
Below are some modules I include in most data analysis projects.

#### Command line Interface (CLI)

A command line interface (CLI) is now one of the first modules I create in an analysis' package.
This CLI is meant to act as an entrypoint to using the code contained in the package from the command line, usually in scripts (more on that below).

In it's simplest form, I'll create a module called `cli` (i.e. a file called "cli.py") and create a ['typer'](https://typer.tiangolo.com/tutorial/typer-command/) app within it.
This has the following general structure:

```python
"""Command line interface."""

from typer import Typer

app = Typer()

@app.command()
def hello_world() -> None:
    """Says hello."""
    print("Hello, world.")
```

In this case, I create the singleton `app` object and give it an example command function `hello_world()`.
Again, a complete description of ['typer'](https://typer.tiangolo.com/tutorial/typer-command/) is beyond the scope of this article, and is simply unnecessary with the high-quality documentation already provided.
It's a great tool, especially if you use type hints, so I highly recommend checking it out.

The command line entrypoint can now be added to the "pyproject.toml":

```toml
[project.scripts]
"ha" = "hares_ear:cli.app"
```

and called from the command line:

```bash
ha --help
```

Note, you will need to re-install the library using the same command as used before.

#### Paths

This is a simple module, usually called `paths` (that is, a file called "paths.py") that just contains paths to standard directories, data files, etc.
A trick I have found to make this module exceptionally useful is to include a way to reference the root directory of the analysis.[^2]
This is useful because I can create a function to give me the path to, say, the "outputs" directory from a notebook without having to worry about the path of the notebook.
This may seem trivial, but removes the need to worry about breaking hard-coded file paths when moving around notebooks or scripts.

[^2]: I have a simple library that already does this that I may publish publicly someday...

#### Project enums

Enum's are not as popular in Python as they are in strongly-typed languages such as Rust or Swift, but when I got used to them when learning these languages, they were such a useful concept.
I won't expand on them here, but I recommend [reading](https://docs.python.org/3/library/enum.html) up on them.
They pair well with the ethos of this package-centric system, and I therefore often have a `project_enums` module.

### Coding practice recommendations

Below are just some comments on good coding practices, specifically on those that take advantage of the structure and features of this package-centric system.

#### Don't Repeat Yourself (DRY)

The principle ["Don't Repeat Yourself"](https://en.wikipedia.org/wiki/Don't_repeat_yourself) (DRY), famously introduced in [*The Pragmatic Programmer*](https://en.wikipedia.org/wiki/The_Pragmatic_Programmer), is meant to retain a single source of truth for all knowledge.
Importantly, the term "knowledge" is meant very much in the Information Theoretic sense of anything that provides order.
This therefore applies to data, logic, documentation, etc.
The key purpose of using a package-centric system is for the package to contain the sources of truth referenced throughout your analysis.
The DRY principle is critical in all software, and using this system making heeding it possible during the iterative and, at times, messy process of data analysis.

#### Reduce coupling / separation of concerns

Reducing dependencies in code is helpful by making code more generally usable in different scenarios.
The modules of the package can make achieving this easier by just giving functionalities a place to live.
Without a system to physically separate code, as is the case in a single, mile-long script, code can (will) become interdependent and making changes will be a nightmare of following this chain.
Instead, the option to create a module with a descriptive name, it's own data types and functions facilitates thinking of code in smaller, more manageable pieces.
Following this idealogy takes advantage of the package-centric system and results in easier code to debug, refactor, and modify.

#### Type hints

It's no secret that I [love]({{< relref "/tags/type-hinting/" >}}) type hints in Python.
I won't try to convert anyone here, but I will plug that using type hints can make reusing code far easier by enhancing a function's or class's API.
Further, the capabilities of modern developer tools in IDEs make great use of type hints when used in packages.

### The analysis

Thus far in this post, no actual data analysis has been performed.
The project's package contains the general, reusable code and the actual analyses executing one-off, specific computations are performed in two places: **scripts** and **notebooks**.
Each of these are described below.

In general, I document the execution of the scripts and notebooks in the project's "README.md" file.
This documentation includes any additional commands required (e.g. requesting an interactive session on a compute node of the HPC), the purpose of the command, and descriptions of any key input or output files.

#### Scripts

I have heard the term "script" used so generically that I will first define my use: "A standalone file of computer code that is executed by calling it from the command line."
So in the case of Python, a script is executed with:

```bash
python my-script.py
```

Importantly, scripts do not share code with each other, they only import Python libraries and modules.
Scripts have functions and classes, but their use is restricted to the script within which they are defined.
This does not necessarily have to be the case; in Python you can import code from any ".py" file.
But the reason I enforce this isolation is because changing code used by other scripts is dangerous.
Scripts aren't tested like a Python library can be and scripts are not amenable to the various refactoring tools of modern IDEs built for library development.
Therefore, my definition is perhaps more prescriptive than descriptive, but I find it aligns with the package-centeric system I have outlined in this post.

In my analyses, the scripts live in a "scripts/" directory.
They can be Python scripts, importing modules from the project's package.
Or they can be Shell scripts that using the CLI entrypoints.
These are great for cases where interaction is not necessary (otherwise notebooks, discussed below, are likely a better option) such as file management, data preparation, workflow execution, etc.

I find that I often develop code semi-interactively within a script and then refactor much of the functionality into the project's package for use elsewhere, cleaner more interpretable scripts, and  better documentation.
In general, I want the script to focus on the "what" (purpose of the script) and move the "how" (implementation) to modules in the package.

#### Notebooks

[Jupyter notebooks](https://jupyter.org) are a staple of the modern data analysis toolkit.
I usually keep these all in a "notebooks/" directory, opting for longer, descriptive file names than a nested directory structure to later traverse through.

{{< alert "circle-info" >}}
**Tip:** I organize the notebooks using a two-tired numbering system.
For instance, I could have the following notebooks "100-100_first-notebook.ipynb" and "100-110_another-notebook.ipynb".
The first number, "100" in this case, indicates these notebooks are related (generally, they are a set of notebooks to address a specific research question), and the second number, "100" and "110", indicate that the notebook "first-notebook" precedes "another-notebook".
Importantly, for the second number, the order doesn't necessarily suggest a dependency on data (i.e. outputs from the first are used in the second), but more often a dependency of logic, that is, findings in the first are required to understand the second.
This is a long note for a seemingly mundane concept, but I think it is rather powerful in what is gained from its simplicity.
{{< /alert >}}

Like the scripts discussed above, the project's package is imported into the notebook and the code used throughout.
As notebooks are often interactive and iterative, I usually build large chunks of code in the notebook and then refactor it to move into the package.
In addition to making the code reusable, this makes the notebook clean and concise, turning the focus to the results.

{{< alert "circle-info" >}}
**Tip:** Use the Jupyter magic commands `%load_ext autoreload` and `%autoreload 2` to be able to change the code in the package and immediately have it available in the notebook.
{{< /alert >}}

## Conclusion

I hope you found this system interesting, possibly even inspiring.
Feel free to ask questions in the comments section or leave additional recommendations!
