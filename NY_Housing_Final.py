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
    ]

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

    # Split TYPE into STATUS and PROPERTY_TYPE
    # (e.g., "FOR SALE - Condo" -> STATUS="FOR SALE", PROPERTY_TYPE="Condo")
    df["STATUS"] = df["TYPE"].apply(
        lambda x: x.split(" - ")[0] if isinstance(x, str) and " - " in x else x
    )
    df["PROPERTY_TYPE"] = df["TYPE"].apply(
        lambda x: x.split(" - ")[1] if isinstance(x, str) and " - " in x else "Unknown"
    )

    # Python Feature 5: list comprehension to build locality list
    locality_unique = df["LOCALITY"].dropna().unique()
    locality_list = [loc for loc in locality_unique]
    locality_list.sort()
    locality_list = ["All"] + locality_list

    # Listing status list
    status_unique = df["STATUS"].dropna().unique().tolist()
    status_unique.sort()
    status_list = ["Any"] + status_unique

    # Property type list
    ptype_unique = df["PROPERTY_TYPE"].dropna().unique().tolist()
    ptype_unique.sort()
    ptype_list = ["Any"] + ptype_unique

    # use helper to get min and max for slider
    min_price, max_price = get_min_max_price(df)

    # --------- SIDEBAR: PRICE RANGE (min + max) ----------
    # Streamlit Feature 2: range slider (you can slide OR type values)
    price_min, price_max = st.sidebar.slider(
        "Price range ($)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=50000,
    )

    # --------- SIDEBAR: BEDROOMS ----------
    beds_unique = sorted(df["BEDS"].dropna().unique().astype(int).tolist())
    bed_options = ["Any"] + beds_unique
    bed_choice = st.sidebar.selectbox("Number of bedrooms", bed_options)

    # --------- SIDEBAR: BATHROOMS ----------
    baths_unique = sorted(df["BATH"].dropna().unique().tolist())
    bath_options = ["Any"] + baths_unique
    bath_choice = st.sidebar.selectbox("Number of bathrooms", bath_options)

    # --------- SIDEBAR: LOCALITY ----------
    # Streamlit Feature 3: selectbox
    locality_choice = st.sidebar.selectbox("Locality", locality_list)

    # --------- SIDEBAR: LISTING STATUS ----------
    status_choice = st.sidebar.selectbox("Listing status", status_list)

    # --------- SIDEBAR: PROPERTY TYPE ----------
    ptype_choice = st.sidebar.selectbox("Property type", ptype_list)

    # -------------- FILTER DATA --------------
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

    # -------------- SUMMARY STATS --------------
    st.subheader("Filtered Properties")

    count, avg_price, avg_beds = get_summary_stats(filtered_df)
    st.write("Number of properties:", count)

    if count > 0:
        st.write("Average price of filtered homes: $", round(avg_price, 2))
        st.write("Average number of bedrooms:", round(avg_beds, 2))
    else:
        st.write("No rows match these filters.")

    st.write(
        "Use the filters in the sidebar to look for homes in a price range, "
        "with a specific number of bedrooms and bathrooms, in a chosen locality, "
        "and with a particular listing status and property type."
    )

    # Show selected columns only
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
            "for homes that match your chosen filters."
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
            "for the current filters."
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
            tooltip={
                "text": "Status: {STATUS}\nType: {PROPERTY_TYPE}\n"
                        "Price: ${PRICE}\nBeds: {BEDS}\nBaths: {BATH}\n{ADDRESS}"
            },
        )

        st.pydeck_chart(deck)
        st.write(
            "Each point on the map shows a property that matches your chosen "
            "bedrooms, bathrooms, price range, status, property type, and area."
        )
    else:
        st.write("No locations to show on the map.")


if __name__ == "__main__":
    main()
