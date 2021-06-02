# Fnatic Match Tracker
#### Video Demo: https://youtu.be/c4hWznfM-tI

## Description

A simple table that shows all upcoming Fnatic esports matches across League of Legends, Valorant, CSGO, Rainbow 6 and Dota 2.

Users can register for accounts to customise which titles they want to see on registration, and update their account settings accordingly.

## Files Overview

There are several HTML pages, and a couple of Python files in here for the website itself. app.py contains all of the routing, API calls and display functions that handle website activity.

There is a database for the users and the accounts created, and a folder of HTML templates, CSS styles and additional files such as fonts and images.

I used custom fonts for the headers, and adapted Bootstrap's default styles to create a dark Fnatic theme for the site.

There is a custom error page as well, which shows an image and displays the error encountered when a user does something they're not supposed to.

## App.py

App.py is the main server document that routes traffic, performs back end functions and generates the data. It first initialises a session, then listens for routing instructions.

# Index

The index route connects to the database to get a user's settings if they are logged in, then populates the matches array from API data based on the titles the user has told us they are interested in. The matches array is passed to the index.html file via Flask.

If a user is not logged in, it generates all matches from all titles, and prompts index.html to display a message asking the user to log in.

If there are no matches to display, the page will ask the user to check their settings.

# Log In/Register

Users can register accounts via the Register page, then log in via the Log In page. These pages are simple forms that query or update the database with user information to verify their credentials. Passwords are hashed and unhashed using Flask's algorithms called from helpers.py.

# Settings

Users can change their passwords or update their game information via the Settings page. This page checks the current user's settings and displays the correct existing game settings through the checkboxes, and allows users to change and update these via the user info database. They can also change passwords on the same page, which are validated as being the same and also valid length.

## Why is this useful?

As a fan of Fnatic, I want to see when and where all of the teams are playing in one place. Because titles and communities are often segregated, it means I often need to check five or six different sites to be able to see when and where teams are playing.

## What technology did I use?

The server is built on Python, with Flask being the framework for routing HTTP requests and displaying responsive content. There is some JavaScript in there as well for front-end sorting, and I used Bootstrap as my front end HTML library.

I used SQLite for the database, and the Pandascore API to be able to get live match data.

## Why make this?

I made this as my final project for Harvard's CS50 Introduction to Computer Science course.
