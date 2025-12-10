"""
Name:       Tyler Rizzitano
CS230:      Section 3
Data:       New York Housing Market (NY-House-Dataset.csv)
URL:        https://trizz927-my-housing-app.streamlit.app/

Description:
This program works like a basic version of Zillow, only New York. You choose the area you want to live in,
the features you want in a home, and a price range. The app then shows you the homes that match 
your filters, displays charts about prices and locations, and provides a map showing where the 
properties are located.

References:
- Streamlit documentation: https://docs.streamlit.io/
- Matplotlib documentation: https://matplotlib.org/
- PyDeck documentation: https://deckgl.readthedocs.io/
- ChatGpt with a few lines that I did not know how to do for example making the numbers not scientific notation,
also to give me a base line for streamlit examples to build on (items used are my own though)
-Youtube to help teach me streamlit while I was stuck because I was not there for the class.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
#this was part of the ai usage below to get the numbers out of scientific notation
from matplotlib.ticker import FuncFormatter


# --------- FUNCTIONS ---------
# read the data
def load_data():
    df = pd.read_csv("NY-House-Dataset.csv")

    # remove rows within the data set that had nothing to aviod issues
    df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])
    df = df[df["PRICE"] > 0]

    return df


# [FUNCRETURN2] function that returns 2+ values
# carrying on this is how you can compare your filtered items to.
def get_summary_stats(df_input):
    """Return count, average price, average beds."""
    if len(df_input) == 0:
        return 0, 0.0, 0.0

    count = len(df_input)
    avg_price = float(df_input["PRICE"].mean())
    avg_beds = float(df_input["BEDS"].mean())
    return count, avg_price, avg_beds


# [FUNC2P] function with 2+ parameters and default values
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
    
    # [FILTER1] filter by one condition (price range)
    # [FILTER2] filter by two or more conditions (AND)
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


# Start of the streamlit area to start making the app

def main():

    st.title("New York Living - Online Assistant")
    # [ST3] use sidebar for layout
    st.sidebar.header("Search Options")

    df = load_data()

    # I wanted to split the for sale... and the housing type to make it an easeir search engine
    status_list = []
    ptype_list = []

    # [ITERLOOP] loop through items in a DataFrame column
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

    # [COLUMNS] adding new columns to DataFrame
    df["PROPERTY_TYPE"] = ptype_list
    df["STATUS"] = status_list

    # Overall data sumamry on app
    # [FUNCCALL2] get_summary_stats is called in 2+ places
    total_count, total_avg_price, total_avg_beds = get_summary_stats(df)
    st.subheader("Overall Dataset Summary")
    st.write("Total number of properties:", total_count)
    st.write("Overall average price: $", round(total_avg_price, 2))
    st.write("Overall average beds:", round(total_avg_beds, 2))

    # Start of the side bar

    # manual price input because the slider was to clanky for this so I move that to a simpler number area
    # [MAXMIN] find min and max values in column
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

    # [ST2] slider widget
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
    # [ST1] dropdown / selectbox
    bath_choice = st.sidebar.selectbox("Bathrooms", bath_options)

    # locality
    locality_unique = df["LOCALITY"].dropna().unique().tolist()
    locality_unique.sort()
    # [LISTCOMP] list comprehension
    locality_options = ["All"] + [loc for loc in locality_unique]
    locality_choice = st.sidebar.selectbox("Location", locality_options)

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

    # Filtered data that shows the statistics on what you are searching for
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

    # Filter summary on what properties are available for what you are looking for
    st.subheader("Filtered Properties Summary")

    count, avg_price, avg_beds = get_summary_stats(filtered_df)
    st.write("Number of properties:", count)

    if count > 0:
        st.write("Average price: $", round(avg_price, 2))
        st.write("Average beds:", round(avg_beds, 2))
    else:
        st.write("No results match your filters.")

    # Table
    if count > 0:
        # [SORT] sort data by one column
        sorted_df = filtered_df.sort_values("PRICE", ascending=False)
        st.dataframe(
            sorted_df[
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

    # Start of the bar chart
    st.subheader("Number of Homes by Locality (Top 10)")

    if count > 0:
        local_counts = filtered_df["LOCALITY"].value_counts().head(10)

        # [DICTMETHOD] use dictionary methods on value_counts result
        local_counts_dict = local_counts.to_dict()
        local_names = list(local_counts_dict.keys())
        local_values = list(local_counts_dict.values())

        # [CHART1] bar chart
        fig, ax = plt.subplots()
        ax.bar(local_counts.index, local_counts.values)
        plt.xticks(rotation=45, ha="right")
        ax.set_ylabel("Count")
        ax.set_xlabel("Locality")
        ax.set_title("Top 10 Localities by Number of Listings")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("Not enough data.")

    #Start of the histogram
    st.subheader("Histogram (Prices of Housing Options)")

    if count > 0:
        # [CHART2] second chart type (histogram)
        fig2, ax2 = plt.subplots()
        ax2.hist(filtered_df["PRICE"], bins=20)

        # I got help with this to get it out of scientific notation and put them into normal
        # numbers to make it easier to read.
        # [LAMBDA] lambda function inside FuncFormatter
        ax2.ticklabel_format(style='plain', axis='x')
        ax2.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: f"{int(x):,}")
        )

        ax2.set_xlabel("Price ($)")
        ax2.set_ylabel("Number of properties")
        ax2.set_title("Distribution of Prices")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.write("Not enough data for histogram.")

    # map where the info was inspired by the example we did in class
    st.subheader("Map of Properties")

    if count > 0:
        # [MAP] detailed map using PyDeck
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position="[LONGITUDE, LATITUDE]",
            get_radius=67,
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
