import os
import dropbox
import dropbox.files
import time

APP_KEY = ''
APP_SECRET = ''
REFRESH_TOKEN = ''

dbx = dropbox.Dropbox(
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    oauth2_refresh_token=REFRESH_TOKEN
)

start_download_time = time.time()
def download_all_cloud_files():
    for entry in dbx.files_list_folder("").entries:
        file_metadata = dbx.files_get_metadata(f"/{entry.name}")
        file_size = file_metadata.size / (1024 * 1024)
        start_time = time.time()
        print(f"Downloading {entry.name} (Size: {file_size:.2f} MB)...", end=' ')

        dbx.files_download_to_file(os.path.join("mods", entry.name), f"/{entry.name}")

        end_time = time.time()
        download_time = end_time - start_time
        download_speed = file_size / download_time
        print(f"done. Download time: {download_time:.2f} seconds. Speed: {download_speed:.2f} MB/second.")

download_all_cloud_files()

end_download_time = time.time()
print(f"Time: {end_download_time - start_download_time:.2f} seconds.")