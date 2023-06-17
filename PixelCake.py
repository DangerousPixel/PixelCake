import tkinter as tk
from tkinter import ttk
import requests
from tkinter import messagebox
import os
from urllib.request import urlretrieve
from tqdm import tqdm
import math
from time import time
import webbrowser

def download_speed_time(start_time, downloaded_size):
    elapsed_time = time() - start_time
    return downloaded_size / elapsed_time


def estimated_time_left(total_size, downloaded_size, start_time):
    remaining_size = total_size - downloaded_size
    speed = download_speed_time(start_time, downloaded_size)
    return remaining_size / speed


def search_apps(app_name):
    url = f"https://apiv2.iphonecake.com/appcake/appcake_api/spv6/appsearch_r.php?device=1&q={app_name}&p=0"
    payload = ""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "appcakej/7.0.4 (iPhone; iOS 13.6.1; Scale/3.00)",
        "Connection": "close",
        "Host": "apiv2.iphonecake.com",
        "Accept-Encoding": "gzip, deflate",
        "Cache-Control": "max-age=0"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return response.json().get("list", [])

def get_ipa_link(app_id):
    url = f"https://apiv2.iphonecake.com/appcake/appcake_api/ipastore_ios_link.php?type=1&id={app_id}"
    payload = ""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "appcakej/7.0.4 (iPhone; iOS 13.6.1; Scale/3.00)",
        "Connection": "close",
        "Host": "apiv2.iphonecake.com",
        "Accept-Encoding": "gzip, deflate",
        "Cache-Control": "max-age=0"
    }
    response = requests.request("GET", url, data=payload, headers=headers)
    return response.json()["link"]

def on_search_click():
    app_name = app_name_entry.get()
    app_list = search_apps(app_name)
    app_listbox.delete(0, tk.END)

    bg_color = "#1D0748"
    fg_color = "yellow"
    noR_bg_color = "red"
    noR_fg_color = "white"
    r_bg_color = "1D0748"
    r_fg_color = "white"

    if not app_list:
        app_listbox.insert(tk.END, "No results")
        app_listbox.itemconfig(tk.END, bg=noR_bg_color, fg=noR_fg_color)
    else:
        for app in app_list:
            app_listbox.insert(tk.END, f"{app['name']} ({app['ver']}) - ID: {app['id']}")
            app_listbox.itemconfig(tk.END, bg=bg_color, fg=fg_color)
            
def on_download_click():
    selected_app = app_listbox.get(app_listbox.curselection())
    if selected_app:
        app_id = selected_app.split("ID: ")[1]
        ipa_link = get_ipa_link(app_id)
        ipa_name = selected_app.split(" (")[0] + ".ipa"
        
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        download_ipa(ipa_link, download_path, ipa_name)
        messagebox.showinfo("Download Complete", f"{ipa_name} downloaded successfully in {download_path}.")
    else:
        messagebox.showwarning("No App Selected", "Please select an app to download.")

def download_ipa(url, save_path, file_name):
    destination = os.path.join(save_path, file_name)
    response = requests.get(url, stream=True)

    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        desc="\033[32mDownloading IPA\033[0m",
        bar_format="{l_bar}\033[32m{bar}\033[0m| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    )

    start_time = time()
    downloaded_size = 0

    with open(destination, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

            downloaded_size += len(data)
            connection_speed = download_speed_time(start_time, downloaded_size)
            time_left = estimated_time_left(total_size, downloaded_size, start_time)

            progress_bar.set_postfix(
                _extra=[
                    ('Speed', f"\033[38;5;197m{connection_speed / (1024 * 1024):.1f} MB/s\033[0m"),
                    ('Time_left', f"\033[38;5;197m{time_left:.2f} s\033[0m")
                ]
            )

    progress_bar.close()
    if total_size != 0 and progress_bar.n != total_size:
        print("Error while downloading the IPA file.")
    else:
        print("Download complete.")
        
def open_dpixel_store():
    webbrowser.open("https://dpixel.co", new=1)

def open_telegram_channel():
    webbrowser.open("https://t.me/dpixel", new=1)

root = tk.Tk()
root.title("PixelCake - By : DPixelStore")

frame = ttk.Frame(root, padding="10")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

app_name_label = ttk.Label(frame, text="App Name:")
app_name_label.grid(column=0, row=0, sticky=tk.W)

app_name_entry = ttk.Entry(frame, width=35)
app_name_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))

search_button = ttk.Button(frame, text="Search", command=on_search_click)
search_button.grid(column=2, row=0, padx=(10, 0), sticky=tk.W)

app_listbox = tk.Listbox(frame, height=15, width=75)
app_listbox.grid(column=0, row=1, columnspan=3, pady=(10, 0))

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=app_listbox.yview)
scrollbar.grid(column=3, row=1, sticky=(tk.N, tk.S))
app_listbox.configure(yscrollcommand=scrollbar.set)

download_button = ttk.Button(frame, text="Direct Download", command=on_download_click)
download_button.grid(column=2, row=2, pady=(10, 0))

dpixel_store_button = tk.Button(frame, text="DPixelStore", foreground="#ff009b", command=open_dpixel_store)
dpixel_store_button.grid(column=0, row=2, pady=(0, 0), sticky=tk.W)

telegram_channel_button = tk.Button(frame, text="Telegram Channel", foreground="#ff009b", command=open_telegram_channel)
telegram_channel_button.grid(column=1, row=2, pady=(0, 0), sticky=tk.W)

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.resizable(False,False)
frame.rowconfigure(1, weight=1)
frame.columnconfigure(1, weight=1)

root.mainloop()
