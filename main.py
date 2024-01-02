import altair as alt
import streamlit as st

from src.db.create import get_database_engine
from src.db.queries import get_watchhistory_count_per_channel, get_watchhistory_count_per_dayhour, get_watchhistory_count_per_month, get_watchhistory_count_per_weekday, get_watchhistory_for_month, get_watchhistory_timestamp_range
from src.ytapi.functions import ytapi_get_videos

st.write("""
# YouTube History Analyzer
         
Analysis of YouTube watch history
""")

# set up database
db_engine = get_database_engine()

df = get_watchhistory_count_per_month(db_engine)
st.subheader("Watches by month")
# st.line_chart(df.set_index('year_month'))
st.altair_chart(alt.Chart(df).mark_line().encode(
    x=alt.X('year_month', sort="ascending", title="Month"),
    y=alt.Y('watch_count', title="Watch Count")
), use_container_width=True)

df = get_watchhistory_count_per_weekday(db_engine)
st.subheader("Watches by day of week")
st.altair_chart(alt.Chart(df).mark_bar().encode(
    x=alt.X('weekday', sort=None, title="Day of week"),
    y=alt.Y('watch_count', title="Watch Count"),
), use_container_width=True)

df = get_watchhistory_count_per_dayhour(db_engine)
st.subheader("Watches by time of day")
st.altair_chart(alt.Chart(df).mark_bar().encode(
    x=alt.X('hour', sort=None, title="Hour of day"),
    y=alt.Y('watch_count', title="Watch Count"),
), use_container_width=True)

df = get_watchhistory_count_per_channel(db_engine)
st.subheader("Watches by channel")
st.altair_chart(alt.Chart(df).mark_bar().encode(
    x=alt.X('channel_name', sort=None, title="Channel Name"),
    y=alt.Y('watch_count', title="Watch Count"),
), use_container_width=True)
