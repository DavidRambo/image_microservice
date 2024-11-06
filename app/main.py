"""A FastAPI application for uploading and serving images.

Images are organized into albums.
Each album has associated with it a "starred" or "favorited" image.
"""

import secrets
import os
from typing import Annotated

import fastapi

import sqlalchemy
import sqlmodel
from sqlmodel import SQLModel, Field

from fastapi.middleware.cors import CORSMiddleware

IMAGES_DIR = "./images"


class ImageBase(SQLModel):
    album: int = Field(default=0, index=True)
    starred: bool = Field(default=False, index=False)


class Image(ImageBase, table=True):
    """Represents the Image table in the SQL database.

    Attributes:
        id: primary key
        album: album with which the image is associated
        starred: whether the image is the representative for its album
        filepath: location of the file on disk
    """

    id: int | None = Field(default=None, primary_key=True)
    filepath: str | None = Field(default=None)


class ImagePublic(ImageBase):
    """Fields of the Image model for public consumption.

    Attributes:
        id: non-Null identifier for an Image
    """

    id: int


class ImageUpdate(ImageBase):
    starred: bool = Field(default=False, index=False)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = sqlmodel.create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_images_dir():
    if not os.path.exists(IMAGES_DIR):
        os.mkdir(IMAGES_DIR)


def get_session():
    """A FastAPI dependency to yield a Session, which stores objects in memory.

    Yields:
        A Session for working with SQL db data.
    """
    with sqlmodel.Session(engine) as session:
        yield session


SessionDep = Annotated[sqlmodel.Session, fastapi.Depends(get_session)]


app = fastapi.FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Sets up the database on application startup."""
    # TODO: For production, have a migration script (Alembic).
    create_db_and_tables()
    create_images_dir()


@app.post("/album/{album_id}", response_model=ImagePublic)
async def create_image(
    album_id: int, img_upload: fastapi.UploadFile, session: SessionDep
):
    """Creates an image entry in the database.

    fastapi.UploadFile has the following attributes:
        filename: a str with the original file name that was uploaded
            e.g. myimage.jpg
        content_type: a str with the MIME type / media type such as image/jpeg
        file: a file-like object

    Args:
        album_id: identification of the album with which to associate the image
        img_upload: an image with filename metadata

    Returns:
        the image's id
    """
    # Validate file's media type.
    try:
        if not img_upload.content_type.startswith("image"):
            raise fastapi.HTTPException(status_code=406, detail="Invalid file type")
    except Exception:
        raise fastapi.HTTPException(status_code=400, detail="Invalid upload")

    # Generate filename from a hash of the file.
    file_ext: str = img_upload.content_type.split("/")[1]
    filename: str = secrets.token_hex(8) + "." + file_ext
    filepath = f"{IMAGES_DIR}/{filename}"

    # Determine whether this album already has a starred image.
    statement = sqlmodel.select(Image).where(
        Image.album == album_id and Image.starred is True
    )
    starred_results: sqlalchemy.ScalarResult = session.exec(statement)
    if starred_results.first() is None:
        star = True
    else:
        star = False

    # Create new Image for db entry.
    new_image: Image = Image(album=album_id, starred=star, filepath=filepath)

    # Save image file to disk.
    with open(filepath, "wb+") as f_obj:
        f_obj.write(img_upload.file.read())

    # Save to database.
    session.add(new_image)
    session.commit()

    session.refresh(new_image)
    return new_image


@app.delete("/images/{image_id}")
async def delete_image(image_id: int, session: SessionDep) -> dict[str, bool]:
    """Deletes the image with the given ID from the database.

    Args:
        image_id: primary key of the image to delete
        session: database Session

    Raises:
        fastapi.HTTPException: throws a 404 when image is not found

    Returns:
        success message
    """
    image = session.get(Image, image_id)
    if not image:
        raise fastapi.HTTPException(status_code=404, detail="Image not found")
    session.delete(image)
    session.commit()
    return {"ok": True}


@app.get("/album/{album_id}", response_model=list[ImagePublic])
async def get_album(album_id: int, session: SessionDep) -> list[ImagePublic]:
    """Returns all the images in the album along with their IDs.

    Args:
        album_id: identification of the album from which to retrieve images
    """
    images = session.exec(
        sqlmodel.select(Image).offset(0).limit(10).where(Image.album == album_id)
    )
    return images


@app.get(
    "/starred/{album_id}",
    response_class=fastapi.responses.FileResponse,
)
async def get_starred(album_id: int, session: SessionDep):
    """Returns the starred image in the identified album.

    Args:
        album_id: identification of the album from which to retrieve starred image.

    Returns:
        image file requested
    """
    # Execute query for the album's starred Image
    statement = sqlmodel.select(Image).filter_by(album=album_id, starred=True)
    img_entry: sqlalchemy.ScalarResult = session.exec(statement).first()
    if img_entry is None:
        raise fastapi.HTTPException(status_code=404, detail="No starred image found")

    # Get file extension for media type.
    file_ext = img_entry.filepath.split(".")[-1]

    return fastapi.responses.FileResponse(
        img_entry.filepath, media_type=f"image/{file_ext}"
    )


@app.patch("/starred/{album_id}")
async def set_starred(album_id: int, image_id: int, session: SessionDep):
    """Stars the image with the given id for the album.

    Args:
        album_id: identification of the album having an image set as starred
        image_id: identification of the image to star
    """
    # Retrieve the image to star to ensure it exists.
    image: Image = session.get(Image, image_id)
    if not image or image.album != album_id:
        raise fastapi.HTTPException(status_code=404, detail="Image not found")

    # Retrieve currently starred image (if any).
    statement = sqlmodel.select(Image).filter_by(album=album_id, starred=True)
    results: sqlalchemy.ScalarResult = session.exec(statement)
    prev_starred: Image = results.first()

    prev_starred.sqlmodel_update({"starred": False})
    session.add(prev_starred)
    session.commit()
    session.refresh(prev_starred)

    # Star the image.
    image.sqlmodel_update({"starred": True})
    session.add(image)

    # Commit changes to database.
    session.commit()
    session.refresh(image)
