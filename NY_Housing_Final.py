"""
Name:       Your Name
CS230:      Section XXX
Data:       NY-House-Dataset.csv
URL:        (add your Streamlit Cloud URL here)

Description:
Simple Streamlit app to explore New York housing data.
User can filter by price range, bedrooms, bathrooms, locality,
listing status (for sale, for rent, etc.), and property type
(condo, house, co-op, etc.). The app shows a table, two charts,
and a map.
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

    # filter by listing status
    if status_choice != "Any":
        filtered = filtered[filtered["STATUS"] == status_choice]

    # filter by property type
    if ptype_choice != "Any":
        filtered = filtered[filtered["PROPERTY_TYPE"] == ptype_choice]

    return filtered


def get_summary_stats(filtered_df):
    """Return count and average price and average beds."""
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

    # ---------- SIMPLE SPLIT OF TYPE COLUMN ----------
    # Example values in TYPE: "Condo for sale", "House for rent", "Co-op for sale"
    status_list = []
    ptype_list = []

    for value in df["TYPE"]:
        if isinstance(value, str):
            text = value.strip()
            words = text.lower().split()

            # CASE 1: something "for sale"
            if "for" in words and "sale" in words:
                parts = text.lower().split("for")
                property_value = parts[0].strip().title()
                status_value = "For " + parts[1].strip().title()

            # CASE 2: something "for rent"
            elif "for" in words and "rent" in words:
                parts = text.lower().split("for")
                property_value = parts[0].strip().title()
                status_value = "For " + parts[1].strip().title()

            # CASE 3: something "sold"
            elif "sold" in words:
                parts = text.lower().split("sold")
                property_value = parts[0].strip().title()
                status_value = "Sold"

            # CASE 4: something "pending"
            elif "pending" in words:
                parts = text.lower().split("pending")
                property_value = parts[0].strip().title()
                status_value = "Pending"

            # OTHER CASES
            else:
                property_value = text.title()
                status_value = "Other"
        else:
            property_value = "Unknown"
            status_value = "Unknown"

        ptype_list.append(property_value)
        status_list.append(status_value)

    df["PROPERTY_TYPE"] = ptype_list
    df["STATUS"] = status_list

    # ------------ BUILD OPTIONS FOR FILTERS ------------

    # price range (slider)
    min_price = int(df["PRICE"].min())
    max_price = int(df["PRICE"].max())

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
    bed_options = ["Any"]
    for b in beds_unique:
        bed_options.append(b)
    bed_choice = st.sidebar.selectbox("Number of bedrooms", bed_options)

    # bathrooms
    baths_unique = df["BATH"].dropna().unique()
    baths_unique = sorted(baths_unique.tolist())
    bath_options = ["Any"]
    for b in baths_unique:
        bath_options.append(b)
    bath_choice = st.sidebar.selectbox("Number of bathrooms", bath_options)

    # locality
    locality_unique = df["LOCALITY"].dropna().unique().tolist()
    locality_unique.sort()
    locality_options = ["All"]
    for loc in locality_unique:
        locality_options.append(loc)
    locality_choice = st.sidebar.selectbox("Locality", locality_options)

    # listing status
    status_unique = df["STATUS"].dropna().unique().tolist()
    status_unique.sort()
    status_options = ["Any"]
    for s in status_unique:
        status_options.append(s)
    status_choice = st.sidebar.selectbox("Listing status", status_options)

    # property type
    ptype_unique = df["PROPERTY_TYPE"].dropna().unique().tolist()
    ptype_unique.sort()
    ptype_options = ["Any"]
    for p in ptype_unique:
        ptype_options.append(p)
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
                    "LOCALITY",
                    "ADDRESS",
                ]
            ]
        )

    # ------------ SIMPLE CHART 1: COUNT BY LOCALITY ------------
    st.subheader("Number of Homes by Locality (Top 10)")

    if count > 0:
        loc_counts = filtered_df["LOCALITY"].value_counts().head(10)

        fig, ax = plt.subplots()
        ax.bar(loc_counts.index, loc_counts.values)
        ax.set_ylabel("Number of homes")
        ax.set_xlabel("Locality")
        ax.set_title("Top 10 Localities by Number of Listings")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig)
    else:
        st.write("Not enough data for this chart.")

    # ------------ SIMPLE CHART 2: PRICE HISTOGRAM ------------
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

    # ------------ SIMPLE MAP WITH PYDECK ------------
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
        )

        st.pydeck_chart(deck)
    else:
        st.write("No locations to show on the map.")


if __name__ == "__main__":
    main()
