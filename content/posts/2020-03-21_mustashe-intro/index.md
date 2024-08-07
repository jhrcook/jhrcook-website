---
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "'mustashe'"
subtitle: ""
summary: "A simple system for saving and loading objects in R. Long running computations can be stashed after the first run and then reloaded the next time. Dependencies can be added to ensure that a computation is re-run if any of its dependencies or inputs have changed."
tags: [R, package]
categories: ["dev"]
date: 2020-03-21T12:41:48-04:00
lastmod: 2020-03-21T12:41:48-04:00
featured: false
draft: false
series: ["Caching in R"]
series_order: 1
---

The purpose of the ‘mustashe’ R package is to save objects that result
from some computation, then load the object from file the next time the
computation is performed. In other words, the first time a chunk of code
is evaluated, the output can be *stashed* for the next time the code
chunk is run.

‘mustashe’ can be installed from CRAN or from GitHub.

``` r
install.packages("mustashe")
```

``` r
# install.packages("devtools")
devtools::install_github("jhrcook/mustashe")
```

Check out the next post the see [how 'mustashe' works under-the-hood]({{<ref "posts/2020-03-22_mustashe-explained">}}).

## Basic example

Below is a breif example outlining the use of the primary function from
the package, `stash()`. First we must load the ‘mustashe’ library.

``` r
library(mustashe)
```

Say we are performing a long-running computation (simulated here using
`Sys.sleep()` to pause for a few seconds) that produces the object named
`x`. The name of the object to stash `"x"` and the code itself are
passed to `stash()` as follows. (I used the package
[‘tictoc’](https://cran.r-project.org/web/packages/tictoc/index.html)
to time the execution of the code.)

``` r
tic("long-running computation")

stash("x", {
  Sys.sleep(5)
  x <- 5
})
```

    #> Stashing object.

``` r
toc()
```

    #> long-running computation: 5.885 sec elapsed

‘mustashe’ tells us that the object was stashed, and we can see that `x`
was successfully assigned the value 5.

``` r
x
```

    #> [1] 5

Say we are done for the day, so we close RStudio and go home. When we
return the next day and continue on the same analysis, we really don’t
want to have to run the same computation again since it will have the
same result as yesterday. Thanks to ‘mustashe’, the code is not
evaluated and, instead, the object `x` is loaded from file.

``` r
tic("long-running computation")

stash("x", {
  Sys.sleep(5)
  x <- 5
})
```

    #> Loading stashed object.

``` r
toc()
```

    #> long-running computation: 0.217 sec elapsed

That’s the basic use case of ‘mustashe’\! Any issues and feedback can be
submitted [here](https://github.com/jhrcook/mustashe/issues). Continue
reading below for explanations of other useful features of ‘mustashe’.

### Why not use ’ProjectTemplate’s `cache()` function?

Originally I tried to use the `cache()` function from ‘ProjectTemplate’,
but ran into a few problems.

The first was, to use it without modification, I would need to be using
the ‘ProjectTemplate’ system for my whole analysis project. It first
checks if all of the expected directories and components are in place,
throwing an error when they are not.

``` r
ProjectTemplate::cache("x")
```

    #> Current Directory: R_playground is not a valid ProjectTemplate directory because one or more mandatory directories are missing.  If you believe you are in a ProjectTemplate directory and seeing this message in error, try running migrate.project().  migrate.project() will ensure the ProjectTemplate structure is consistent with your version of ProjectTemplate.
    #> Change to a valid ProjectTemplate directory and run cache() again.

    #> Error in .quietstop():

I then tried copying the source code for the `cache()` function to my
project and tweaking it to work (mainly removing internal checks for
‘ProjectTemplate’ system). I did this and thought it was working: on
the first pass it would cache the result, and on the second it would
load from the cache. However, in a new session of R, it would not just
load from the cache, but, instead, evaluate the code and cache the
results. After a bit of exploring the `cache()` source code, I realized
the problem was that ‘ProjectTemplate’ compares the current value of the
object to be cached with the object that is cached. Of course, this
requires the object to be in the environment already, which it is in a
‘ProjectTemplate’ system after running `load.project()` because that
loads the cache (lazily) into the R environment. I do not want this
behaviour, and thus the caching system used by ‘ProjectTemplate’ was
insufficient for my needs.

That said, I *heavily* relied upon the code for `cache()` when creating
`stash()`. This would have been far more difficult to do without
reference to ‘ProjectTemplate’.

## Features

There are two major features of the `stash()` function from ‘mustashe’
not covered in the basic example above:

1. ‘mustashe’ “remembers” the code passed to `stash()` and will
    re-evalute the code if it has changed.
2. Dependencies can be explicitly linked to the stashed object so that
    the code is re-evaluated if the dependencies change.

These two features are demonstrated below.

### ‘mustashe’ “remembers” the code

If the code that creates an object changes, then the object itself is
likely to have changed. Thus, ‘mustashe’ “remembers” the code and
re-evaluates the code if it has been changed. Here is an example, again
using ‘tictoc’ to indicate when the code is evaluated.

``` r
tic()
stash("a", {
  Sys.sleep(3)
  a <- runif(5)
})
```

    #> Stashing object.

``` r
toc()
```

    #> 3.013 sec elapsed

``` r
tic()
stash("a", {
  Sys.sleep(3)
  a <- runif(10)
})
```

    #> Updating stash.

``` r
toc()
```

    #> 3.012 sec elapsed

**However, ‘mustashe’ is insensitive to changes in comments and other
style-based adjustments to the code.** In the next example, a comment
has been added, but we see that the object is loaded from the stash.

``` r
stash("a", {
  Sys.sleep(3)
  # Here is a new comment.
  a <- runif(10)
})
```

    #> Loading stashed object.

And below is the code from a horrible person, but ‘mustashe’ still loads
the object from the stash.

``` r
# styler: off
stash("a", {
        Sys.sleep(    3  )

    # Here is a comment.

a=runif(  10  )      # Another comment
})
```

    #> Loading stashed object.

``` r
# styler: on
```

### Dependencies

Dependencies can be explcitly linked to an object to make sure that if
they change, the stashed object is re-evaluated. “Dependency” in this
case could refer to data frames that are used to create another
(e.g. summarising a data frame’s columns), inputs to a function, etc.

The following demonstrates this with a simple example where `x` is used
to calculate `y`. By passing `"x"` to the `depends_on` argument, when
the value of `x` is changed, the code to create `y` is re-evaluated

``` r
x <- 1

stash("y", depends_on = "x", {
  y <- x + 1
})
```

    #> Stashing object.

``` r
# Value of `y`
y
```

    #> [1] 2

The second time this is run without changing `x`, the value for `y` is
loaded from the stash.

``` r
stash("y", depends_on = "x", {
  y <- x + 1
})
```

    #> Loading stashed object.

However, if we change the value of `x`, then the code is re-evaluated
and the stash for `y` is updated.

``` r
x <- 100

stash("y", depends_on = "x", {
  y <- x + 1
})
```

    #> Updating stash.

``` r
# Value of `y`
y
```

    #> [1] 101

Multiple dependencies can be passed as a vector to `depends_on`.

``` r
stash("y", depends_on = c("x", "a"), {
  y <- x + a
})
```

    #> Updating stash.

### Unstashing and clearing stash

To round up the explanation of the ‘mustashe’ package, the stash can be
cleared using `unstash()` and specific stashes can be removed using
`unstash()`.

``` r
unstash("a")
```

    #> Unstashing 'a'.

``` r
clear_stash()
```

    #> Clearing stash.

-----

### Contact

Any issues and feedback on ‘mustashe’ can be submitted
[here](https://github.com/jhrcook/mustashe/issues). I can be reached
through the contact form on my [website](https://joshuacook.netlify.com)
or on Twitter [@JoshDoesa](https://twitter.com/JoshDoesa).
