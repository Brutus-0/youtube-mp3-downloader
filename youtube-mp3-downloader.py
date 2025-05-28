import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from yt_dlp import YoutubeDL

def sanitize_filename(s):
    return re.sub(r'[\\/*?:"<>|]', "", s)

def download_youtube_audio(urls, download_path, quality, progress_callback):
    quality_map = {
        "High (320 kbps)": "320",
        "Medium (192 kbps)": "192",
        "Low (128 kbps)": "128"
    }

    for url in urls:
        try:
            # Step 1: Get metadata
            with YoutubeDL({'quiet': True, 'extract_flat': 'in_playlist'}) as ydl:
                info = ydl.extract_info(url, download=False)

            is_playlist = 'entries' in info
            title = sanitize_filename(info.get('title', 'download'))
            out_dir = os.path.join(download_path, title) if is_playlist else download_path
            os.makedirs(out_dir, exist_ok=True)

            # Step 2: Configure download options
            options = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(out_dir, '%(playlist_index)02d - %(title)s.%(ext)s') if is_playlist else os.path.join(out_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality_map[quality],
                }],
                'noplaylist': False,
                'progress_hooks': [progress_callback],
                'quiet': True,
                'ffmpeg_location': 'C:/ffmpeg-7.1.1-full_build/bin'
            }

            # Step 3: Download
            with YoutubeDL(options) as ydl:
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download {url}:\n{e}")

def start_download():
    raw_urls = url_text.get("1.0", tk.END).strip()
    urls = [u.strip() for u in raw_urls.splitlines() if u.strip()]
    if not urls:
        messagebox.showwarning("Input Error", "Please enter at least one YouTube URL.")
        return
    if not download_folder.get():
        messagebox.showwarning("Folder Error", "Please choose a download location.")
        return

    selected_quality = quality_choice.get()
    if selected_quality not in ["High (320 kbps)", "Medium (192 kbps)", "Low (128 kbps)"]:
        messagebox.showwarning("Quality Error", "Please select a valid audio quality.")
        return

    progress_bar['value'] = 0
    status_label.config(text="Starting downloads...")

    def threaded_download():
        download_youtube_audio(urls, download_folder.get(), selected_quality, update_progress)
        status_label.config(text="All downloads completed.")
        progress_bar['value'] = 100

    threading.Thread(target=threaded_download, daemon=True).start()

def update_progress(d):
    if d['status'] == 'downloading':
        progress_bar['value'] = 50
        status_label.config(text=f"Downloading: {d.get('filename', '')}")
    elif d['status'] == 'finished':
        progress_bar['value'] = 90
        status_label.config(text="Converting to MP3...")

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        download_folder.set(folder)

# GUI Setup
root = tk.Tk()
root.title("YouTube to MP3 Downloader")
root.geometry("600x450")

tk.Label(root, text="Enter YouTube video or playlist URLs (one per line):").pack(pady=5)
url_text = tk.Text(root, height=8, width=70)
url_text.pack()

tk.Button(root, text="Select Download Folder", command=browse_folder).pack(pady=5)
download_folder = tk.StringVar()
tk.Entry(root, textvariable=download_folder, width=60).pack()

tk.Label(root, text="Select Audio Quality:").pack(pady=5)
quality_choice = ttk.Combobox(root, values=["High (320 kbps)", "Medium (192 kbps)", "Low (128 kbps)"])
quality_choice.current(1)  # Default to Medium
quality_choice.pack()

tk.Button(root, text="Download MP3s", command=start_download, bg="green", fg="white").pack(pady=10)

progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.pack(pady=5)
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()