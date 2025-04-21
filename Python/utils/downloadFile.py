import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


def fetch_file(url: str, local_path: str) -> None:
    """
    Fetch a file from a URL and save it locally.

    :param url: The URL of the file to download.
    :param local_path: The local path where the file will be saved.
    """
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise an error for bad responses
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"File downloaded successfully: {local_path}")
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
    except Exception as e:
        print(f"Error saving file {local_path}: {e}")


def download_all_files(base_url: str, local_folder: str) -> None:
    """
    Download all files and URLs found inside the page in the same relative directory tree using threading.

    :param base_url: The base URL of the page to parse.
    :param local_folder: The local folder where files will be saved.
    """

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
        main_file_path = os.path.join(local_folder, "index.html")
        fetch_file(base_url, main_file_path)

        # Find and download all linked files
        threads = []
        for tag in soup.find_all(["a", "link", "script", "img"]):
            attr = "href" if tag.name in ["a", "link"] else "src"
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
        os.chdir(os.path.abspath(local_folder))
    except FileNotFoundError:
        print(f"Error: The folder {local_folder} does not exist or cannot be accessed.")
        return

    server = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
    print(f"Serving files from {os.getcwd()} on http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    while True:
        url = input("Enter the URL of the page to download (or 'exit' to quit): ")
        if url.lower() == "exit":
            break
        local_folder = input("Enter the local folder to save the files: ")
        download_all_files(url, local_folder)

        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(
            target=start_http_server, args=(local_folder,), daemon=True
        )
        server_thread.start()

        input("Press Enter to stop the server and exit...")
        break
