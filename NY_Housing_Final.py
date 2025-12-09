"""
Name:       Your Name
CS230:      Section XXX
Data:       New York Housing Market
URL:        (add Streamlit Cloud URL here if you deploy it)

Description:
This program is an interactive Streamlit web app that explores New York
housing data. Users can filter by price, beds, baths, location, and
property type, and see the results in tables, charts, and a map.
The app includes summary statistics, charts of average prices and
price vs. square footage, and a PyDeck map of properties.

References:
- Streamlit docs: https://docs.streamlit.io/
- PyDeck docs: https://deckgl.readthedocs.io/
- Matplotlib docs: https://matplotlib.org/
"""

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk

DATA_PATH = "NY-House-Dataset.csv"


# ----------------- DATA LOADING & UTILITIES ----------------- #

# [FUNC2P] function with 2+ parameters, one with default
@st.cache_data
def load_data(path=DATA_PATH, nrows=None):
    """Load housing data from CSV and do basic cleaning."""
    df = pd.read_csv(path, nrows=nrows)
    # basic cleaning
    df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])
    df = df[df["PRICE"] > 0]
    return df


# [FUNCRETURN2] function that returns two values
def get_price_range(df):
    """Return (min_price, max_price) from the DataFrame."""
    min_price = int(df["PRICE"].min())
    max_price = int(df["PRICE"].max())
    return min_price, max_price


def add_price_per_sqft(df):
    """Add a price per square foot column if square footage is available."""
    # [LAMBDA] using lambda function
    df = df.copy()
    df["PRICE_PER_SQFT"] = df.apply(
        lambda row: row["PRICE"] / row["PROPERTYSQFT"]
        if row.get("PROPERTYSQFT", 0) and row["PROPERTYSQFT"] > 0
        else np.nan,
        axis=1,
    )
    return df


def filter_properties(
    df,
    max_price,
    min_beds,
    min_baths,
    selected_locality,
    selected_types,
):
    """
    Filter properties based on price, beds, baths, locality, and type.
    """
    # [FILTER1] simple filter by max price
    filtered = df[df["PRICE"] <= max_price]

    # [FILTER2] filter with multiple conditions
    filtered = filtered[
        (filtered["BEDS"] >= min_beds)
        & (filtered["BATH"] >= min_baths)
    ]

    if selected_locality != "All":
        filtered = filtered[filtered["LOCALITY"] == selected_locality]

    if selected_types:
        filtered = filtered[filtered["TYPE"].isin(selected_types)]

    # [SORT] sort by price descending
    filtered = filtered.sort_values("PRICE", ascending=False)
    return filtered


def summarize_stats(df):
    """Return a small dictionary of summary statistics."""
    stats = {
        "Number of properties": len(df),
        "Average price": df["PRICE"].mean(),
        "Average beds": df["BEDS"].mean(),
        "Average baths": df["BATH"].mean(),
    }
    # [DICTMETHOD] using dictionary methods
    # Example methods: .items() and .get()
    _ = list(stats.items())
    _ = stats.get("Average price", 0)
    return stats


# ----------------- MAIN STREAMLIT APP ----------------- #

def main():
    st.set_page_config(
        page_title="NY Housing Explorer",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # [ST3] simple page design feature: custom title styling
    st.markdown(
        "<h1 style='text-align:center; color:#1f4e79;'>New York Housing Data Explorer</h1>",
        unsafe_allow_html=True,
    )
    st.write("Use the controls in the sidebar to explore the New York housing market.")

    # [FUNCCALL2] load_data is called in more than one place if needed
    df = load_data()
    df = add_price_per_sqft(df)

    # ------------- SIDEBAR CONTROLS ------------- #
    st.sidebar.header("Filter Options")

    # [LISTCOMP] list comprehension for property types
    property_types = [t for t in sorted(df["TYPE"].dropna().unique())]

    # [ST1] dropdown / multiselect
    selected_locality = st.sidebar.selectbox(
        "Select Locality (city/borough)",
        options=["All"] + sorted(df["LOCALITY"].dropna().unique()),
    )

    selected_types = st.sidebar.multiselect(
        "Property type(s)",
        options=property_types,
        default=property_types,
    )

    min_price, max_price = get_price_range(df)

    # [ST2] slider
    price_limit = st.sidebar.slider(
        "Maximum price ($)",
        min_value=min_price,
        max_value=max_price,
        value=min(min_price * 10, max_price),
        step=10000,
    )

    min_beds = st.sidebar.slider("Minimum beds", 0, int(df["BEDS"].max()), 0, 1)
    min_baths = st.sidebar.slider(
        "Minimum baths", 0.0, float(df["BATH"].max()), 0.0, 0.5
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Adjust filters to update charts, tables, and the map below.")

    # Apply filters
    filtered_df = filter_properties(
        df,
        max_price=price_limit,
        min_beds=min_beds,
        min_baths=min_baths,
        selected_locality=selected_locality,
        selected_types=selected_types,
    )

    # ----------------- TOP METRICS ----------------- #
    stats = summarize_stats(filtered_df)

    cols = st.columns(4)
    # [ITERLOOP] iterating through dictionary items
    for col, (label, value) in zip(cols, stats.items()):
        with col:
            if "price" in label.lower():
                col.metric(label, f"${value:,.0f}")
            else:
                col.metric(label, f"{value:,.2f}")

    # ----------------- DATA TABLE ----------------- #
    st.subheader("Filtered Properties")

    show_cols = [
        "TYPE",
        "PRICE",
        "BEDS",
        "BATH",
        "PROPERTYSQFT",
        "LOCALITY",
        "SUBLOCALITY",
        "ADDRESS",
        "PRICE_PER_SQFT",
    ]
    existing_show_cols = [c for c in show_cols if c in filtered_df.columns]
    st.dataframe(filtered_df[existing_show_cols], use_container_width=True)

    # ----------------- CHART 1: AVG PRICE BY LOCALITY ----------------- #
    st.markdown("### Average Price by Locality (Top 10)")

    if not filtered_df.empty:
        avg_price_by_loc = (
            filtered_df.groupby("LOCALITY")["PRICE"].mean().sort_values(ascending=False)
        )
        avg_price_by_loc = avg_price_by_loc.head(10)

        fig1, ax1 = plt.subplots()
        # [CHART1] bar chart with custom labels, rotation, etc.
        ax1.bar(avg_price_by_loc.index, avg_price_by_loc.values)
        ax1.set_ylabel("Average Price ($)")
        ax1.set_xlabel("Locality")
        ax1.set_title("Top 10 Localities by Average Listing Price")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig1)
    else:
        st.info("No properties match the current filters for this chart.")

    # ----------------- CHART 2: PRICE VS SQFT SCATTER ----------------- #
    st.markdown("### Price vs. Property Square Footage")

    scatter_df = filtered_df.dropna(subset=["PROPERTYSQFT", "PRICE"])
    if not scatter_df.empty:
        fig2, ax2 = plt.subplots()
        # [CHART2] scatter plot
        sc = ax2.scatter(
            scatter_df["PROPERTYSQFT"],
            scatter_df["PRICE"],
            alpha=0.6,
        )
        ax2.set_xlabel("Square Footage")
        ax2.set_ylabel("Price ($)")
        ax2.set_title("Price vs. Square Footage")
        plt.tight_layout()

        st.pyplot(fig2)
    else:
        st.info("Not enough data with both price and square footage for this chart.")

    # ----------------- PIVOT TABLE ----------------- #
    st.markdown("### Average Price by Locality and Property Type (Pivot Table)")

    if not filtered_df.empty:
        # [PIVOTTABLE] pivot analysis
        pivot = filtered_df.pivot_table(
            values="PRICE",
            index="LOCALITY",
            columns="TYPE",
            aggfunc="mean",
        )
        st.dataframe(pivot.style.format("${:,.0f}"), use_container_width=True)
    else:
        st.info("No data available for pivot table with current filters.")

    # [COLUMNS] was used when adding PRICE_PER_SQFT in add_price_per_sqft()

    # [MAXMIN] find most expensive and cheapest properties
    st.markdown("### Price Extremes in Filtered Results")
    if not filtered_df.empty:
        max_row = filtered_df.loc[filtered_df["PRICE"].idxmax()]
        min_row = filtered_df.loc[filtered_df["PRICE"].idxmin()]

        col_max, col_min = st.columns(2)
        with col_max:
            st.write("#### Most Expensive Listing")
            st.write(f"**Price:** ${max_row['PRICE']:,.0f}")
            st.write(f"**Type:** {max_row['TYPE']}")
            st.write(f"**Beds/Baths:** {max_row['BEDS']} / {max_row['BATH']}")
            st.write(f"**Address:** {max_row['ADDRESS']}")
        with col_min:
            st.write("#### Least Expensive Listing")
            st.write(f"**Price:** ${min_row['PRICE']:,.0f}")
            st.write(f"**Type:** {min_row['TYPE']}")
            st.write(f"**Beds/Baths:** {min_row['BEDS']} / {min_row['BATH']}")
            st.write(f"**Address:** {min_row['ADDRESS']}")
    else:
        st.info("No properties to show extremes for.")

    # ----------------- MAP ----------------- #
    st.markdown("### Map of Properties")

    if not filtered_df.empty:
        # [MAP] PyDeck detailed map with tooltips
        map_df = filtered_df[
            ["LATITUDE", "LONGITUDE", "PRICE", "TYPE", "BEDS", "BATH", "ADDRESS"]
        ].dropna(subset=["LATITUDE", "LONGITUDE"])

        midpoint = (
            np.average(map_df["LATITUDE"]),
            np.average(map_df["LONGITUDE"]),
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[LONGITUDE, LATITUDE]",
            get_radius=30,
            get_fill_color="[200, 30, 0, 160]",
            pickable=True,
        )

        tooltip = {
            "html": (
                "<b>Price:</b> ${PRICE}<br/>"
                "<b>Type:</b> {TYPE}<br/>"
                "<b>Beds/Baths:</b> {BEDS} / {BATH}<br/>"
                "<b>Address:</b> {ADDRESS}"
            ),
            "style": {"backgroundColor": "steelblue", "color": "white"},
        }

        deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=midpoint[0],
                longitude=midpoint[1],
                zoom=10,
                pitch=40,
            ),
            layers=[layer],
            tooltip=tooltip,
        )

        st.pydeck_chart(deck)
    else:
        st.info("No locations to show on the map with the current filters.")


if __name__ == "__main__":
    main()
