---
title: "Using a progress bar while multiprocessing in Python"
subtitle: "How to effectively use a progress bar while multiprocessing in Python."
summary: "Spreading out computation is made simple in Python with the built-in `multiprocessing` module. Yet, it is not immediately obvious how to effectively portray the completion status in a progress bar. In this brief tutorial, I demonstrate how to easily and accurately display the progress of a multiprocessing pool."
tags: ["tutorial", "python"]
categories: ["dev"]
date: 2024-06-23T08:09:00-05:00
lastmod: 2024-06-23T08:09:00-05:00
featured: false
draft: false
showHero: true
---

## Introduction

This is just a simple post to demonstrate how one can use a progress bar with the built-in [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html) module.
**See the bottom of the post for a [video](#video) of the results using the various method discussed in the text.**
Note, that this method only works if the order of execution is irrelevant, that is, the operations are independent and the order of the output is unimportant.

## Progress bar and multiprocessing

> The following code snippets are incomplete, but I have provided the [full script](#complete-code) at the bottom.

### Time-consuming function

For demonstration purposes, I've created the function `slow_add_one()` that returns the input value plus 1 after waiting for a duration that is one-third the seconds of the input.

```python
def slow_add_one(x: float) -> float:
    time.sleep(x / 3)
    return x + 1
```

### `map()`

Multiprocessing can be used to iterate over input values, spreading the computation across multiple cores (in the examples here, I use 5 processes).
To track the progress of the operations, I used the [tqdm](https://tqdm.github.io) library to provide a progress bar (though this should work with other progress bar libraries).

The following operation works, but the progress bar is pointless because [`map()`](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.map) only returns once all of the processes have completed.

```python
from multiprocessing import Pool
from tqdm import tqdm

inputs = [1, 2, 3]
res = []
with Pool(5) as p:
    for r in tqdm(p.map(slow_add_one, inputs), total=len(inputs)):
        res.append(r)
```

### `imap_unordered()`

One solution is to use [`imap()`](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.imap) instead which returns results in order as processes finish.
One restriction, though, is that if later processes finish first, they will not register in the progress bar until all of the preceding processes complete.
If the order of the outputs is critical to your program, then a functional progress bar would require a more complicated solution.
Instead, if the order is *irrelevant*, then the related [`imap_unordered()`](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.imap_unordered) method can be used as it returns results as the processes finish, regardless of the order.

```python
res = []
with Pool(5) as p:
    for r in tqdm(p.imap_unordered(slow_add_one, inputs), total=len(inputs)):
        res.append(r)
```

### Video

Below is a demonstration of what the progress bar looks like using these methods (single-process `map()`, multiprocessing `map()`, multiprocessing `imap()`, and multiprocessing `imap_unordered()`).
Note that the input values are arranged in descending order so that the first tasks take longer, rendering the progress bar uninformative for the multiprocessing `map()` and `imap()`.

<script src="https://asciinema.org/a/oR0oqrcV83C85DXyYtYvY7Ysq.js" id="asciicast-oR0oqrcV83C85DXyYtYvY7Ysq" async="true"></script>

Before finishing, it is worth noting that there are more complicated solutions to this problem, especially if the order of the outputs is required.
Yet, this solution covers many of the cases that I come across so it's simplicity is rather valuable.

---

## Complete code

Below is the full script I used for the above demonstrations.

{{< details "<i>Click to reveal/hide code</i>" >}}

```python
#!/usr/bin/env python3

"""Demonstration of using a progress bar when multiprocessing."""

import time
from collections.abc import Sequence
from multiprocessing import Pool
from typing import Final

from rich import print
from tqdm import tqdm

N_PROCESSES: Final[int] = 5


def slow_add_one(x: float) -> float:
    time.sleep(x / 3)
    return x + 1


def single_process_example(inputs: Sequence[float]) -> None:
    print("Example using single-process `map()`:")
    tic = time.perf_counter()
    res = []
    for r in tqdm(map(slow_add_one, inputs), total=len(inputs)):
        res.append(r)
    toc = time.perf_counter()
    print(f"Result: {res}")
    print(f"(Took {toc-tic:.3f} sec.)")


def map_example(inputs: Sequence[float]) -> None:
    print("Example using multi-process `map()`:")
    tic = time.perf_counter()

    res = []
    with Pool(N_PROCESSES) as p:
        for r in tqdm(p.map(slow_add_one, inputs), total=len(inputs)):
            res.append(r)

    toc = time.perf_counter()
    print(f"Result: {res}")
    print(f"(Took {toc-tic:.3f} sec.)")


def imap_example(inputs: Sequence[float]) -> None:
    print("Example using multi-process `imap()`:")
    tic = time.perf_counter()

    res = []
    with Pool(N_PROCESSES) as p:
        for r in tqdm(p.imap(slow_add_one, inputs), total=len(inputs)):
            res.append(r)

    toc = time.perf_counter()
    print(f"Result: {res}")
    print(f"(Took {toc-tic:.3f} sec.)")


def imap_unordered_example(inputs: Sequence[float]) -> None:
    print("Example using multi-process `imap_unordered()`:")
    tic = time.perf_counter()

    res = []
    with Pool(N_PROCESSES) as p:
        for r in tqdm(p.imap_unordered(slow_add_one, inputs), total=len(inputs)):
            res.append(r)

    toc = time.perf_counter()
    print(f"Result: {res}")
    print(f"(Took {toc-tic:.3f} sec.)")


def main() -> None:
    inputs = list(reversed(range(1, 6)))
    print(f"Number of cores: {N_PROCESSES}")
    print(f"Inputs: {inputs}")
    single_process_example(inputs)
    map_example(inputs)
    imap_example(inputs)
    imap_unordered_example(inputs)


if __name__ == "__main__":
    main()
```

{{< /details >}}
