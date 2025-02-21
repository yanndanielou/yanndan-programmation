import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import urllib.request
import threading
import os
import time


class MultipleFilesDownloadPopup:
    def __init__(self, master, downloads, parallel=True):
        self.master = master
        self.downloads = downloads
        self.parallel = parallel
        self.cancel_downloads = {}

        self.master.title("Downloading...")
        self.master.geometry("550x400")

        self.frame_container = ttk.Frame(master)
        self.frame_container.pack(fill="both", expand=True)

        self.add_button = tk.Button(
            master, text="Add Download", command=self.add_download_asking_details
        )
        self.add_button.pack(pady=5)

        self.frames = []
        for url, save_path in downloads:
            self._create_download_row(url, save_path)

        if self.parallel:
            for url, save_path, progress, progress_label, _, _, _ in self.frames:
                threading.Thread(
                    target=self.download_file,
                    args=(url, save_path, progress, progress_label),
                    daemon=True,
                ).start()
        else:
            threading.Thread(target=self.download_sequentially, daemon=True).start()

    def _create_download_row(self, url, save_path):
        frame = ttk.Frame(self.frame_container)
        frame.pack(fill="x", padx=10, pady=5)

        label = tk.Label(frame, text=os.path.basename(save_path))
        label.pack(side="left")

        progress = ttk.Progressbar(frame, length=150, mode="determinate")
        progress.pack(side="left", padx=10)

        progress_label = tk.Label(frame, text="0% (0 KB / 0 KB, ETA: --s)")
        progress_label.pack(side="left", padx=5)

        cancel_button = tk.Button(
            frame, text="Cancel", command=lambda sp=save_path: self.cancel(sp)
        )
        cancel_button.pack(side="left", padx=5)

        self.frames.append(
            (
                url,
                save_path,
                progress,
                progress_label,
                cancel_button,
                frame,
                time.time(),
            )
        )
        self.cancel_downloads[save_path] = False

        if self.parallel:
            threading.Thread(
                target=self.download_file,
                args=(url, save_path, progress, progress_label),
                daemon=True,
            ).start()

    def download_sequentially(self):
        for url, save_path, progress, progress_label, _, _, _ in self.frames:
            self.download_file(url, save_path, progress, progress_label)

    def download_file(self, url, save_path, progress, progress_label):
        try:
            response = urllib.request.urlopen(url)
            file_size = int(response.getheader("Content-Length", 0))
            chunk_size = 8192
            downloaded = 0
            start_time = time.time()

            with open(save_path, "wb") as file:
                while not self.cancel_downloads[save_path]:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded += len(chunk)
                    elapsed_time = time.time() - start_time
                    speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                    remaining_time = (
                        (file_size - downloaded) / speed if speed > 0 else 0
                    )
                    percent = (downloaded / file_size) * 100
                    progress["value"] = percent
                    readable_size = lambda size: (
                        f"{size / (1024 * 1024):.2f} MB"
                        if size > 1024 * 1024
                        else f"{size / 1024:.2f} KB"
                    )
                    eta_formatted = (
                        time.strftime("%M:%S", time.gmtime(remaining_time))
                        if remaining_time > 0
                        else "--"
                    )
                    progress_label.config(
                        text=f"{percent:.2f}% ({readable_size(downloaded)} / {readable_size(file_size)}, ETA: {eta_formatted})"
                    )
                    self.master.update_idletasks()

            if self.cancel_downloads[save_path]:
                os.remove(save_path)
                self.show_message(
                    "Download", f"Download {os.path.basename(save_path)} canceled."
                )
            else:
                self.show_message(
                    "Download",
                    f"Download {os.path.basename(save_path)} completed successfully.",
                )
        except Exception as e:
            self.show_message("Error", f"Download failed: {e}")

    def cancel(self, save_path):
        self.cancel_downloads[save_path] = True

    def show_message(self, title, message):
        threading.Thread(
            target=lambda: messagebox.showinfo(title, message), daemon=True
        ).start()

    def add_download_asking_details(self):
        url = tk.simpledialog.askstring("Add Download", "Enter file URL:")
        save_path = tk.simpledialog.askstring("Add Download", "Enter save path:")
        if url and save_path:
            self._create_download_row(url, save_path)

    def add_download(self, url, save_path):
        self._create_download_row(url, save_path)


class SingleFileDownloadPopupWithProgressBar:
    def __init__(self, master, url, save_path):
        self.master = master
        self.url = url
        self.save_path = save_path
        self.cancel_download = False

        self.master.title("Downloading...")
        self.master.geometry("300x180")

        self.label = tk.Label(master, text="Downloading file...")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(master, length=250, mode="determinate")
        self.progress.pack(pady=10)

        self.progress_label = tk.Label(master, text="0% (0 KB / 0 KB)")
        self.progress_label.pack(pady=5)

        self.cancel_button = tk.Button(master, text="Cancel", command=self.cancel)
        self.cancel_button.pack(pady=10)

        threading.Thread(target=self.download_file, daemon=True).start()

    def download_file(self):
        try:
            response = urllib.request.urlopen(self.url)
            file_size = int(response.getheader("Content-Length", 0))
            chunk_size = 8192
            downloaded = 0

            with open(self.save_path, "wb") as file:
                while not self.cancel_download:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / file_size) * 100
                    self.progress["value"] = percent
                    self.progress_label.config(
                        text=f"{percent:.2f}% ({downloaded / 1024:.2f} KB / {file_size / 1024:.2f} KB)"
                    )
                    self.master.update_idletasks()

            if self.cancel_download:
                os.remove(self.save_path)
                messagebox.showinfo("Download", "Download canceled.")
            else:
                messagebox.showinfo("Download", "Download completed successfully.")
            self.master.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {e}")
            self.master.destroy()

    def cancel(self):
        self.cancel_download = True


# Example usage
def _example_usage(root):
    url = "https://example.com/largefile.zip"  # Replace with an actual file URL
    save_path = "largefile.zip"

    popup = tk.Toplevel(root)
    SingleFileDownloadPopupWithProgressBar(popup, url, save_path)


def _example_main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    _example_usage(root)
    root.mainloop()
