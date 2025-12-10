"""
Name:       Your Name
CS230:      Section XXX
Data:       NY-House-Dataset.csv
URL:        (add your Streamlit Cloud URL here)

Description:
Simple Streamlit app to explore New York housing data.
You can choose a maximum price, minimum beds, and locality.
The app shows the filtered rows, summary statistics, two charts, and a map.

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


# Python Feature 3: function with parameters and a default argument
def filter_data(df, max_price, min_beds=0, locality_choice="All"):
    """Return a filtered copy of the DataFrame."""
    # Data Analytics Feature 2: boolean filtering on multiple columns
    filtered = df[df["PRICE"] <= max_price]
    filtered = filtered[filtered["BEDS"] >= min_beds]

    if locality_choice != "All":
        filtered = filtered[filtered["LOCALITY"] == locality_choice]

    return filtered


# Python Feature 4: function computing summary numbers
def get_summary_stats(filtered_df):
    if len(filtered_df) == 0:
        return 0, 0.0, 0.0

    count = len(filtered_df)
    avg_price = float(filtered_df["PRICE"].mean())
    avg_beds = float(filtered_df["BEDS"].mean())
    return count, avg_price, avg_beds


def main():
    st.title("New York Housing Explorer")

    # Streamlit Feature 1: sidebar layout
    st.sidebar.header("Filters")

    # -------------- LOAD DATA --------------
    df = load_data()

    # Data Analytics Feature 3: create a new derived column
    df["PRICE_PER_SQFT"] = df["PRICE"] / df["PROPERTYSQFT"].replace(0, pd.NA)

    # Python Feature 5: list comprehension to build locality list
    locality_unique = df["LOCALITY"].dropna().unique()
    locality_list = [loc for loc in locality_unique]
    locality_list.sort()
    locality_list = ["All"] + locality_list

    # use helper to get min and max for slider
    min_price, max_price = get_min_max_price(df)

    # Streamlit Feature 2: sliders
    max_price_choice = st.sidebar.slider(
        "Maximum price ($)",
        min_value=min_price,
        max_value=max_price,
        value=max_price,
        step=50000,
    )

    min_beds_choice = st.sidebar.slider(
        "Minimum number of bedrooms",
        min_value=0,
        max_value=int(df["BEDS"].max()),
        value=0,
        step=1,
    )

    # Streamlit Feature 3: selectbox
    locality_choice = st.sidebar.selectbox("Locality", locality_list)

    # -------------- FILTER DATA --------------
    filtered_df = filter_data(
        df,
        max_price=max_price_choice,
        min_beds=min_beds_choice,
        locality_choice=locality_choice,
    )

    # -------------- SUMMARY STATS --------------
    st.subheader("Filtered Properties")

    count, avg_price, avg_beds = get_summary_stats(filtered_df)
    st.write("Number of properties:", count)

    if count > 0:
        st.write("Average price of filtered homes: $", round(avg_price, 2))
        st.write("Average number of bedrooms:", round(avg_beds, 2))
    else:
        st.write("No rows match these filters.")

    # short “story” text
    st.write(
        "This table lets us explore how price and size change across different areas "
        "of New York when we change the filters in the sidebar."
    )

    # Show selected columns only
    if count > 0:
        st.dataframe(
            filtered_df[
                [
                    "TYPE",
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

    # -------------- VISUALIZATION 1: BAR CHART --------------
    st.subheader("Average Price by Locality (Top 10)")

    if count > 0:
        # Data Analytics Feature 4: groupby + mean + sort
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

        # Visualization Feature 1: Matplotlib bar chart in Streamlit
        st.pyplot(fig)

        st.write(
            "This bar chart shows which localities have the highest average prices "
            "under the current filters."
        )
    else:
        st.write("Not enough data for the chart.")

    # -------------- VISUALIZATION 2: HISTOGRAM --------------
    st.subheader("Histogram of Prices (Filtered Data)")

    if count > 0:
        fig2, ax2 = plt.subplots()
        ax2.hist(filtered_df["PRICE"], bins=20)
        ax2.set_xlabel("Price ($)")
        ax2.set_ylabel("Count of properties")
        ax2.set_title("Distribution of Prices")
        plt.tight_layout()

        # Visualization Feature 2: Matplotlib histogram
        st.pyplot(fig2)

        st.write(
            "The histogram shows how many properties fall into different price ranges "
            "for the chosen filters."
        )
    else:
        st.write("Not enough data for the histogram.")

    # -------------- VISUALIZATION 3: MAP --------------------
    st.subheader("Map of Properties")

    if count > 0:
        # Visualization Feature 3: PyDeck map
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
            tooltip={"text": "Price: ${PRICE}\nBeds: {BEDS}\n{ADDRESS}"},
        )

        st.pydeck_chart(deck)
        st.write(
            "Each point on the map shows a property that matches the filters. "
            "This helps us see where listings are concentrated."
        )
    else:
        st.write("No locations to show on the map.")


if __name__ == "__main__":
    main()
