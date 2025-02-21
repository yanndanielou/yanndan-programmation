import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import threading
import os


class DownloadPopup:
    def __init__(self, master, url, save_path):
        self.master = master
        self.url = url
        self.save_path = save_path
        self.cancel_download = False

        self.master.title("Downloading...")
        self.master.geometry("300x150")

        self.label = tk.Label(master, text="Downloading file...")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(master, length=250, mode="determinate")
        self.progress.pack(pady=10)

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
                    self.progress["value"] = (downloaded / file_size) * 100
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
    DownloadPopup(popup, url, save_path)


def _example_main():
    root = tk.Tk()
    root.withdraw(root)  # Hide the main window
    _example_usage()
    root.mainloop()
