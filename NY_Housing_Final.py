"""
Name:       Your Name
CS230:      Section XXX
Data:       New York Housing Market
URL:        https://trizz927-my-housing-app.streamlit.app/

Description:
This Streamlit app explores New York housing data. The user can filter homes
by price range, bedrooms, bathrooms, locality, listing status (for sale, for rent, etc.),
and property type (condo, house, co-op, etc.). The app shows a filtered table of homes,
summary statistics, a bar chart of number of homes by locality, a histogram of prices,
and a map of the filtered properties.

References:
- Streamlit docs: https://docs.streamlit.io/
- PyDeck docs: https://deckgl.readthedocs.io/
- Matplotlib docs: https://matplotlib.org/

Some layout and comments were helped by ChatGPT, but I understand the code.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


# Python Feature: basic function to load data
def load_data():
    """Read the CSV file and do small cleaning."""
    df = pd.read_csv("NY-House-Dataset.csv")

    # keep only rows with price and coordinates
    df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])
    df = df[df["PRICE"] > 0]

    return df


# [FUNC2P] function with two or more parameters, one with a default value
# [FUNCRETURN2] function that returns two or more values
def get_summary_stats(df_input, label=""):
    """Return count, average price, average beds for a given DataFrame."""
    if len(df_input) == 0:
        return 0, 0.0, 0.0

    count = len(df_input)
    avg_price = float(df_input["PRICE"].mean())
    avg_beds = float(df_input["BEDS"].mean())
    return count, avg_price, avg_beds


# [FUNC2P] (again) and [FUNCCALL2] (we call this in main() multiple times)
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
    # [FILTER2] filter data by two or more conditions (price min AND max)
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


def main():
    st.title("New York Housing Explorer")

    # [ST3] page design feature: sidebar
    st.sidebar.header("Filters")

    # ------------ LOAD DATA ------------
    df = load_data()

    # [COLUMNS] Add new columns to the DataFrame by splitting TYPE
    # Example values in TYPE: "Condo for sale", "House for rent", "Co-op for sale"
    status_list = []
    ptype_list = []

    # [ITERLOOP] loop that iterates through items in a DataFrame column
    for value in df["TYPE"]:
        if isinstance(value, str):
            text = value.strip()
            words = text.lower().split()

            # "something for sale"
            if "for" in words and "sale" in words:
                parts = text.lower().split("for")
                property_value = parts[0].strip().title()
                status_value = "For " + parts[1].strip().title()

            # "something for rent"
            elif "for" in words and "rent" in words:
                parts = text.lower().split("for")
                property_value = parts[0].strip().title()
                status_value = "For " + parts[1].strip().title()

            # "something sold"
            elif "sold" in words:
                parts = text.lower().split("sold")
                property_value = parts[0].strip().title()
                status_value = "Sold"

            # "something pending"
            elif "pending" in words:
                parts = text.lower().split("pending")
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

    # [MAXMIN] find minimum and maximum price values
    min_price = int(df["PRICE"].min())
    max_price = int(df["PRICE"].max())

    # ------------ STREAMLIT FILTER WIDGETS ------------

    # [ST2] slider (double-ended slider)
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
    # [LISTCOMP] list comprehension to build options
    bed_options = ["Any"] + [b for b in beds_unique]

    # [ST1] dropdown / selectbox
    bed_choice = st.sidebar.selectbox("Number of bedrooms", bed_options)

    # bathrooms
    baths_unique = df["BATH"].dropna().unique()
    baths_unique = sorted(baths_unique.tolist())
    bath_options = ["Any"] + [b for b in baths_unique]
    bath_choice = st.sidebar.selectbox("Number of bathrooms", bath_options)

    # locality
    locality_unique = df["LOCALITY"].dropna().unique().tolist()
    locality_unique.sort()
    locality_options = ["All"] + locality_unique
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

    # ------------ OVERALL SUMMARY (before filtering) ------------
    st.subheader("Overall Summary (All Properties)")
    # [FUNCCALL2] using get_summary_stats in more than one place
    total_count, total_avg_price, total_avg_beds = get_summary_stats(df, "All")
    st.write("Total number of properties:", total_count)
    st.write("Average price (all properties): $", round(total_avg_price, 2))
    st.write("Average number of bedrooms (all properties):", round(total_avg_beds, 2))

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

    count, avg_price, avg_beds = get_summary_stats(filtered_df, "Filtered")
    st.write("Number of filtered properties:", count)

    if count > 0:
        st.write("Average price (filtered): $", round(avg_price, 2))
        st.write("Average number of bedrooms (filtered):", round(avg_beds, 2))
    else:
        st.write("No rows match these filters.")

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

    st.write(
        "Use the filters in the sidebar to search for homes by price range, "
        "bedrooms, bathrooms, area, listing status, and property type."
    )

    # ------------ CHART 1: COUNT BY LOCALITY ------------
    st.subheader("Number of Homes by Locality (Top 10)")

    if count > 0:
        # [FILTER1] simple filter example: only localities that appear in filtered_df
        loc_counts = filtered_df["LOCALITY"].value_counts().head(10)

        # [SORT] sort by locality name (index) for nicer display
        loc_counts = loc_counts.sort_index()

        # [CHART1] bar chart with labels and title
        fig, ax = plt.subplots()
        ax.bar(loc_counts.index, loc_counts.values)
        ax.set_ylabel("Number of homes")
        ax.set_xlabel("Locality")
        ax.set_title("Top Localities by Number of Listings")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig)
    else:
        st.write("Not enough data for this chart.")

    # ------------ CHART 2: PRICE HISTOGRAM ------------
    st.subheader("Histogram of Prices (Filtered Data)")

    if count > 0:
        # [CHART2] second chart type (histogram)
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
        # [MAP] customized PyDeck map with tooltips
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
