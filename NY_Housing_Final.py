"""
Name:       Your Name
CS230:      Section XXX
Data:       New York Housing Market
URL:        (add Streamlit Cloud URL here if you deploy it)

Description:
Simple Streamlit app to explore New York housing data.
You can choose a borough and a maximum sale price.
The app shows filtered rows, a bar chart of average price by borough,
and a map of property locations.

References:
- Streamlit docs: https://docs.streamlit.io/
- PyDeck docs: https://deckgl.readthedocs.io/
- Matplotlib docs: https://matplotlib.org/
# Some layout and comments were helped by ChatGPT, but I understand the code.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# ----------------- LOAD DATA -----------------

# Change this to your real file name
DATA_FILE = "NY-House-Dataset.csv"

def load_data(filename="NY-House-Dataset.csv"):  # #[FUNC2P] function with default parameter
    """Load the New York housing CSV file."""
    df = pd.read_csv(filename)

    # You MUST make sure these column names match your CSV.
    # If your columns are different, rename them here.
    # Example names we expect:
    #   "borough", "neighborhood", "sale_price", "latitude", "longitude"
    # If necessary:
    # df = df.rename(columns={
    #     "BOROUGH": "borough",
    #     "NEIGHBORHOOD": "neighborhood",
    #     "SALE PRICE": "sale_price",
    #     "LAT": "latitude",
    #     "LON": "longitude"
    # })

    # Convert sale_price to number (in case it's stored as text)
    df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")

    # Remove missing or weird values
    df = df.dropna(subset=["sale_price"])
    df = df[df["sale_price"] > 10000]  # ignore crazy tiny prices

    return df

df = load_data(DATA_FILE)

# ----------------- SIDEBAR (USER INPUT) -----------------

st.title("New York Housing Market Explorer")

st.sidebar.header("Filters")

# Borough dropdown
borough_list = sorted(df["borough"].unique().tolist())  # #[LISTCOMP] could also be used, but kept simple
borough_list = ["All"] + borough_list
selected_borough = st.sidebar.selectbox(
    "Select Borough", borough_list
)  # #[ST1] dropdown

# Max price slider
max_price = float(df["sale_price"].max())
selected_max_price = st.sidebar.slider(
    "Maximum Sale Price",
    min_value=50000.0,
    max_value=max_price,
    value=min(1000000.0, max_price),
    step=50000.0,
)  # #[ST2] slider

st.sidebar.markdown("---")
st.sidebar.write("Use the filters to change the table, chart, and map.")  # #[ST3] using sidebar for layout/text


# ----------------- FILTER DATA -----------------

def filter_data(data, borough, max_price_limit):  # #[FUNCRETURN2] (we will return 2 things)
    """Filter by borough (if not All) and by max price."""
    df_filtered = data.copy()

    # #[FILTER1] example: filter by 1 condition
    if borough != "All":
        df_filtered = df_filtered[df_filtered["borough"] == borough]

    # filter by max price
    df_filtered = df_filtered[df_filtered["sale_price"] <= max_price_limit]

    # summary: average price
    avg_price = df_filtered["sale_price"].mean()

    return df_filtered, avg_price  # returning 2 values


filtered_df, avg_price = filter_data(df, selected_borough, selected_max_price)  # #[FUNCCALL2]


# ----------------- SHOW FILTERED TABLE + SUMMARY -----------------

st.subheader("Filtered Data")

st.write(f"Number of rows: {len(filtered_df)}")
st.write(f"Average price (filtered): ${avg_price:,.0f}")

# #[SORT] sort by price
filtered_sorted = filtered_df.sort_values("sale_price", ascending=False)

# #[MAXMIN] find biggest + smallest sale price in filtered data
max_filtered_price = filtered_sorted["sale_price"].max()
min_filtered_price = filtered_sorted["sale_price"].min()
st.write(f"Highest price (filtered): ${max_filtered_price:,.0f}")
st.write(f"Lowest price (filtered): ${min_filtered_price:,.0f}")

# Show first 20 rows only so Streamlit isn’t too slow
st.dataframe(filtered_sorted.head(20))


# ----------------- CHART 1: AVERAGE PRICE BY BOROUGH -----------------

st.subheader("Average Sale Price by Borough")

# group by borough
borough_avg = df.groupby("borough")["sale_price"].mean().reset_index()

# simple bar chart with matplotlib
fig, ax = plt.subplots()
ax.bar(borough_avg["borough"], borough_avg["sale_price"], color="orange")
ax.set_xlabel("Borough")
ax.set_ylabel("Average Sale Price ($)")
ax.set_title("Average Sale Price by Borough")

plt.xticks(rotation=45)
plt.tight_layout()

# #[CHART1] bar chart with labels and color
st.pyplot(fig)


# ----------------- MAP: PROPERTY LOCATIONS -----------------

st.subheader("Map of Property Sales")

# Need latitude/longitude columns
if "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
    # Drop rows without coordinates
    map_df = filtered_df.dropna(subset=["latitude", "longitude"])

    if len(map_df) == 0:
        st.write("No points to show on map for current filters.")
    else:
        # Create pydeck layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[longitude, latitude]",
            get_radius=100,
            get_color=[200, 0, 0],
            pickable=True,
        )

        # View somewhere around NYC
        view_state = pdk.ViewState(
            longitude=-74.0,
            latitude=40.7,
            zoom=9,
            pitch=0,
        )

        tooltip = {
            "html": "<b>Price:</b> ${sale_price}<br/><b>Borough:</b> {borough}<br/><b>Neighborhood:</b> {neighborhood}"
        }

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
        )

        # #[MAP] custom pydeck map
        st.pydeck_chart(deck)
else:
    st.write("Your data file does not have 'latitude' and 'longitude' columns, so the map cannot be shown.")
