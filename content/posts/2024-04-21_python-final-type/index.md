---
title: "Caution when using Python's `Final` type hint on mutable objects."
subtitle: "The supported way to use Python type checkers to prevent against the mutation of mutable objects."
summary: "In the course of my work, I stumbled across a misconception I had about the `Final` type annotation. I perceived it to mean that the annotated object should not be mutated. In this post, I demonstrate how this is an incorrect understanding of the `Final` type hint and a better solution to get help from the type checker in these situations."
tags: ["tutorial", "python", "type hinting"]
categories: ["dev"]
date: 2024-04-21T07:30:13-05:00
lastmod: 2024-04-21T07:30:13-05:00
featured: false
draft: false
showHero: true
---

In some code I was writing for work, I ran into an issue where I wanted an immutable collection, specifically, a dictionary with values of sets of strings.
As a fan of type hints in Python, I tried to declare the following such that the dictionary and the nested set were type hinted as `Final` (the specifics of my example have been replaced with the names of Nobel Prize-winning biologists):

```python
from typing import Final

my_dict: Final[dict[str, Final[set[str]]]] = {
    "biologists": {"Arthur Kornberg", "Hermann Muller"}
}
```

but the static type checking ['mypy'](https://www.mypy-lang.org) threw the following error:

```text
script.py:9: error: Final can be only used as an outermost qualifier in a variable annotation  [valid-type]
```

(Note that `script.py:9` is just the name of my python file and line of the error).
Basically, this was an invalid type hint; the `Final` annotation can only be on the very outside of the type hint.[^1]

[^1]: An exception to this is that other type qualifiers (e.g. `Annotation`) can wrap `Final`.

So I removed the internal `Final` and, to test my mental model of the `Final` type, I tried to add a name to the set in the dictionary, hoping 'mypy' would catch this:

```python
my_dict: Final[dict[str, set[str]]] = {
    "biologists": {"Arthur Kornberg", "Hermann Muller"}
}
my_dict["biologists"].add("Daniel Nathans")
```

But 'mypy' had no issue with this.

As a simple demonstration that 'mypy' recognized the `Final` type at all, I executed the tool on the following snippet:

```python
# Mutable variable, should not elicit a warning.
str1: str = "Arthur Kornberg"
str1 = "Hermann Muller"

# Final variable, should raise a warning.
str2: Final[str] = "Arthur Kornberg"
str2 = "Hermann Muller"
```

which induced the following error, as expected:

```text
script.py:28: error: Cannot assign to final name "str2"  [misc]
```

These examples made me reconsider the behavior of the `Final` type hint.
What specifically does it indicate to the type checkers, and what does this mean for how it should be employed to prevent logic errors in code?

The [documentation](https://typing.readthedocs.io/en/latest/spec/qualifiers.html#uppercase-final) for `Final` provides the following definition,

> The `typing.Final` type qualifier is used to indicate that a variable or attribute should not be reassigned, redefined, or overridden.

Further down, the documentation notes,

> > Note that declaring a name as final only guarantees that the name will not be re-bound to another value, but does not make the value immutable.

followed by the helpful suggestion,

> Immutable ABCs and containers may be used in combination with Final to prevent mutating such values.

In essence, this means that `Final` protects the *binding of the variable name in the scope*.
That is, a variable name annotated as `Final` will not be assigned to a new object in the function, method, etc. in which it is declared.
Importantly, this does not indicate that the object itself won't change; *if it's mutable (like a dictionary or set) then the value may change still.*
Therefore, the ideal solution is, when an immutable object is desired, an immutable class should be used.
For example, a tuple (immutable) instead of a list (mutable).

But sometimes, I want the properties of a specific class (e.g. the uniqueness guarantee of a set), but don't want to have to create (and then maintain) a new class with this functionality.
In this case, an option is to employee a more opaque Abstract Base Class as the type hint.
For example, looking through the ABCs in the [`collection` module](https://docs.python.org/3/library/collections.abc.html#module-collections.abc) I can modify my example to the following:

```python
from collections.abc import Collection
from typing import Final

my_dict: Final[dict[str, Collection[str]]] = {
    "biologists": {"Arthur Kornberg", "Hermann Muller"}
}
```

I chose `Collection` because it indicates that the collection object is sized and iterable, but does not guarantee a an ordering (the key properties of a set that I want in this case).
The dictionary still contains values of type set, but because of the type annotation as `Collection`, the following attempt to modify the value in the dictionary raises an error from 'mypy':

```python
my_dict["biologists"].add("Daniel Nathans")
```

```text
script.py:34: error: "Collection[str]" has no attribute "add"  [attr-defined]
```

So, in conclusion, while this has a feeling of ["security through obscurity,"](https://en.wikipedia.org/wiki/Security_through_obscurity) the recommended type hinting solution to protecting against the mutation of mutable objects is to use immutable ABC annotations.
