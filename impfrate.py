
from numpy import true_divide
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from st_aggrid import AgGrid


age_group_list=['Alle Altersgruppen','0-15','16-49','50-64','>74','unbekannt']
menu_options_list=['Übersicht','Zeitreihen Altersgruppen']

class App:
    def __init__(self, data, data_melted, bev, data_age):
        self.data_age = data_age
        self.data = data
        self.data_melted = data_melted
        self.bev_df = bev
        self.impf_typ = ''

    def prepare_data(self):
        lst_altersklassen = ['Gesamtbevölkerung','16-49', '50-64', '65-74', '> 74', 'Unbekannt']
        self.altersklasse = st.sidebar.selectbox("Altersklasse", options=lst_altersklassen)
        df = self.data_age[(self.data_age['Altersgruppe']==self.altersklasse) & (self.data_age['Impftyp'].isin([1,2]))]
        df = df[['Impfdatum','Anzahl','Impftyp Beschreibung']]
        df['mid_week_date'] = pd.to_datetime(df['Impfdatum']) - pd.to_timedelta(df['Impfdatum'].dt.dayofweek % 7 - 2, unit='D')
        df['mid_week_date'] = df['mid_week_date'].dt.date 

        df = df.groupby(['mid_week_date', 'Impftyp Beschreibung'])['Anzahl'].sum()
        df = df.reset_index()
        return df

    
    def get_fig(self, df):
        chart = alt.Chart(df).mark_bar(width = 20).encode(
            x= alt.X('mid_week_date:T'),
            y= alt.Y('Anzahl:Q'), 
            color='Impftyp Beschreibung',
            tooltip=['mid_week_date','Impftyp Beschreibung', 'Anzahl']    
        ).properties(width=1000, height = 600)
        
        return chart
        
    def show_menu(self): 
        df = self.prepare_data()
        fig = self.get_fig(df)
        st.markdown("### Wöchentliche Impfrate nach Impftyp")
        st.altair_chart(fig)

