import requests


def fetch_file(url: str, local_filename: str) -> None:
    """
    Fetch a file from a URL and save it locally.

    :param url: The URL of the file to download.
    :param local_filename: The local path where the file will be saved.
    """
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise an error for bad responses
            with open(local_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"File downloaded successfully: {local_filename}")
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
