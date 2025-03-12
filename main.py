
import os
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from st_supabase_connection import SupabaseConnection, execute_query
import plotly.express as px
import pandas as pd
import datetime
import time
import pytz


st.set_page_config(
  page_title = 'GTNH - Items Tracker',
  layout='wide'
)

st.title("GTNH - Applied Energistics Items Track")

# Refresh the page every 5 minutes (300,000 milliseconds)
st_autorefresh(interval=300000, key="refresh_page")


sort_table = pd.read_csv(
  "/mnt/sdb/gtnh_ger/World/opencomputers/f93bf4e7-03b1-41e8-893e-d9033d3f97a9/home/GTNH_Lua_Applied/Export.csv",
  on_bad_lines='warn'  # Warns about bad lines but doesn't crash
)
sort_table['Date Time'] = pd.to_datetime(sort_table['Date Time'])
last_date = sort_table["Date Time"][len(sort_table)-1]


st.markdown("#### Last Update: " + str(last_date))




f = open("Aggregator2.txt", "r")
old_date = f.read()
datetime_object = datetime.datetime.strptime(old_date, '%Y-%m-%d %H:%M:%S')

if(last_date - datetime_object >  pd.Timedelta(days=1) ):
    st.markdown("#### " + "Trigger")
    f = open("Aggregator2.txt", "w")
    f.write(f"{sort_table["Date Time"][len(sort_table)-1]}")
    f.close()


sort_table.sort_values('Quantity', inplace=True, ascending=False)
# Select Box to filter a item
items_filter = st.selectbox("Select the Item", sort_table["Item"].unique().tolist() )




# Chart for Item
fig_col1, fig_col2 = st.columns([0.2, 0.8])
with fig_col1:
  st.markdown("### " + items_filter)
  st.markdown("#### Past 24-hour metrics")

  # Filter for the selected item
  item_track = sort_table.loc[sort_table['Item'] == items_filter]

  # Convert to datetime (and sort by date)
  item_track['Date Time'] = pd.to_datetime(item_track["Date Time"]).dt.tz_localize("Europe/Rome")
  item_track = item_track.sort_values(by='Date Time')

  # Use a timezone-aware now
  now = pd.Timestamp.now(tz="Europe/Rome")
  last_24h = item_track[item_track["Date Time"] >= now - pd.Timedelta(days=1)]

  if len(last_24h) <= 1:
    kpi_avg = 0
    kpi_change = 0
  else:
    # Calculate the difference in Quantity in chronological order
    last_24h["real_production"] = last_24h["Quantity"].diff().fillna(0)
    total_production = last_24h["real_production"].sum()
    total_hours = (last_24h["Date Time"].max() - last_24h["Date Time"].min()).total_seconds() / 3600
    kpi_avg = (total_production / total_hours).round(0).astype(int)
    kpi_change = total_production.round(0).astype(int)

  st.metric(label="Average Produced per Hour", value="{:,}".format(kpi_avg))
  st.metric(label="Total Amount Produced", value="{:,}".format(kpi_change))

with fig_col2:
  # Plot the quantity over time
  fig1 = px.line(item_track, x='Date Time', y='Quantity', title='Quantity of: ' + items_filter)
  st.write(fig1, key='fig1')






