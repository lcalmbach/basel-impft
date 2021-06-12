
from numpy import true_divide
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from st_aggrid import AgGrid


age_group_list=['Alle Altersgruppen','0-15','16-49','50-64','>74','unbekannt']
menu_options_list=['Übersicht','Zeitreihen Altersgruppen', "Impfrate"]

class App:
    def __init__(self, data, data_melted, bev, data_age):
        self.data_age = data_age
        self.data = data
        self.data_melted = data_melted
        self.bev_df = bev
        self.impf_typ = ''

    def status_summary(self):
        sort_gruppen = {'16-49':1, '50-64':2, '65-74':3, '> 74':4, 'Unbekannt':5, 'Impfberechtigte Bevölkerung': 6, 'Gesamtbevölkerung':7}
        max_datum = self.data_age['Impfdatum'].max()
        st.markdown(f"### Geimpfte nach Altersgruppen, Stand {max_datum.strftime('%d.%m.%Y')}")
        df = self.data_age[self.data_age['Impfdatum']==max_datum]
        summary_df = pd.DataFrame(data={},columns=['Altersgruppe', 'Erstimpfung', 'Erstimpfung kumuliert', 'Zweitimpfung','Zweitimpfung kumuliert','Bevölkerungszahl','Anteil der Geimpften', 'sort'])
        for alter in df['Altersgruppe'].unique():
            first = df[(df['Altersgruppe']==alter) & (df['Impftyp']==1)]['Anzahl'].iloc[0]
            first_kum= df[(df['Altersgruppe']==alter) & (df['Impftyp']==1)]['Anzahl Kumuliert'].iloc[0]
            second = df[(df['Altersgruppe']==alter) & (df['Impftyp']==2)]['Anzahl'].iloc[0]
            second_kum= df[(df['Altersgruppe']==alter) & (df['Impftyp']==2)]['Anzahl Kumuliert'].iloc[0]
            bev = df[(df['Altersgruppe']==alter) & (df['Impftyp']==2)]['Bevölkerungzahl der Altersgruppe'].iloc[0]
            anteil=df[(df['Altersgruppe']==alter) & (df['Impftyp']==2)]['Anteil der Geimpften'].iloc[0]
            anteil = "{:,.1f}".format(anteil)
            sort = sort_gruppen[alter]
            rec = {'Altersgruppe':alter,
                'Erstimpfung':first, 
                'Erstimpfung kumuliert':first_kum, 
                'Zweitimpfung':second, 
                'Zweitimpfung kumuliert':second_kum, 
                'Bevölkerungszahl':bev, 
                'Anteil der Geimpften':anteil, 
                'sort':sort, 
            }
            summary_df = summary_df.append(rec,ignore_index=True)
            
        summary_df=summary_df.sort_values(by=['sort'])
        summary_df = summary_df.drop('sort',axis=1)
        AgGrid(summary_df)

        erstimpf = int(df[(df['Altersgruppe']=='Gesamtbevölkerung') & (df['Impftyp']==1)]['Anzahl'].iloc[0])
        zweitimpf = int(df[(df['Altersgruppe']=='Gesamtbevölkerung') & (df['Impftyp']==2)]['Anzahl'].iloc[0])
        
        kum_erstimpf = int(df[(df['Altersgruppe']=='Gesamtbevölkerung') & (df['Impftyp']==-1)]['Anzahl Kumuliert'].iloc[0])
        kum_zweitimpf = int(df[(df['Altersgruppe']=='Gesamtbevölkerung') & (df['Impftyp']==2)]['Anzahl Kumuliert'].iloc[0])
        kum_pzt = df[(df['Altersgruppe']=='Gesamtbevölkerung') & (df['Impftyp']==1)]['Anteil der Geimpften'].iloc[0]
        kum_pzt = "{:,.1f}".format(kum_pzt)
        kum_impfwillige_pzt = df[(df['Altersgruppe']=='Impfberechtigte Bevölkerung') & (df['Impftyp']==1)]['Anteil der Geimpften'].iloc[0]
        kum_impfwillige_pzt = "{:,.1f}".format(kum_impfwillige_pzt)

        text = f"""Am {max_datum.strftime('%d.%m.%Y')} wurden Total {int(erstimpf + zweitimpf)} Dosen verimpft; Davon waren {erstimpf} 
        Erstimpfungen und {zweitimpf} Zweitimpfungen. Es wurden bis zu diesem Tag {kum_erstimpf + kum_zweitimpf} Personen mindestens einmal geimpft, davon haben {kum_zweitimpf} bereits ihre Zweitimpfung erhalten.
        Somit sind heute {kum_pzt}% der Gesamtbevölkerung und {kum_impfwillige_pzt}% der Impfberechtigten (Bevölkerung ab 16 Jahre) mindestens einmal geimpft. 
        """
        st.write(text)

    def get_fig(self):
        lst=['16-49','50-64','65-74','> 74','Unbekannt']
        df = self.data_age[(self.data_age['Altersgruppe'].isin(lst) & (self.data_age['Impftyp Beschreibung']==self.impf_typ))]
        chart = alt.Chart(df).mark_area().encode(
            x= alt.X('Impfdatum:T', title=''),
            y= alt.Y('Anzahl Kumuliert:Q',title=self.impf_typ + ' kumuliert'), 
            color = "Altersgruppe",
            tooltip=['Impfdatum','Impftyp Beschreibung','Altersgruppe','Anzahl', 'Anzahl Kumuliert']    
        ).properties(width=1000, height = 600)
        
        return chart

    def prepare_data(self):
        lst_altersklassen = ['Gesamtbevölkerung','16-49', '50-64', '65-74', '> 74', 'Unbekannt']
        self.altersklasse = st.sidebar.selectbox("Altersklasse", options=lst_altersklassen)
        df = self.data_age[(self.data_age['Altersgruppe']==self.altersklasse) & (self.data_age['Impftyp'].isin([1,2]))]
        df = df[['Impfdatum','Anzahl','Impftyp Beschreibung']]
        df['mitte_woche_datum'] = pd.to_datetime(df['Impfdatum']) - pd.to_timedelta(df['Impfdatum'].dt.dayofweek % 7 - 2, unit='D')
        df['von'] = df['mitte_woche_datum'] - pd.to_timedelta(3, unit='D')
        df['bis'] = df['mitte_woche_datum'] + pd.to_timedelta(3, unit='D')
        df['mitte_woche_datum'] = df['mitte_woche_datum'].dt.date 
        df = df.groupby(['mitte_woche_datum','von', 'bis','Impftyp Beschreibung'])['Anzahl'].sum()
        df = df.reset_index()
        return df

    
    def get_impfrate_fig(self, df):
        chart = alt.Chart(df).mark_bar(width = 20).encode(
            x= alt.X('mitte_woche_datum:T', title=''),
            y= alt.Y('Anzahl:Q', title='Wöchentliche Impfrate'), 
            color='Impftyp Beschreibung',
            tooltip=['von','bis','Impftyp Beschreibung', 'Anzahl']    
        ).properties(width=1000, height = 600)
        
        return chart

    def get_impfrate_text(self, df):
        _df = df.groupby(['von', 'bis'])['Anzahl'].sum().reset_index()
        min_datum = self.data_age['Impfdatum'].min()
        vacc_start = min_datum.strftime('%d.%m.%Y')
        avg_vac_rate_since_start = _df['Anzahl'].mean()
        max_weekly_vacc_rate = _df['Anzahl'].max()
        woche_max_rate_df = _df[_df['Anzahl']>=max_weekly_vacc_rate]
        max_weekly_vacc_start_date =  woche_max_rate_df['von'].iloc[0].strftime('%d.%m.%Y')
        max_weekly_vacc_end_date =  woche_max_rate_df['bis'].iloc[0].strftime('%d.%m.%Y')
        text = f"""Die mittlere wöchentliche Impfrate für die Altersklasse {self.altersklasse} im Kanton Basel-Stadt seit Impfbeginn am {vacc_start} beträgt {"{:,.0f}".format(avg_vac_rate_since_start)}. Die grösste wöchentliche Impfrate
            wurde in der Woche vom {max_weekly_vacc_start_date} bis {max_weekly_vacc_end_date} erreicht und betrug {"{:,.0f}".format(max_weekly_vacc_rate)} verimpfte Dosen 
            ({"{:,.0f}".format(max_weekly_vacc_rate / 7)} pro Tag). 
            """
        return text

    def show_menu(self): 
        menu_option=st.sidebar.selectbox("Darstellung",options=menu_options_list)
        if menu_option == 'Übersicht':
            self.status_summary()

        if menu_option == 'Zeitreihen Altersgruppen':
            self.impf_typ=st.sidebar.selectbox("Impftyp",options=self.data_age['Impftyp Beschreibung'].unique())
            fig = self.get_fig()
            st.altair_chart(fig)

        if menu_option == 'Impfrate':
            st.markdown("### Wöchentliche Impfrate nach Impftyp")
            df = self.prepare_data()            
            fig = self.get_impfrate_fig(df)
            st.altair_chart(fig)
            text = self.get_impfrate_text(df)
            st.markdown(text)
