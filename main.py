import os
import colorama
import dropbox
import dropbox.files
import time
import hashlib
from colorama import Fore, Style

APP_KEY = ''
APP_SECRET = ''
REFRESH_TOKEN = ''

count = 0

colorama.init()
dbx = dropbox.Dropbox(
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    oauth2_refresh_token=REFRESH_TOKEN
)

start_download_time = time.time()

def dropbox_content_hash(file):
    hash_chunk_size = 4 * 1024 * 1024;
    with open(file, "rb") as f:
        block_hashes = bytes()
        while True:
            chunk = f.read(hash_chunk_size)
            if not chunk:
                break
            block_hashes += hashlib.sha256(chunk).digest()
        return hashlib.sha256(block_hashes).hexdigest()

def download_changed():
    dropbox_entries = dbx.files_list_folder("").entries
    dropbox_file_names = [entry.name for entry in dropbox_entries]
    global count

    for entry in dropbox_entries:
        #file_metadata = dbx.files_get_metadata(f"/{entry.name}")
        file_size = entry.size / (1024 * 1024)
        local_file_path = os.path.join("mods", entry.name)
        count += 1

        if os.path.exists(local_file_path):
            local_hash = dropbox_content_hash(local_file_path)
            if local_hash != entry.content_hash:
                # CHANGES
                print(f"{Style.BRIGHT}{Fore.YELLOW}MOD FOI ATUALIZADO: {entry.name} {Fore.WHITE}[{file_size:0.2f} MB]")
                dbx.files_download_to_file(local_file_path, f"/{entry.name}")
            else:
                # NO CHANGES
                print(f"{Style.BRIGHT}{Fore.CYAN}SEM MUDANÇAS: {entry.name} {Fore.WHITE}[{file_size:0.2f} MB]")
        else:
            # NEW FILES
            print(f"{Style.BRIGHT}{Fore.GREEN}NOVO MOD: {entry.name} {Fore.WHITE}[{file_size:0.2f} MB]")
            dbx.files_download_to_file(local_file_path, f"/{entry.name}")

    local_files = os.listdir("mods")
    for local_file in local_files:
        if local_file not in dropbox_file_names:
            # DELETE FILE
            print(f"{Style.BRIGHT}{Fore.RED}MOD REMOVIDO: {local_file} {Fore.WHITE}[{file_size:0.2f} MB]")
            os.remove(os.path.join("mods", local_file))

download_changed()
end_download_time = time.time()
print(f"\n{Style.BRIGHT}Tempo: {end_download_time - start_download_time:.2f} Segundos.\n{count} Mods instanciados e verificados")
os.system("pause")