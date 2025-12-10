"""
Name:       Your Name
CS230:      Section XXX
Data:       New York Housing Market (NY-House-Dataset.csv)
URL:        (add your Streamlit Cloud URL here)

Description:
This Streamlit app explores New York housing data. The user can filter homes
by price range, bedrooms, bathrooms, locality, listing status, and property type.
The app shows a filtered table of homes, summary statistics, a bar chart by locality,
a histogram of prices, and a map of the filtered properties.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


# --------- FUNCTIONS ---------

def load_data():
    """Read the CSV file and clean it."""
    df = pd.read_csv("NY-House-Dataset.csv")

    # remove rows with missing critical fields
    df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])
    df = df[df["PRICE"] > 0]

    return df


def get_summary_stats(df_input):
    """Return count, average price, average beds."""
    if len(df_input) == 0:
        return 0, 0.0, 0.0

    count = len(df_input)
    avg_price = float(df_input["PRICE"].mean())
    avg_beds = float(df_input["BEDS"].mean())
    return count, avg_price, avg_beds


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
    
    # price filtering
    filtered = df[(df["PRICE"] >= min_price) & (df["PRICE"] <= max_price)]

    # bedroom RANGE filtering
    if bed_min is not None and bed_max is not None:
        filtered = filtered[
            (filtered["BEDS"] >= bed_min) & (filtered["BEDS"] <= bed_max)
        ]

    # bathrooms
    if bath_choice != "Any":
        filtered = filtered[filtered["BATH"] == bath_choice]

    # locality
    if locality_choice != "All":
        filtered = filtered[filtered["LOCALITY"] == locality_choice]

    # status
    if status_choice != "Any":
        filtered = filtered[filtered["STATUS"] == status_choice]

    # property type
    if ptype_choice != "Any":
        filtered = filtered[filtered["PROPERTY_TYPE"] == ptype_choice]

    return filtered


# --------- MAIN APP ---------

def main():

    st.title("New York Living - Online Assistant")
    st.sidebar.header("Filters")

    df = load_data()

    # ---------- SPLIT TYPE COLUMN ----------
    status_list = []
    ptype_list = []

    for value in df["TYPE"]:
        if isinstance(value, str):
            text = value.strip()
            text_lower = text.lower()
            words = text_lower.split()

            if "for sale" in text_lower:
                parts = text_lower.split("for sale")
                property_value = parts[0].strip().title()
                status_value = "For Sale"

            elif "for rent" in text_lower:
                parts = text_lower.split("for rent")
                property_value = parts[0].strip().title()
                status_value = "For Rent"

            elif "sold" in words:
                parts = text_lower.split("sold")
                property_value = parts[0].strip().title()
                status_value = "Sold"

            elif "pending" in words:
                parts = text_lower.split("pending")
                property_value = parts[0].strip().title()
                status_value = "Pending"

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

    # ------------ SIDEBAR FILTERS ------------

    # manual price input
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

    # bedroom slider
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
    baths_unique = sorted(df["BATH"].dropna().unique().tolist())
    bath_options = ["Any"] + baths_unique
    bath_choice = st.sidebar.selectbox("Bathrooms", bath_options)

    # locality
    locality_unique = df["LOCALITY"].dropna().unique().tolist()
    locality_unique.sort()
    locality_options = ["All"] + [loc for loc in locality_unique]
    locality_choice = st.sidebar.selectbox("Locality", locality_options)

    # status
    status_unique = df["STATUS"].dropna().unique().tolist()
    status_unique.sort()
    status_options = ["Any"] + status_unique
    status_choice = st.sidebar.selectbox("Listing Status", status_options)

    # property type
    ptype_unique = df["PROPERTY_TYPE"].dropna().unique().tolist()
    ptype_unique.sort()
    ptype_options = ["Any"] + ptype_unique
    ptype_choice = st.sidebar.selectbox("Property Type", ptype_options)

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

    # ------------ SUMMARY ------------
    st.subheader("Filtered Properties Summary")

    count, avg_price, avg_beds = get_summary_stats(filtered_df)
    st.write("Number of properties:", count)

    if count > 0:
        st.write("Average price: $", round(avg_price, 2))
        st.write("Average beds:", round(avg_beds, 2))
    else:
        st.write("No results match your filters.")

    # ------------ TABLE ------------
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

    # ------------ BAR CHART ------------
    st.subheader("Number of Homes by Locality (Top 10)")

    if count > 0:
        local_counts = filtered_df["LOCALITY"].value_counts().head(10)

        fig, ax = plt.subplots()
        ax.bar(local_counts.index, local_counts.values)
        plt.xticks(rotation=45, ha="right")
        ax.set_ylabel("Count")
        ax.set_xlabel("Locality")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("Not enough data.")

    # ------------ HISTOGRAM ------------
    st.subheader("Histogram of Prices (Filtered Data)")

    if count > 0:
        fig2, ax2 = plt.subplots()
        ax2.hist(filtered_df["PRICE"], bins=20)

        # I got help with this to get it out of scientific notation and put them into to normal numbers to make it easier to read.
        ax2.ticklabel_format(style='plain', axis='x')
        ax2.get_xaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"{int(x):,}")
        )

        ax2.set_xlabel("Price ($)")
        ax2.set_ylabel("Number of properties")
        ax2.set_title("Distribution of Prices")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.write("Not enough data for histogram.")

    # ------------ MAP ------------
    st.subheader("Map of Properties")

    if count > 0:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position="[LONGITUDE, LATITUDE]",
            get_radius=60,
            get_color=[200, 0, 0],
        )

        view_state = pdk.ViewState(
            longitude=float(filtered_df["LONGITUDE"].mean()),
            latitude=float(filtered_df["LATITUDE"].mean()),
            zoom=10,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
        )

        st.pydeck_chart(deck)
    else:
        st.write("No map data.")


if __name__ == "__main__":
    main()
