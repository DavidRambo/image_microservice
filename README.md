# Image Microservice

A FastAPI microservice for uploading and downloading images organized into albums.

## Setup

## Usage

## How it works

The service saves image files to disk in a directory specified by the `IMAGE_DIR` constant.
This directory is created upon startup if necessary.
A SQLite database is used to store data related to the images.
A row comprises a primary key `id`, an `album` identifier, whether the image is `starred` for its album, and a `filepath` to reference the file.

## TODO:

- [ ] DELETE endpoint
- [ ] Modularize `main.py`
- [ ] Check path operation function signatures
- [ ] Assess error handling
- [ ] Tests
- [ ] Move startup functions into an Alembic migration script.
