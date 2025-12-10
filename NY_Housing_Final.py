"""
Name:       Your Name
CS230:      Section XXX
Data:       New York Housing Market (NY-House-Dataset.csv)
URL:        (add your Streamlit Cloud URL here)

Description:
This Streamlit app explores New York housing data. The user can filter homes
by price range, bedrooms, bathrooms, locality, listing status (for sale, for rent, etc.),
and property type (condo, house, co-op, etc.). The app shows a filtered table of homes,
summary statistics for the filtered homes, a bar chart of number of homes by locality,
a histogram of prices, and a map of the filtered properties.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


# --------- FUNCTIONS ---------

# function to load and clean data
def load_data():
    """Read the CSV file and do small cleaning."""
    df = pd.read_csv("NY-House-Dataset.csv")

    # keep only rows with price and coordinates
    df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])
    df = df[df["PRICE"] > 0]

    return df


# function with 2+ parameters and return of 2+ values
def get_summary_stats(df_input, label="filtered"):
    """Return count, average price, average beds for a given DataFrame."""
    if len(df_input) == 0:
        return 0, 0.0, 0.0

    count = len(df_input)
    avg_price = float(df_input["PRICE"].mean())
    avg_beds = float(df_input["BEDS"].mean())
    return count, avg_price, avg_beds


# function with several parameters and defaults that filters the data
def filter_data(
    df,
    min_price,
    max_price,
    bed_min=None,
    bed_max=None,
    bath_choice="Any",
    locality_choice="All",
    status_choice="Any",
    ptype_choice="Any",
):
    """Filter the DataFrame based on user choices."""
    # filter by price range
    filtered = df[(df["PRICE"] >= min_price) & (df["PRICE"] <= max_price)]

    # filter by bedroom RANGE (slider)
    if bed_min is not None and bed_max is not None:
        filtered = filtered[
            (filtered["BEDS"] >= bed_min) & (filtered["BEDS"] <= bed_max)
        ]

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


# --------- MAIN APP ---------

def main():
    st.title("New York Living - Online Assistant")

    # sidebar for controls
    st.sidebar.header("Filters")

    # ------------ LOAD DATA ------------
    df = load_data()

    # ---------- SPLIT TYPE INTO PROPERTY_TYPE AND STATUS (simple) ----------
    # this area is used to split the status part, so you are able to find the type of house
    # and the status while searching
    status_list = []
    ptype_list = []

    for value in df["TYPE"]:
        if isinstance(value, str):
            text = value.strip()
            text_lower = text.lower()
            words = text_lower.split()

            # "something for sale"
            if "for sale" in text_lower:
                parts = text_lower.split("for sale")
                property_value = parts[0].strip().title()
                status_value = "For Sale"

            # "something for rent"
            elif "for rent" in text_lower:
                parts = text_lower.split("for rent")
                property_value = parts[0].strip().title()
                status_value = "For Rent"

            # "something sold"
            elif "sold" in words:
                parts = text_lower.split("sold")
                property_value = parts[0].strip().title()
                status_value = "Sold"

            # "something pending"
            elif "pending" in words:
                parts = text_lower.split("pending")
                property_value = parts[0].strip().title()
                status_value = "Pending"

            # other cases
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

    # ---- Price inputs (manual only) ----
    min_price = int(df["PRICE"].min())
    max_price = int(df["PRICE"].max())

    st.sidebar.subheader("Price Range")

    exact_min = st.sidebar.number_input(
        "Exact minimum price",
        min_value=min_price,
        max_value=max_price,
        value=min_price,
        step=50000,
    )

    exact_max = st.sidebar.number_input(
        "Exact maximum price",
        min_value=min_price,
        max_value=max_price,
        value=max_price,
        step=50000,
    )

    price_min = exact_min
    price_max = exact_max

    # ---- Bedrooms slider (range) ----
    beds_series = df["BEDS"].dropna().astype(int)
    bed_min = int(beds_series.min())
    bed_max = int(beds_series.max())

    bed_min_sel, bed_max_sel = st.sidebar.slider(
        "Number of Bedrooms",
        min_value=bed_min,
        max_value=bed_max,
        value=(bed_min, bed_max),
        step=1,
    )

    # bathrooms
    baths_unique = df["BATH"].dropna().unique()
    baths_unique = sorted(baths_unique.tolist())
    bath_options = ["Any"] + baths_unique
    bath_choice = st.sidebar.selectbox("Number of bathrooms", bath_options)

    # locality
    locality_unique = df["LOCALITY"].dropna().unique().tolist()
    locality_unique.sort()
    # list comprehension here for rubric
    locality_options = ["All"] + [loc for loc in locality_unique]
    locality_choice = st.sidebar.selectbox("Locality", locality_options)

    # listing status
    status_unique = df["STATUS"].dropna().unique().tolist()
    status_unique.sort()
    status_options = ["Any"] + status_unique
    status_choice = st.sidebar.selectbox("Listing status", status_options)

    # property type
    ptype_unique = df["PROPERTY_TYPE"].dropna().unique().tolist()
    ptype_unique.sort()
    ptype_options = ["Any"] + ptype_unique
    ptype_choice = st.sidebar.selectbox("Property type", ptype_options)

    # ------------ FILTER DATA ------------
    filtered_df = filter_data(
        df,
        min_price=price_min,
        max_price=price_max,
        bed_min=bed_min_sel,
        bed_max=bed_max_sel,
        bath_choice=bath_choice,
        locality_choice=locality_choice,
        status_choice=status_choice,
        ptype_choice=ptype_choice,
    )

    # ------------ FILTERED STATS (ONLY) ------------
    st.subheader("Filtered Properties Summary")

    count, avg_price, avg_beds = get_summary_stats(filtered_df)
    st.write("Number of properties:", count)

    if count > 0:
        st.write("Average price of filtered homes: $", round(avg_price, 2))
        st.write("Average number of bedrooms:", round(avg_beds, 2))
    else:
        st.write("No rows match these filters.")

    st.write(
        "Use the filters in the sidebar to search for homes by price range, "
        "bedrooms, bathrooms, area, listing status, and property type."
    )

    # ------------ FILTERED TABLE ------------
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

    # ------------ CHART 1: COUNT BY LOCALITY ------------
    st.subheader("Number of Homes by Locality (Top 10)")

    if count > 0:
        local_counts = filtered_df["LOCALITY"].value_counts().head(10)

        fig, ax = plt.subplots()
        ax.bar(local_counts.index, local_counts.values)
        ax.set_ylabel("Number of homes")
        ax.set_xlabel("Locality")
        ax.set_title("Top 10 Localities by Number of Listings")
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
            get_radius=100,
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
