import os
import dropbox
import dropbox.files
import time
import hashlib
import customtkinter as ctk
from customtkinter import filedialog

APP_KEY = ''
APP_SECRET = ''
REFRESH_TOKEN = ''

count = 0

dbx = dropbox.Dropbox(
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    oauth2_refresh_token=REFRESH_TOKEN
)

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

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x650")
        self.resizable(width=False, height=False)
        self.title("ModsLoader App")
        self._set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)

        self.selected_directory = None

        self.log_frame = ctk.CTkScrollableFrame(self, width=550, height=400)
        self.log_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        self.log_row_count = 0
        self.max_logs = 100  # Limite de logs visíveis

        self.progress_label = ctk.CTkLabel(self, text="0%", anchor="center", text_color="white", font=("Helvetica", 25))
        self.progress_label.grid(row=1, column=0, columnspan=2)

        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal", height=20)
        self.progressbar.grid(row=2, column=0, columnspan=2, padx=20, sticky="ew")
        self.progressbar.set(0)

        self.button = ctk.CTkButton(self, text="Sincronizar pasta", command=lambda:[self.button.configure(state="disabled"), self.button_click(), self.button.configure(state="normal")], corner_radius=20, height=40, font=("Arial bold", 16))
        self.button.grid(row=3, column=0, columnspan=2, padx=20, pady=15, sticky="ew")

        self.folder_warning = ctk.CTkLabel(self, text="Pasta do jogo não selecionada. Selecione a pasta onde está localizada o diretório mods.",
                                           text_color="#a4a4a4", wraplength=300, font=("Arial bold", 14))
        self.folder_warning.grid(row=4, column=0, padx=20, sticky="ew")
        self.button.configure(state="disabled")

        self.folder_button = ctk.CTkButton(self, text="Selecione a pasta do jogo", command=self.folder_button_action, font=("Arial bold", 12))
        self.folder_button.grid(row=4, column=1, padx=20)

    def log_to_history(self, message, color):
        if self.log_row_count >= self.max_logs:
            # Remove o primeiro log (mais antigo)
            children = self.log_frame.winfo_children()
            if children:
                children[0].destroy()

        log_label = ctk.CTkLabel(self.log_frame, text=message, text_color=color, font=("Helvetica", 18), anchor="w")
        log_label.grid(row=self.log_row_count, column=0, sticky="ew", pady=0, padx=10)

        # Move a visualização para o fim da lista
        self.log_frame.update_idletasks()
        self.log_frame._parent_canvas.yview_moveto(1)  # Isso faz o scroll ir para o fim

        self.log_row_count += 1
        self.update()

    def folder_button_action(self):
        self.selected_directory = filedialog.askdirectory()

        if self.selected_directory:
            mods_path = os.path.join(self.selected_directory, "mods")

            if os.path.exists(mods_path):
                # self.folder_warning.grid_forget()
                self.folder_warning.configure(text=f"{mods_path}", text_color="green",font=("Arial bold", 14), wraplength=350)
                self.button.configure(state="normal")
            else:
                self.folder_warning.configure(text="Pasta 'mods' não encontrada nesse diretório", text_color="#ed4e4e", font=("Arial bold", 14))
                self.button.configure(state="disabled")
        else:
            self.folder_warning.configure(text="Nenhum diretório foi selecionado.", text_color="#ed4e4e", font=("Arial bold", 14))
            self.button.configure(state="disabled")

    def download_changed(self):
        dropbox_entries = dbx.files_list_folder("").entries
        dropbox_file_names = [entry.name for entry in dropbox_entries]
        dropbox_entries_length = len(dropbox_entries)
        self.max_logs = len(dropbox_entries)
        global count
        count = 0

        for entry in dropbox_entries:
            file_size = entry.size / (1024 * 1024)
            local_file_path = os.path.join(self.selected_directory, "mods", entry.name)
            count += 1

            if os.path.exists(local_file_path):
                local_hash = dropbox_content_hash(local_file_path)
                if local_hash != entry.content_hash:
                    dbx.files_download_to_file(local_file_path, f"/{entry.name}")
                    self.log_to_history(f"Atualizado: {entry.name} [{file_size:0.2f} MB]", "yellow")
                else:
                    self.log_to_history(f"Sem mudanças: {entry.name}", "cyan")
            else:
                dbx.files_download_to_file(local_file_path, f"/{entry.name}")
                self.log_to_history(f"Novo Mod: {entry.name} [{file_size:0.2f} MB]", "green")

            percentage = count / dropbox_entries_length
            self.progressbar.set(percentage)
            self.progress_label.configure(text=f"{int(percentage * 100)}%")
            self.update()

        local_files = os.listdir(self.selected_directory + "/mods")
        for local_file in local_files:
            if local_file not in dropbox_file_names:
                os.remove(os.path.join(self.selected_directory, "mods", local_file))
                self.log_to_history(f"Removido: {local_file} [{file_size:0.2f} MB]", "red")

        self.log_to_history(f"{count} Mods verificados e instanciados", "white")
        self.folder_button.configure(state="normal")
        count = 0

    def button_click(self):
        start_download_time = time.time()
        self.folder_button.configure(state="disabled")
        self.download_changed()

app = App()
app.mainloop()