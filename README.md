# Image Microservice

A FastAPI microservice for uploading and downloading images organized into albums.

Currently this is only intended for running locally.

## Setup

Create and activate a virtual environment and then install the dependencies listed in `pyproject.toml`.
With specific library versions specified in `uv.lock`, you can use [uv](https://docs.astral.sh/uv/guides/projects/) to install them:

```bash
uv sync
```

Next, ensure the listed CORS URLs include the address of whatever client you'll be using to send requests.
These are listed as `str`s in `origins` in `app/main.py` and added to the app's middleware (look for the `app.add_middleware()` function call).

That's it!
The app uses sqlite, which is part of Python's standard library, so the database will be taken care of by a setup script.

## Usage

To start the service, make sure a virtual environment is active with all dependencies installed, then, from the top-level directory, run:

```bash
fastapi run app/main.py
```

By default, fastapi runs on localhost port 8000.
The port can be set by passing `--port <PORT>` to the above command.

### OpenAI Docs and Manual Testing

To view the automated documentation and try out endpoints, add `/docs` to the URL in your browser.

## How it works

The service saves image files to disk in a directory specified by the `IMAGE_DIR` constant.
This directory is created upon startup if necessary.
A SQLite database is used to store data related to the images.
A row comprises a primary key `id`, an `album` identifier, whether the image is `starred` for its album, and a `filepath` to reference the file.

## TODO:

- [x] DELETE endpoint
- [x] Basic usage documentation
- [ ] Modularize `main.py`
- [ ] Check path operation function signatures
- [ ] Assess error handling
- [ ] Tests
- [ ] Move startup functions into an Alembic migration script.
