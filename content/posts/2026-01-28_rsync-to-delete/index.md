---
title: "Faster file deletion with rsync"
subtitle: "How to use rsync to quickly delete large files and directories."
summary: "This is just a quick post about a way I found in graduate school to quickly delete large amounts of data."
tags: ["Programming"]
categories: ["Dev"]
date: 2026-01-28T00:00:00-08:00
lastmod: 2026-01-28T00:00:00-08:00
featured: false
draft: false
showHero: true
---

## Introduction

As a bioinformatician, I often work with huge datasets – think terabytes of intermediate files, reads, or assemblies that I no longer need after a workflow run.
Back in graduate school, working on our High Performance Computing (HPC) cluster running Linux, I learned that deleting large directories with `rm -rf` could take far longer than expected.
It was slow enough that I’d sometimes submit the deletion as a separate compute job.

After some searching, I came across a tip suggesting an alternative: use `rsync`.
It may sound odd at first, since `rsync` is usually used for copying or syncing files, not deleting them – but it actually offers a clever shortcut for wiping out files multiple orders of magnitude faster.

{{< alert >}}
It should go without saying: **use caution when deleting data**.
Always double-check paths before running potentially destructive commands.
And never use `sudo` here unless you *really* know what’s happening.
{{< /alert >}}

## The `rsync` method

### What `rsync` is meant for

`rsync` was designed for efficiently syncing files and directories, especially over networks.
It compares differences between a source and destination and transfers only what’s needed.
But that same compare-and-sync mechanism also makes it excellent for *deleting* – by syncing your target directory with an empty one.

### Using `rsync` to delete data

Here’s how to do it safely and effectively.

Create an empty directory (this will act as the “template” for deletion):

```bash
mkdir /tmp/empty
```

Now, tell `rsync` to make your target directory (`/data/big-ol-directory`) match the empty one:

```bash
rsync -a --delete /tmp/empty/ /data/big-ol-directory/
```

`rsync` will go through `/data/huge_tmp` and remove everything that doesn’t exist in `/tmp/empty`, effectively deleting all files while leaving the directory itself intact.  

If you want to preview which files would be deleted before actually removing anything, run a dry-run:

```bash
rsync -a --delete --dry-run /tmp/empty/ /data/big-ol-directory/
```

That’s it!
This approach is typically faster than `rm -rf`, especially on file systems with heavy metadata overhead or when deleting many small files.

One nice bonus is that `rsync` gives you more predictable progress output and can handle tricky filenames or permissions cleanly.
