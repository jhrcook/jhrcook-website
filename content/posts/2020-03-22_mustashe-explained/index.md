---
title: "'mustashe' Explained"
subtitle: "An explanation of the caching system employed in 'mustashe'."
summary: "An explanation of the caching system employed in 'mustashe'."
tags: [R, package]
categories: ["dev"]
date: 2020-03-22T11:45:50-04:00
lastmod: 2020-03-22T11:45:50-04:00
featured: false
draft: false
series: ["Caching in R"]
series_order: 2
---

The purpose of the ‘mustashe’ R package is to save objects that result
from some computation, then load the object from file the next time the
computation is performed. In other words, the first time a chunk of code
is evaluated, the output can be *stashed* for the next time the code
chunk is run.

This post explains how ‘mustashe’ works. See the previous post for an [introduction to the package]({{<ref "posts/2020-03-21_mustashe-intro" >}}).

‘mustashe’ can be installed from CRAN or from GitHub.

``` r
install.packages("mustashe")
```

``` r
# install.packages("devtools")
devtools::install_github("jhrcook/mustashe")
```

## How ‘mustashe’ works

### Overview

The following is the actual code for the `stash()` function, the main
function of the ‘mustashe’ package. I have only added a few more
comments for clarification.

``` r
stash <- function(var, code, depends_on = NULL) {
    
    # Make sure the stashing directory ".mustashe" is available.
    check_stash_dir()
    
    # Deparse and format the code.
    deparsed_code <- deparse(substitute(code))
    formatted_code <- format_code(deparsed_code)

    # Make sure the `var` and `code` are not `NULL`.
    if (is.null(var)) stop("`var` cannot be NULL")
    if (formatted_code == "NULL") stop("`code` cannot be NULL")

    # Make a new hash table.
    new_hash_tbl <- make_hash_table(formatted_code, depends_on)

    # if the variable has been stashed:
    #     if the hash tables are equivalent:
    #         load the stored variable
    #     else:
    #         make a new stash
    # else:
    #     make a new stash
    if (has_been_stashed(var)) {
        old_hash_tbl <- get_hash_table(var)
        if (hash_tables_are_equivalent(old_hash_tbl, new_hash_tbl)) {
            message("Loading stashed object.")
            load_variable(var)
        } else {
            message("Updating stash.")
            new_stash(var, formatted_code, new_hash_tbl)
        }
    } else {
        message("Stashing object.")
        new_stash(var, formatted_code, new_hash_tbl)
    }

    invisible(NULL)
}
```

Overall, I believe the logic is quite simple. The steps that the
`stash()` function follows, further explained in the following sections,
are:

1. Deparse and format the code.
2. Make a hash table based on the code and dependencies.
3. If the object has previously been stashed, then the new hash table
    and the stashed one are compared. If they are the same, then the
    object is loaded from memory.
4. If the hash tables are different or the object has never been
    stored, then the code is evaluated and the object and its hash table
    are stashed.

### Deparsing and formatting code

The first step taken by the `stash()` function is to deparse and format
the code.

Deparsing the code means to turn the unevaluated expression into a
string. The deparsing is done by passing the code *immediately* to
`substitute()` and `deparse()`. This must be done immediately, else the
code will be evaluated. The `substitute()` function “returns the parse
tree for the (unevaluated) expression `expr`, substituting any variables
bound in env.”

``` r
substitute(x <- 1)
```

    #> x <- 1

The `deparse()` function “Turn\[s\] unevaluated expressions into
character strings.” Paired with `substitute()`, it returns a string of
the unevaluated code.

``` r
deparse(substitute(x <- 1))
```

    #> [1] "x <- 1"

With the code now as a string, it is formatted using the `tidy_source()`
function from
[‘formatR’](https://cran.r-project.org/web/packages/formatR/index.html).
An internal function in ‘mustashe’, `format_code()` handles this
process:

``` r
format_code <- function(code) {
  fmt_code <- formatR::tidy_source(
    text = code,
    comment = FALSE,
    blank = FALSE,
    arrow = TRUE,
    brace.newline = FALSE,
    indent = 4,
    wrap = TRUE,
    output = FALSE,
    width.cutoff = 80
  )$text.tidy
  paste(fmt_code, sep = "", collapse = "\n")
}

format_code("x <- 2")
```

    #> [1] "x <- 2"

The purpose of formatting the code is so any stylistic changes to the
`code` input do not affect the hash table. To demonstrate this, notice
how the output from `format_code()` is the same between the two
different code examples.

``` r
format_code("x=2")
```

    #> [1] "x <- 2"

``` r
format_code(("x <- 2  # a comment"))
```

    #> [1] "x <- 2"

### Making a hash table

The hash table is a two-column table with the name and hash value of the
code and any (optional) dependencies.

The hashing is handled by the
[‘digest’](https://cran.r-project.org/web/packages/digest/index.html)
package. It takes a value and reproducibly produces a unique hash value.

``` r
digest::digest("mustashe")
```

    #> [1] "ac2aad9fdb730500c56009bff6154a7e"

A hash value is made for the code and for any of the dependencies linked
to the object. This process is handled by the `make_hash_table(code,
depends_on)` internal function.

### Comparing hash tables

To tell if the code or dependencies have changed, the new hash table and
stashed hashed table are compared. The function underlying this process
is `all.equal()` from base R. This function compares two objects and “If
they are different, \[a\] comparison is still made to some extent, and a
report of the differences is returned.”

Here is an example of using `all.equal()` to compare two data frames.

``` r
# Two data frames with a small difference     *
df1 <- data.frame(a = c(1, 2, 3), b = c(5, 6, 7))
df2 <- data.frame(a = c(1, 2, 3), b = c(5, 6, 8))

# When the two data frames are equivalent.
all.equal(df1, df1)
```

    #> [1] TRUE

``` r
# When the two data frmaes are not equivalent.
all.equal(df1, df2)
```

    #> [1] "Component \"b\": Mean relative difference: 0.1428571"

A word of caution, if using `all.equal()` for a boolean comparison (like
in an if-statement), make sure to wrap it with `isTRUE`, otherwise it
will return `TRUE` or comments on the differences, but not `FALSE`.

### Evaluating code and making a stash

If the hash tables are different, that means the code must be evaluated,
the new object be assigned to the desired name (`var`), and the new hash
table and value stashed. This is handled by the internal function
`new_stash()`.

``` r
# Make a new stash from a variable, code, and hash table.
new_stash <- function(var, code, hash_tbl) {
  val <- evaluate_code(code)
  assign_value(var, val)
  write_hash_table(var, hash_tbl)
  write_val(var, val)
}
```

The first step is to evaluate the code with the `evaluate_code(code)`
function. It uses the `parse()` and `eval()` functions and returns the
resulting value.

``` r
# Evaluate the code in a new environment.
evaluate_code <- function(code) {
  eval(parse(text = code), envir = new.env())
}
```

This value is then assigned the desired name in the global environment
using the internal `assign_value(var, val)` function, where `.TargetEnv`
is a variable in the package pointing to `.GlobalEnv`.

``` r
# Assign the value `val` to the variable `var`.
assign_value <- function(var, val) {
  assign(var, val, envir = .TargetEnv)
}
```

Lastly, the hash table and value are written to file using wrapper
functions around `readr::write_tsv()` and `saveRDS()`.

-----

### Contact

Any issues and feedback on ‘mustashe’ can be submitted
[here](https://github.com/jhrcook/mustashe/issues). I can be reached
through the contact form on my [website](https://joshuacook.netlify.com)
or on Twitter [@JoshDoesa](https://twitter.com/JoshDoesa).
