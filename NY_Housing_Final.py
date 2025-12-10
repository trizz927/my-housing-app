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
    filtered = df[(df["PRICE"] >= min_price) & (df["PRICE"] <= max_price)]

    if bed_choice != "Any":
        filtered = filtered[filtered["BEDS"] == bed_choice]

    if bath_choice != "Any":
        filtered = filtered[filtered["BATH"] == bath_choice]

    if locality_choice != "All":
        filtered = filtered[filtered["LOCALITY"] == locality_choice]

    if status_choice != "Any":
        filtered = filtered[filtered["STATUS"] == status_choice]

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
        df["PRICE_PER_SQFT"] = df["PRICE"] / df["PROPERTYSQFT"]
    else:
        df["PRICE_PER_SQFT"] = None

    # ------------ SPLIT TYPE INTO STATUS + PROPERTY_TYPE ------------
    status_list = []
    ptype_list = []

    for value in df["TYPE"]:
        # handle values like "FOR SALE - Condo"
        if isinstance(value, str) and " - " in value:
            parts = value.split(" - ")
            status_value = parts[0]
            ptype_value = parts[1]
        else:
            # if it's missing or in a different format
            status_value = value
            ptype_value = "Unknown"

        status_list.append(status_value)
        ptype_list.append(ptype_value)

    df["STATUS"] = status_list
    df["PROPERTY_TYPE"] = ptype_list

    # ------------ BUILD OPTIONS FOR FILTERS ------------

    # price range
    min_price, max_price = get_min_max_price(df)

    price_min, price_max = st.sidebar.slider(
        "Price range ($)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=50000,
    )

    # bedrooms
    beds_unique = df["BEDS"].dropna().unique()
    beds_unique = sorted(beds_unique.astype(int).tolist())
    bed_options = ["Any"] + beds_unique
    bed_choice = st.sidebar.selectbox("Number of bedrooms", bed_options)

    # bathrooms
    baths_unique = df["BATH"].dropna().unique()
    baths_unique = sorted(baths_unique.tolist())
    bath_options = ["Any"] + baths_unique
    bath_choice = st.sidebar.selectbox("Number of bathrooms", bath_options)

    # locality
    locality_unique = df["LOCALITY"].dropna().unique().tolist()
    locality_unique.sort()
    locality_options = ["All"] + locality_unique
    locality_choice = st.sidebar.selectbox("Locality", locality_options)

    # listing status (For Sale, For Rent, Sold, etc.)
    status_unique = df["STATUS"].dropna().unique().tolist()
    status_unique.sort()
    status_options = ["Any"] + status_unique
    status_choice = st.sidebar.selectbox("Listing status", status_options)

    # property type (Condo, Apartment, House, etc.)
    ptype_unique = df["PROPERTY_TYPE"].dropna().unique().tolist()
    ptype_unique.sort()
    ptype_options = ["Any"] + ptype_unique
    ptype_choice = st.sidebar.selectbox("Property type", ptype_options)

    # ------------ FILTER DATA ------------
    filtered_df = filter_data(
        df,
        min_price=price_min,
        max_price=price_max,
        bed_choice=bed_choice,
        bath_choice=bath_choice,
        locality_choice=locality_choice,
        status_choice=status_choice,
        ptype_choice=ptype_choice,
    )

    # ------------ SUMMARY + TABLE ------------
    st.subheader("Filtered Properties")

    count, avg_price, avg_beds = get_summary_stats(filtered_df)
    st.write("Number of properties:", count)

    if count > 0:
        st.write("Average price: $", round(avg_price, 2))
        st.write("Average number of bedrooms:", round(avg_beds, 2))
    else:
        st.write("No rows match these filters.")

    st.write(
        "Use the filters in the sidebar to search for homes by price range, "
        "bedrooms, bathrooms, area, listing status, and property type."
    )

    if count > 0:
        st.dataframe(
            filtered_df[
                [
                    "STATUS",
                    "PROPERTY_TYPE",
                    "PRICE",
                    "BEDS",
                    "BATH",
                    "PROPERTYSQFT",
                    "LOCALITY",
                    "ADDRESS",
                    "PRICE_PER_SQFT",
                ]
            ]
        )

    # ------------ CHART 1: AVERAGE PRICE BY LOCALITY ------------
    st.subheader("Average Price by Locality (Top 10)")

    if count > 0:
        avg_by_loc = (
            filtered_df.groupby("LOCALITY")["PRICE"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
        )

        fig, ax = plt.subplots()
        ax.bar(avg_by_loc.index, avg_by_loc.values)
        ax.set_ylabel("Average Price ($)")
        ax.set_xlabel("Locality")
        ax.set_title("Top Localities by Average Price")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig)
    else:
        st.write("Not enough data for this chart.")

    # ------------ CHART 2: PRICE HISTOGRAM ------------
    st.subheader("Histogram of Prices (Filtered Data)")

    if count > 0:
        fig2, ax2 = plt.subplots()
        ax2.hist(filtered_df["PRICE"], bins=20)
        ax2.set_xlabel("Price ($)")
        ax2.set_ylabel("Number of properties")
        ax2.set_title("Distribution of Prices")
        plt.tight_layout()

        st.pyplot(fig2)
    else:
        st.write("Not enough data for the histogram.")

    # ------------ MAP WITH PYDECK ------------
    st.subheader("Map of Properties")

    if count > 0:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position="[LONGITUDE, LATITUDE]",
            get_radius=50,
            get_color=[200, 0, 0],
        )

        view_state = pdk.ViewState(
            longitude=float(filtered_df["LONGITUDE"].mean()),
            latitude=float(filtered_df["LATITUDE"].mean()),
            zoom=9,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "Status: {STATUS}\nType: {PROPERTY_TYPE}\n"
                        "Price: ${PRICE}\nBeds: {BEDS}\nBaths: {BATH}\n{ADDRESS}"
            },
        )

        st.pydeck_chart(deck)
    else:
        st.write("No locations to show on the map.")


if __name__ == "__main__":
    main()
