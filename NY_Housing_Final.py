"""
Name:       Your Name
CS230:      Section XXX
Data:       NY-House-Dataset.csv
URL:        (add your Streamlit Cloud URL here)

Description:
Simple Streamlit app to explore New York housing data.
You can choose a price range, a specific number of bedrooms and bathrooms,
a locality, a listing status (For Sale, For Rent, etc.), and a property type
(Condo, Apartment, House, etc.). The app shows the filtered rows, summary
statistics, two charts, and a map.

References:
- Streamlit docs: https://docs.streamlit.io/
- Matplotlib docs: https://matplotlib.org/
- PyDeck docs: https://deckgl.readthedocs.io/
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


# Python Feature 1: function with a parameter and a return value
def load_data():
    """Read the CSV file and do very small cleaning."""
    df = pd.read_csv("NY-House-Dataset.csv")

    # Data Analytics Feature 1: basic cleaning with dropna and filter
    df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])
    df = df[df["PRICE"] > 0]

    return df


# Python Feature 2: function returning two values
def get_min_max_price(df):
    min_price = int(df["PRICE"].min())
    max_price = int(df["PRICE"].max())
    return min_price, max_price


# Python Feature 3: function with parameters and default arguments
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
    """Return a filtered copy of the DataFrame using all user choices."""
    # Data Analytics Feature 2: boolean filtering on multiple columns
    filtered = df[
        (df["PRICE"] >= min_price) &
        (df["PRICE"] <= max_price)
