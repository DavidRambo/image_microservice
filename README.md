# Image Microservice

A FastAPI microservice for uploading and downloading images organized into albums.

Currently this is only intended for running locally.

## Setup

Create and activate a virtual environment and then install the dependencies.
There are different options to do so, as the dependencies are listed in `pyproject.toml`, `requirements.txt`, and `uv.lock`.
With pip:

```bash
pip install -r requirements.txt
```

With [uv](https://docs.astral.sh/uv/guides/projects/):

```bash
uv sync
```

Next, ensure the listed CORS URLs include the address of whatever client you'll be using to send requests.
These are listed as `str`s in `origins` in `app/main.py` and added to the app's middleware (look for the `app.add_middleware()` function call).

The app uses sqlite, which is part of Python's standard library, so the database will be taken care of by a setup script.

## Usage

To start the service, make sure a virtual environment is active with all dependencies installed, then, from the top-level directory, run:

```bash
fastapi run app/main.py
```

By default, fastapi runs on localhost port 8000.
The port can be set by passing `--port <PORT>` to the above command.

### Sequence Diagram

### Communication Contract

### OpenAI Docs and Manual Testing

To view the automated documentation and try out endpoints, add `/docs` to the URL in your browser.

## How it works

The service saves image files to disk in a directory specified by the `IMAGE_DIR` constant.
This directory is created upon startup if necessary.
A SQLite database is used to store data related to the images.
A row comprises a primary key `id`, an `album` identifier, whether the image is `starred` for its album, and a `filepath` to reference the file.

## TODO:

- [x] DELETE endpoint
- [x] Setup documentation
- [ ] Document endpoints
  - [ ] create image
  - [ ] delete image
  - [ ] get image
  - [ ] get album's starred image
  - [ ] get IDs for all images in an album
  - [ ] update which image is starred in an album
- [ ] UML diagrams
  - [ ] create image
  - [ ] delete image
  - [ ] get image
  - [ ] get album's starred image
  - [ ] get IDs for all images in an album
  - [ ] update which image is starred in an album

### If there's time

- [ ] Modularize `main.py`
- [ ] Check path operation function signatures
- [ ] Assess error handling
- [ ] Tests
- [ ] Move startup functions into an Alembic migration script.
