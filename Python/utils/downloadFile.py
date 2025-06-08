import os
from sys import platform
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

downloaded_files = set()


def fetch_file(url: str, local_path: str) -> None:
    """
    Fetch a file from a URL and save it locally, but only if the URL ends with a file extension.
    Does not download if the file already exists or has already been downloaded in this session.

    :param url: The URL of the file to download.
    :param local_path: The local path where the file will be saved.
    """
    if local_path in downloaded_files:
        print(f"File already downloaded in this session, skipping: {local_path}")
        return

    if os.path.exists(local_path):
        print(f"File already exists, skipping: {local_path}")
        downloaded_files.add(local_path)
        return

    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise an error for bad responses
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"File downloaded successfully: {local_path}")
        downloaded_files.add(local_path)
    except requests.RequestException as e:
        print(f"Error downloading file {url}: {e}")
    except Exception as e:
        print(f"Error saving file {url} at {local_path}: {e}")


def download_all_files(base_url: str, local_folder: str, search_schema: str) -> None:
    """
    Download all files and URLs found inside the page in the same relative directory tree using threading.

    :param base_url: The base URL of the page to parse.
    :param local_folder: The local folder where files will be saved.
    """
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    print(f"Downloading files from {base_url} to {local_folder}...")
    if len(search_schema) > 0:
        modified_files = set()
        soup = _download_files(base_url, local_folder)
        # Search for sub pages based on the schema (an element ID; find all <a> tags under all elements with that ID)
        if soup:
            # Find all elements with the given ID
            target_elems = soup.find_all(id=search_schema)
            if target_elems:
                total_links = 0
                for target_elem in target_elems:
                    links = target_elem.find_all("a", href=True)
                    total_links += len(links)
                    for link in links:
                        sub_url = urljoin(base_url, link["href"])
                        sub_local_folder = os.path.join(
                            local_folder,
                            link["href"]
                            .lstrip("/")
                            .replace("https://", "")
                            .replace("/", "_")
                            + ".html",
                        )
                        fileName = (
                            link["href"]
                            .lstrip("/")
                            .replace("https://", "")
                            .replace("/", "_")
                            + ".html"
                        )
                        print(f"Found link: {sub_url} -> Saving to {sub_local_folder}")
                        # Download the linked page and its resources
                        _download_files(sub_url, os.path.dirname(sub_local_folder))
                        modified_files.add((sub_url, fileName))
        for htmlFile in os.listdir(os.path.abspath(local_folder)):
            if htmlFile.endswith(".html"):
                with open(os.path.join(local_folder, htmlFile), "r") as f:
                    content = f.read()
                for sub_url, fileName in modified_files:
                    if sub_url in content:
                        print(f"Updating link in {htmlFile} to {fileName}")
                        content = content.replace(sub_url, fileName.split("/")[-1])
                with open(os.path.join(local_folder, htmlFile), "w") as f:
                    f.write(content)
        else:
            print(f"No elements found with ID '{search_schema}'.")
    else:
        _download_files(base_url, local_folder)

    print(f"All files downloaded to {local_folder}")


def _download_files(base_url: str, local_folder: str) -> None:

    def download_file_thread(file_url: str, local_file_path: str) -> None:
        """
        Thread function to download a single file.
        """
        try:
            fetch_file(file_url, local_file_path)
        except Exception as e:
            print(f"Error downloading file {file_url}: {e}")

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Save the main HTML file
        main_file_path = os.path.join(
            local_folder,
            base_url.replace("http://", "").replace("https://", "").replace("/", "_")
            + ".html",
        )
        fetch_file(base_url, main_file_path)

        # Find and download all linked files
        threads = []
        for tag in soup.find_all(["link", "script", "img"]):
            attr = "href" if tag.name in ["link"] else "src"
            file_url = tag.get(attr)
            if file_url:
                file_url = urljoin(base_url, file_url)
                parsed_url = urlparse(file_url)
                if parsed_url.path:  # Ensure the path is not empty
                    relative_path = os.path.relpath(parsed_url.path, "/")
                    local_file_path = os.path.join(local_folder, relative_path)
                    thread = threading.Thread(
                        target=download_file_thread, args=(file_url, local_file_path)
                    )
                    threads.append(thread)
                    thread.start()
                else:
                    print(f"Skipping invalid or empty path for URL: {file_url}")

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return soup

    except requests.RequestException as e:
        print(f"Error processing URL: {e}")


def start_http_server(local_folder: str) -> None:
    """
    Start an HTTP server to serve files from the specified folder.

    :param local_folder: The folder to serve files from.
    """
    if not os.path.exists(local_folder):
        print(f"Error: The folder {local_folder} does not exist.")
        return

    try:
        for htmlFile in os.listdir(os.path.abspath(local_folder)):
            if htmlFile.endswith(".html"):
                print(
                    f"Serving file: {htmlFile} at url http://localhost:8000/{htmlFile}"
                )
        os.chdir(os.path.abspath(local_folder))
    except FileNotFoundError:
        print(f"Error: The folder {local_folder} does not exist or cannot be accessed.")

    server = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    while True:
        try:
            url = input("Enter the URL of the page to download (or 'exit' to quit): ")
            if url.lower() == "exit":
                break
            local_folder = input("Enter the local folder to save the files: ")
            search_schema = input(
                "Enter a pattern to search for sub pages to download as well (or press Enter to skip): "
            )
            download_all_files(url, local_folder, search_schema)

            # Start the HTTP server in a separate thread
            server_thread = threading.Thread(
                target=start_http_server, args=(local_folder,), daemon=True
            )
            server_thread.start()
            print("HTTP server started. Press Ctrl+C to stop it.")
        except KeyboardInterrupt:
            print("\nStopping the HTTP server...")
            server_thread.join(timeout=1)
            if (
                input("Do you want to clear the local folder? (y/n): ").strip().lower()
                == "y"
            ):
                os.chdir("..")
                if os.path.exists(local_folder):
                    if platform == "darwin":
                        os.system(f'rm -rf "{local_folder}"')
                    elif platform == "win32":
                        os.system(f'rmdir /S /Q "{local_folder}"')
                    else:
                        os.system(f"rm -rf {local_folder}")
                    print(f"Cleared the folder: {local_folder}")
                    sys.exit(0)
                else:
                    print(f"Folder {local_folder} does not exist.")
        except Exception as e:
            print(f"Error starting HTTP server: {e}")
