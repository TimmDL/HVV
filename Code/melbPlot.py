import pandas as pd
import plotly.express as px
import streamlit as st

df = pd.read_csv('/Users/timmdill/Downloads/sst_alldata.csv')

df1 = df[['HstName', 'LmuId', 'CompType', 'state', 'Latitude', 'Longitude']]

#Farben für Plotly Map
color_scale = {'OPERATIONAL': 'blue', 'IN_OPERATION': 'blue', 'other': 'red'}

fig1 = px.scatter_mapbox(df1,
                         hover_name='HstName',
                         hover_data=['LmuId', 'CompType', 'state'],
                         lat="Latitude",
                         lon="Longitude",
                         color='state',
                         color_discrete_map=color_scale,
                         size_max=15, zoom=12,
                         mapbox_style="open-street-map",
                         title="HVV Stations")

# manuelles Überschreiben der anderen Stati, damit sie alle 'rot' sind
fig1.update_traces(marker=dict(color='red'), selector=dict(type='scatter_mapbox', customdata=df1[df1['state']=='other']))

#fig1.show()

st.plotly_chart(fig1, use_container_width=True)
