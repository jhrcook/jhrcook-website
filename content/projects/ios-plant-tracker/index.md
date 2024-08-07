---
title: "Plant Tracker iOS App"
summary: "An app to help my mom keep track of and care for her plants."
tags: ["iOS", "Swift", "app", "programming"]
categories: ["Dev"]
date: 2019-08-12T11:55:41-04:00
draft: false
---

{{< button href="https://github.com/jhrcook/PlantTracker" target="_blank" rel="noopener noreferrer" >}}
  {{< icon "github" >}} Source
{{< /button >}}

## Purpose

The goal of this iOS application is to help the user (my mom) care for his/her plants. To this end it will record when the user last watered each plant, have their specific seasons (eg. growing or dormant seasons), and provide useful links for further care information. There is also a section where the user can take notes on each specimen. In addition, it will record the progress of each plant by storing and ordering their photos.

## Design and layout

### Library

The app will be divided into multiple tabs. The first is the Library, a collection of all the types of plants that the user has encountered and documented. There is only one entry per plant type which will hold general information on the plant.

### Collection

The Collection tab will hold all of the plants owned by the user. Whereas the Library entries were referencing the general plant variety, the collection holds specific plant specimens. Therefore, along with general care information, there will also be information specific to the plant such as when it was last watered and from who and when it was acquired.

### To-Do

The third tab will hold the To-Do list for the garden. A specific feature that will be quite handy is that specific To-Do's can be linked to specific plants in Collection. Also, notifications to water plants will be automatically added here.

## Current status

This app is very much in production. I am still working on the Library tab, though it is almost far enough along to begin working on the Collection tab.

You can check out the up-to-date status of this app at it's GitHub repository linked at the top.

{{< youtubeLite id="lqPm9C2KUbU" label="App demo" >}}
