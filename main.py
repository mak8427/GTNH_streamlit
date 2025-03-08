
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

# Supabase Table
supabase_table = "gtnh-items"

sort_table = pd.read_csv(
  "/mnt/sdb/gtnh_ger/World/opencomputers/f93bf4e7-03b1-41e8-893e-d9033d3f97a9/home/GTNH_Lua_Applied/Export.csv",
  on_bad_lines='warn'  # Warns about bad lines but doesn't crash
)
sort_table['Date Time'] = pd.to_datetime(sort_table['Date Time'])
print(sort_table)
st.dataframe(sort_table)
# Select Box to filter a item
items_filter = st.selectbox("Select the Item", sort_table["Item"].unique().tolist() )



# Chart for Item
fig_col1, fig_col2 = st.columns([0.2, 0.8])
with fig_col1:
  st.markdown("### "+items_filter)

  st.markdown("#### Past 24-hour metrics")

  item_track = sort_table.loc[sort_table['Item'] == items_filter]
  item_track['Date Time"'] = pd.to_datetime(item_track["Date Time"])
  now = pd.Timestamp.now(tz="America/Sao_Paulo")
  now = now.tz_localize(None)
  last_24h = item_track[item_track["Date Time"] >= now - pd.Timedelta(days=1)]

  if len(last_24h) <= 1:
    kpi_avg = 0
    kpi_change = 0
  else:
    last_24h["real_production"] = last_24h["Quantity"].diff().fillna(0)
    total_production = last_24h["real_production"].sum()
    total_hours = (last_24h["Date Time"].max() - last_24h["Date Time"].min()).total_seconds() / 3600
    kpi_avg = (total_production / total_hours).round(0).astype(int)

    kpi_change = total_production.round(0).astype(int) 
  
  st.metric(label="Average Produced per Hour", value="{:,}".format(kpi_avg))
  st.metric(label="Total Amount Produced", value="{:,}".format(kpi_change))

with fig_col2:
  fig1 = px.line(item_track, x='Date Time', y='Quantity', title='Quantity of: ' + items_filter)
  st.write(fig1, key='fig1')


# Expander with all items
with st.expander("All items:"):
  for col in distinct_items:
    temp_df = sort_table.loc[sort_table['item'] == col]
    
    fig = px.line(temp_df, x='datetime', y='quantity', title='Quantity of: ' + col)
    
    st.write(fig)


