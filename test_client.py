import json
import requests
import os

from pathlib import Path


IMG_DIR = Path.joinpath(Path.home(), "Downloads")
SERVICE_URL = "http://localhost:8000/"


def add_image(album_id: int, img_path: str):
    """Submits a POST request to the server along with an image file."""
    files = {"img_upload": ("stand-in filename", open(img_path, "rb"), "image/jpeg")}
    server = SERVICE_URL + f"images/album/{album_id}"
    res = requests.post(server, files=files)

    print("Status code: ", res.status_code)
    print("Response text: ", json.dumps(res.json(), indent=2))


def get_album_images(album_id: int) -> list[dict]:
    """Retrieves rows for every image associated with the given album."""
    server = SERVICE_URL + f"images/album/{album_id}"
    res = requests.get(server)
    return res.json()


def open_starred_image(album_id: int) -> None:
    server = SERVICE_URL + f"images/album/{album_id}/starred"
    res = requests.get(server)

    with open("starred.jpeg", "wb") as f:
        f.write(res.content)

    os.system("open starred.jpeg")


def open_image_by_id(image_id: int) -> None:
    server = SERVICE_URL + f"images/{image_id}"
    res = requests.get(server)

    with open("image.jpeg", "wb") as f:
        f.write(res.content)

    os.system("open image.jpeg")


def set_starred_image(album_id: int, image_id: int) -> int:
    """Sets the given album's starred image to the given image id.

    Returns the response status code.
    """
    server = SERVICE_URL + f"images/album/{album_id}/starred"
    res = requests.patch(server, params={"image_id": image_id})
    return res.status_code


def delete_image(image_id) -> None:
    """Deletes the given image from the server."""
    server = SERVICE_URL + f"images/{image_id}"
    res = requests.delete(server)
    if res.status_code != 204:
        print("There was a problem with deleting that image.")
        print(res.text)


def remove_all_images(album_id: int):
    """Removes all images in the given album."""
    # Retrieve all image IDs for the album.
    data: list[dict] = get_album_images(album_id)
    for row in data:
        delete_image(row["id"])


if __name__ == "__main__":
    print(">>> Removing all images associated with album 3...")
    remove_all_images(3)
    _ = input("\nPress Enter to continue...\n")

    print(">>> Adding a new image to album 3...")
    add_image(3, Path.joinpath(IMG_DIR, "mocha_jake.jpeg"))
    _ = input("\nPress Enter to continue...\n")

    print(">>> Adding a second image to album 3...")
    add_image(3, Path.joinpath(IMG_DIR, "strawflower.jpeg"))
    _ = input("\nPress Enter to continue...\n")

    print(">>> Adding a third image to album 3...")
    add_image(3, Path.joinpath(IMG_DIR, "ka_blood_orange.jpeg"))
    _ = input("\nPress Enter to continue...\n")

    print(">>> Retrieving row data for images associated with album 3...")
    data = get_album_images(3)
    print(json.dumps(data, indent=4))

    img_id = input("\nEnter the id of an image to view: ")
    open_image_by_id(img_id)
    _ = input("\nPress Enter to continue...\n")

    print(">>> Opening the starred image of album 3...")
    open_starred_image(3)
    _ = input("\nPress Enter to continue...\n")

    print(">>> Changing the starred image of album 3...")
    img_id = input("\nEnter the id of the image to star: ")
    status_code = set_starred_image(3, img_id)
    _ = input("\nPress Enter to continue...\n")

    print(">>> Opening the starred image of album 3...")
    open_starred_image(3)
    _ = input("\nPress Enter to continue...\n")
