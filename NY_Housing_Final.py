"""
Name:       Your Name
CS230:      Section XXX
Data:       NY-House-Dataset.csv
URL:        (add your Streamlit Cloud URL here)

Description:
Simple Streamlit app to explore New York housing data.
You can choose a price range, a specific number of bedrooms and bathrooms,
a locality, a listing status (For sale, For rent, Sold, etc.), and a property type
(Condo, Apartment, House, etc.). The app shows the filtered rows, summary
statistics, two charts, and a map.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


def load_data():
    """Read the CSV file and do small cleaning."""
    df = pd.read_csv("NY-House-Dataset.csv")

    # keep only rows with price and coordinates
    df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])
    df = df[df["PRICE"] > 0]

    return df


def get_min_max_price(df):
    """Return minimum and maximum price in the dataset."""
    min_price = int(df["PRICE"].min())
    max_price = int(df["PRICE"].max())
    return min_price, max_price


def filter_data(
    df,
    min_price,
    max_price,
    bed_choice="Any",
    bath_choice="Any",
    locality_choice="All",
    status_choice="Any",
    ptype_choice="Any",
):
    """Filter the DataFrame based on user choices."""
    # filter by price range
    filtered = df[(df["PRICE"] >= min_price) & (df["PRICE"] <= max_price)]

    # filter by exact number of bedrooms
    if bed_choice != "Any":
        filtered = filtered[filtered["BEDS"] == bed_choice]

    # filter by exact number of bathrooms
    if bath_choice != "Any":
        filtered = filtered[filtered["BATH"] == bath_choice]

    # filter by locality
    if locality_choice != "All":
        filtered = filtered[filtered["LOCALITY"] == locality_choice]

    # filter by listing status (For sale, For rent, Sold, etc.)
    if status_choice != "Any":
        filtered = filtered[filtered["STATUS"] == status_choice]

    # filter by property type (Condo, Apartment, House, etc.)
    if ptype_choice != "Any":
        filtered = filtered[filtered["PROPERTY_TYPE"] == ptype_choice]

    return filtered


def get_summary_stats(filtered_df):
    """Return count, average price, average beds for the filtered data."""
    if len(filtered_df) == 0:
        return 0, 0.0, 0.0

    count = len(filtered_df)
    avg_price = float(filtered_df["PRICE"].mean())
    avg_beds = float(filtered_df["BEDS"].mean())
    return count, avg_price, avg_beds


def main():
    st.title("New York Housing Explorer")

    st.sidebar.header("Filters")

    # ------------ LOAD DATA ------------
    df = load_data()

    # simple derived column (if square footage exists)
    if "PROPERTYSQFT" in df.columns:
        df["PRICE_PER_SQFT"] = df["PR]()
