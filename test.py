import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import re
import urllib.parse
from difflib import get_close_matches
import pandas as pd
from collections import Counter
import pandas as pd
from urllib.parse import urlparse, unquote
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from fuzzywuzzy import process
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import chromedriver_autoinstaller
import re
import requests
from selenium.webdriver.common.by import By
import urllib
from urllib.parse import quote_plus

def get_google_maps_url(google_maps_search_url):
    # Create options for the Chrome webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # you can uncomment this headless to apply headless scraping
    #options.add_argument('--headless')
    
    # Set window size and position
    options.add_argument("--window-position=0,0")  # Set window position (top-left corner)
    options.add_argument("--force-device-scale-factor=0.10")  # Set the device scale factor to 0.25 (25%)

    # Create a new instance of the Chrome webdriver with the specified options
    driver = webdriver.Chrome(options=options)  # 'chromedriver' is in the PATH in Colab

    try:
        # Open Google Maps search URL
        driver.get(google_maps_search_url)

        # Wait for the page to load (you might need to adjust the sleep duration)
        time.sleep(20)

        # Find all the anchor elements (links) containing search results
        search_results = driver.find_elements(By.CSS_SELECTOR, "a")

        # Extract the href attribute from each anchor element
        hrefs = [link.get_attribute('href') for link in search_results]

        # Filter out None values and invalid URLs
        valid_hrefs = [href for href in hrefs if href is not None and 'https://www.google.com/maps/place/' in href]

        return valid_hrefs

    finally:
        # Close the browser window
        driver.quit()

def load_data(adm1_filter=None, adm2_filter=None, adm3_filter=None, adm4_filter=None):
    path = "ph_areas_keys.csv"
    df = pd.read_csv(path)

    unique_adm1_en = df.groupby('ADM1_EN_KEY')['ADM1_EN'].first().tolist()
    unique_adm2_en = df.loc[df['ADM1_EN'] == adm1_filter, 'ADM2_EN'].unique().tolist()
    unique_adm3_en = df.loc[(df['ADM1_EN'] == adm1_filter) & (df['ADM2_EN'] == adm2_filter), 'ADM3_EN'].unique().tolist()
    unique_adm4_en = df.loc[(df['ADM1_EN'] == adm1_filter) & (df['ADM2_EN'] == adm2_filter) & (df['ADM3_EN'] == adm3_filter), 'ADM4_EN'].unique().tolist()

    adm1_list = [""] + unique_adm1_en
    adm2_list = [""] + unique_adm2_en
    adm3_list = [""] + unique_adm3_en
    adm4_list = [""] + unique_adm4_en

    adm1_combobox['values'] = adm1_list
    adm2_combobox['values'] = adm2_list
    adm3_combobox['values'] = adm3_list
    adm4_combobox['values'] = adm4_list

    treeview.delete(*treeview.get_children())  # Clear existing data
    for _, row in df.iterrows():
        if (not adm1_filter or row['ADM1_EN'] == adm1_filter) and \
           (not adm2_filter or row['ADM2_EN'] == adm2_filter) and \
           (not adm3_filter or row['ADM3_EN'] == adm3_filter) and \
           (not adm4_filter or row['ADM4_EN'] == adm4_filter):
            treeview.insert('', tk.END, values=(row["ADM4_EN"], row["ADM3_EN"], row["ADM2_EN"], row["ADM1_EN"]))
    
    filtered_df = df.loc[(df['ADM1_EN'] == adm1_filter) & 
                         (df['ADM2_EN'] == adm2_filter) & 
                         (df['ADM3_EN'] == adm3_filter) & 
                         (df['ADM4_EN'] == adm4_filter)]
    if filtered_df.empty:
        filtered_df = df[(df['ADM1_EN'] == adm1_filter) & 
                            (df['ADM2_EN'] == adm2_filter) & 
                            (df['ADM3_EN'] == adm3_filter)]
    elif filtered_df.empty:
        filtered_df = df[(df['ADM1_EN'] == adm1_filter) & 
                            (df['ADM2_EN'] == adm2_filter)]
    elif filtered_df.empty:
        filtered_df = df[(df['ADM1_EN'] == adm1_filter)]
    
    return filtered_df

def region_selected(event):
    adm1 = adm1_combobox.get()
    adm2_combobox['state'] = 'enable'  # Disable province combobox
    adm2_combobox.set("")  # Reset province selection
    adm3_combobox['state'] = 'disable'  # Disable city combobox
    adm3_combobox.set("")  # Reset city selection
    adm4_combobox['state'] = 'disabled'  # Disable barangay combobox
    adm4_combobox.set("")  # Reset barangay selection
    load_data(adm1_filter=adm1)

def province_selected(event):
    adm1 = adm1_combobox.get()
    adm2 = adm2_combobox.get()
    adm3_combobox['state'] = 'enable'  # Disable city combobox
    adm3_combobox.set("")  # Reset city selection
    adm4_combobox['state'] = 'disabled'  # Disable barangay combobox
    adm4_combobox.set("")  # Reset barangay selection
    load_data(adm1_filter=adm1, adm2_filter=adm2)

def municipality_selected(event):
    adm1 = adm1_combobox.get()
    adm2 = adm2_combobox.get()
    adm3 = adm3_combobox.get()
    adm4_combobox['state'] = 'enable'  # Disable barangay combobox
    adm4_combobox.set("")  # Reset barangay selection
    load_data(adm1_filter=adm1, adm2_filter=adm2, adm3_filter=adm3)
def barangay_selected(event):
    adm1 = adm1_combobox.get()
    adm2 = adm2_combobox.get()
    adm3 = adm3_combobox.get()
    adm4 = adm4_combobox.get()
    adm4_combobox['state'] = 'enable'  # Disable barangay combobox
    load_data(adm1_filter=adm1, adm2_filter=adm2, adm3_filter=adm3,adm4_filter=adm4)

def export_data(event=None):
    adm1 = adm1_combobox.get()
    adm2 = adm2_combobox.get()
    adm3 = adm3_combobox.get()
    adm4 = adm4_combobox.get()

    filtered_df = load_data(adm1_filter=adm1, adm2_filter=adm2, adm3_filter=adm3, adm4_filter=adm4)
    
    # Export the filtered DataFrame to a CSV file
    filtered_df.to_csv("output/filtered_data.csv", index=False, encoding = 'utf-8')
    generate_button['state'] = 'enable'  # Initially disabled

root = tk.Tk()
root.title("ojt_neu_scrapper")
root.geometry("1167x600")

style = ttk.Style(root)
root.tk.call("source", "forest-light.tcl")
root.tk.call("source", "forest-dark.tcl")
style.theme_use("forest-dark")

frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

widgets_frame = ttk.LabelFrame(frame, text="Filter Table")
widgets_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

df = pd.read_csv('ph_areas_keys.csv', encoding='utf-8')
unique_adm1_en = df.groupby('ADM1_EN_KEY')['ADM1_EN'].first().tolist()
unique_adm2_en = df.groupby('ADM2_EN_KEY')['ADM2_EN'].first().tolist()
unique_adm3_en = df.groupby('ADM3_EN_KEY')['ADM3_EN'].first().tolist()
unique_adm4_en = df.groupby('ADM4_EN_KEY')['ADM4_EN'].first().tolist()

# Label and combobox for Region
region_label = ttk.Label(widgets_frame, text="Region:")
region_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
adm1_combobox = ttk.Combobox(widgets_frame, values=[""] + unique_adm1_en)
adm1_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
adm1_combobox.bind("<<ComboboxSelected>>", region_selected)

# Label and combobox for Province
province_label = ttk.Label(widgets_frame, text="Province:")
province_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
adm2_combobox = ttk.Combobox(widgets_frame, values=[""])
adm2_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
adm2_combobox.bind("<<ComboboxSelected>>", province_selected)
adm2_combobox['state'] = 'disabled'  # Initially disabled

# Label and combobox for Municipality
municipality_label = ttk.Label(widgets_frame, text="Municipality:")
municipality_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
adm3_combobox = ttk.Combobox(widgets_frame, values=[""])
adm3_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
adm3_combobox.bind("<<ComboboxSelected>>", municipality_selected)
adm3_combobox['state'] = 'disabled'  # Initially disabled

# Label and combobox for Barangay
barangay_label = ttk.Label(widgets_frame, text="Barangay:")
barangay_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
adm4_combobox = ttk.Combobox(widgets_frame, values=[""])
adm4_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
adm4_combobox.bind("<<ComboboxSelected>>", barangay_selected)
adm4_combobox['state'] = 'disabled'  # Initially disabled

button = ttk.Button(widgets_frame, text="export csv", command=export_data)
button.grid(row=4, column=0, padx=5, pady=5, columnspan=2, sticky="nsew")

# Bind the Return key to trigger the filter_data function
root.bind('<Return>', export_data)

separator = ttk.Separator(widgets_frame)
separator.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

treeFrame = ttk.Frame(frame)
treeFrame.grid(row=0, column=1, pady=10, sticky="nsew")
treeScroll = ttk.Scrollbar(treeFrame)
treeScroll.pack(side="right", fill="y")

cols = ("ADM4_EN", "ADM3_EN", "ADM2_EN", "ADM1_EN")
treeview = ttk.Treeview(treeFrame, show="headings",
                        yscrollcommand=treeScroll.set, columns=cols, height=13)
treeview.column("ADM4_EN", width=200, anchor="center")
treeview.column("ADM3_EN", width=200, anchor="center")
treeview.column("ADM2_EN", width=200, anchor="center")
treeview.column("ADM1_EN", width=200, anchor="center")
treeview.heading("ADM4_EN", text="Barangay")
treeview.heading("ADM3_EN", text="Municipality")
treeview.heading("ADM2_EN", text="Province")
treeview.heading("ADM1_EN", text="Region")
treeview.pack(expand=True, fill="both")
treeScroll.config(command=treeview.yview)
load_data()  # Load all data initially

filtered_df = load_data()
separator = ttk.Separator(widgets_frame)
separator.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

# New Frame for Large Text
large_text_frame = ttk.LabelFrame(frame, text="Google Scrape")
large_text_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

large_text = tk.Text(large_text_frame, height=10, wrap="word")
large_text.pack(fill="both", expand=True)

def generate_google_maps_urls():
    filtered_df = pd.read_csv("output/filtered_data.csv", encoding='utf-8')
    # Get user input for the establishment
    establishment = establishment_entry.get()

    # Base URL for Google Maps search
    base_url = "https://www.google.com/maps/search/"

    # Combine the base URL, location data, and establishment query for each location
    location_data = filtered_df.apply(lambda row: f"{row['ADM4_EN']}, {row['ADM3_EN']}, {row['ADM2_EN']}, {row['ADM1_EN']}", axis=1)
    queries = base_url + establishment + " in " + location_data

    # Clear existing content in the large_text widget
    large_text.delete(1.0, "end")
    # Scraping Google Maps URLs for each query
        
    list_establishment_links = []
    for query in queries:
        list_links = get_google_maps_url(query)
        for link in list_links:
            list_establishment_links.append(link)

    # Display the generated URLs in the large_text widget
    for link in list_establishment_links:
        large_text.insert("end", link + "\n")
    df_links = pd.DataFrame()
    df_links['links'] = list_establishment_links
    df_links.to_csv('output/gmaps_links.csv',index = False, encoding = 'utf-8')

# Create an entry for user input
establishment_label = ttk.Label(widgets_frame, text="Establishment:")
establishment_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")
establishment_entry = ttk.Entry(widgets_frame)
establishment_entry.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

# Button to generate Google Maps URLs
generate_button = ttk.Button(widgets_frame, text="Generate URLs", command=generate_google_maps_urls)
generate_button.grid(row=8, column=0, padx=5, pady=5, columnspan=2, sticky="nsew")
generate_button['state'] = 'disabled'  # Initially disabled

root.mainloop()
