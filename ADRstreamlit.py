#%%
import streamlit as st
import pandas as pd
import numpy as np
import datetime

filename = 'ADRoutput.csv'
df = pd.read_csv(filename,index_col=0)
df.reset_index(drop=True,inplace=True)
df['timestamp'] = pd.to_datetime(df['timestamp'])

lats = df['lat'].unique()
lons = df['lon'].unique()

#%%

#"""Blablabla hier kun je markdown tekst wegzetten"""
#
#st.title("Supercoole vrachtwagen visualisatie!")
#st.markdown(
#"""
#Blablabla hier kun je markdown tekst wegzetten
#""")

# Mode either realtime or aggregated
mode = st.sidebar.radio('Kies realtime of aggregated',('realtime','aggregated'))
mode = 'aggregated'

# Select Gevi code, filter is later
options = st.sidebar.multiselect(
    'Selecteer Gevi code',
    df['gevi'].unique())

############# Aggregated
if mode =='aggregated':

    # Get first and last timestamp, in order to get first and last dates and times
    mn, mx = min(df['timestamp']),max(df['timestamp'])
    
    startdatum = st.sidebar.date_input('Startdatum', datetime.date(2019, mn.month, mn.day))
    enddatum = st.sidebar.date_input('Einddatum', datetime.date(2019, mx.month, mx.day))
    
    starttime = st.sidebar.time_input('Selecteer begintijd', datetime.time(mn.hour, mn.minute))
    endtime = st.sidebar.time_input('Selecteer eindtijd', datetime.time(mx.hour, mx.minute))
    
    start = str(startdatum)+' '+str(starttime)
    end = str(enddatum)+' '+str(endtime)
    
    if start>end:
        st.error('Error: End date must fall after start date.')
    if start==end:
        end = str(enddatum)+' '+str(datetime.time(mx.hour, mx.minute+1))
    
    data = df[(df['timestamp']>=start)&(df['timestamp']<=end)]
    
############# Realtime
if mode == 'realtime':
    timecutoff = max(df['timestamp']) - datetime.timedelta(minutes=15)
    data = df[df['timestamp']>=timecutoff]

############# Filter op codes. Geen selectie is alles    
if len(options)>0:
    data = data[data['gevi'].isin(options)]

#%%    
############# Plotting - map
midpoint = (np.average(df["lat"]), np.average(df["lon"]))
st.deck_gl_chart(
    viewport={
#        "mapStyle": "mapbox://styles/mapbox/light-v9",
#        "mapboxApiAccessToken": '<pk.eyJ1IjoibGFyc2tpbGxhYXJzIiwiYSI6ImNrMWc2aHVmeDAwN2ozb3Fva2prM3cybjQifQ.G0kykI805dHb9fBDxkPy2Q>',
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 6.2,
        "pitch": 0,
    },
    layers=[
        {
            "type": "HexagonLayer",
            "data": data,
            "radius": 2500,
            "elevationScale": 4,
            "elevationRange": [0, 1000],
            "pickable": True,
            "extruded": True,
        }
    ],
)

#%%
#############%% Plotting - linechart
## Kies uit uren of dagen
#groupmode = st.sidebar.radio('Kies uren of dagen',('Uren','Dagen'))
#
#if groupmode=='Uren':
#    timeseries_to_plot.loc[:,'timestamp'] = timeseries_to_plot['timestamp'].apply(lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour))
#    
#if groupmode=='Dagen':
#    timeseries_to_plot.loc[:,'timestamp'] = timeseries_to_plot['timestamp'].apply(lambda dt: datetime.datetime(dt.year, dt.month, dt.day))

# Maak 1-hot zodat elke code een bar krijgt
timeseries_to_plot = data[['gevi','road']]
timeseries_to_plot = pd.get_dummies(timeseries_to_plot['gevi'])
timeseries_to_plot['road'] = data['road']

# Grouperen op timestamp 
timeseries_to_plot = timeseries_to_plot.groupby(timeseries_to_plot['road']).sum()
timeseries_to_plot.index.names = ['index']
#timeseries_to_plot['gevi'] = np.arange(len(timeseries_to_plot))
st.bar_chart(timeseries_to_plot)

#%%% Show data
if st.checkbox("Show raw data", False):
#    st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    st.write(timeseries_to_plot)