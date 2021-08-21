
from altair.vegalite.v4.schema.channels import StrokeDash
import pandas as pd
from pandas.core.arrays import integer
import streamlit as st
import altair as alt
import datetime as dt
import locale

class App:
    def __init__(self, data, data_melted, bev, data_age):
        self.data_age = data_age
        self.data = data
        self.data_melted = data_melted
        self.bev_df = bev
        self.bev_total = bev[bev['alter']==0]['anzahl'][0]
        
        self.first_date = self.data['datum'].min()
        self.last_date = self.data['datum'].max()
        self.status_dosis1 = int(self.data[self.data['datum'] == self.last_date]['dosis1'])
        self.status_dosis2 = int(self.data[self.data['datum'] == self.last_date]['dosis2'])
        self.status_total = int(self.data[self.data['datum'] == self.last_date]['total'])
        self.aggregation_period = 7
        self.impfwillige = 80
        self.herd_immunity_threshold = 80
        self.zugelassene_alter= 16
        self.zugelassene_num = self.age2number(self.zugelassene_alter)
        self.population = self.age2number(0)
        self.impfbereite_eff = 0
        locale.setlocale(locale.LC_ALL, '')
        
    def age2number(self, age):
        return  int(self.bev_df[self.bev_df['alter']==age]['anzahl'])

    def get_text(self, key:str, sum_d1, sum_d2, sum_tot, d1_100pz, d2_100pz):
        text = {}
        threshold_herdimm_pct = "{:,d}".format(int(self.population * self.herd_immunity_threshold/100))

        text_threshold = f"""Die Hürde von {self.herd_immunity_threshold}% der Bevölkerung liegt bei {threshold_herdimm_pct} """

        if self.impfbereite_eff > self.population * self.herd_immunity_threshold/100:
            text_threshold += f""" und sie wird somit nach Impfen aller Impfbereiten um {"{:,d}".format(int(self.impfbereite_eff - self.population * self.herd_immunity_threshold/100))} überschritten. Es bestehen gute 
            Chancen, dass die Herdenimmunität im Kanton erreicht wird.
            """
        else:
            text_threshold += f""" und sie wird somit nach Impfen aller impfbereiten Personen um {"{:,d}".format(int(self.impfbereite_eff - self.population * self.herd_immunity_threshold/100))} immer noch unterschritten. Zum Erreichen der 
            Herdenimmunität im Kanton müssen weitere Altersklassen für die Impfung zugelassen werden, und/oder der Anteil der Impfwilligen muss erhöht werden. Sie können den benötigten Anteil der
            impfwilligen Personen eruieren, indem sie deren Anteil im Navigationsbereich am linken Rand erhöhen, bis dass die Linie der Impfwilligen die Herdenimmunitäts-Linie überdeckt. 
            """

        text['verlauf'] = f"""Es wurden bis heute {"{:,d}".format(self.status_total)} Dosen verabreicht, {"{:,d}".format(self.status_dosis1)} Personen wurden einmal geimpft, {"{:,d}".format(self.status_dosis2)} 
        Personen haben bereits eine zweite Impfung erhalten. {self.status_dosis2 / self.bev_total :.1%} der Basler Bevölkerung sind somit vollständig geimpft. Die Rate der über die letzten {self.aggregation_period} Tage geimpften Personen beträgt {"{:,d}".format(int(sum_tot / self.aggregation_period))} pro Tag.
        Davon sind {"{:,d}".format(int(sum_d1 / self.aggregation_period))} pro Tag Erstimpfungen und {"{:,d}".format(int(sum_d2/self.aggregation_period))} pro Tag Zweitimpfungen.
        
Die Linie `{self.herd_immunity_threshold}% Bevölkerung` zeigt die Hürde, bei welcher die Herdenimmunität erreicht ist. 
        Gemäss [BAG](https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/konzeptpapier_3-phasen-modell.pdf.download.pdf/Konzeptpapier_Drei-Phasen-Modell_DE.pdf) liegt dieser Wert bei 80% doch kann er im 
        Navigationsfeld angepasst werden. Die Linie `>{self.zugelassene_alter}-Jährige` zeigt die, für das Szenario gewählte Altersklasse (Impfberechtigte = {"{:,d}".format(self.zugelassene_num)}). Die Linie `Impfwillige` zeigt den, für das Szenario angenommenen Anteil 
        der Personen, die sich impfen lassen wollen ({self.impfwillige}%).
        """

        text['prognose'] = f"""Wenn man die mittlere Impfrate der vergangenen {self.aggregation_period} Tage für Erstimpfungen extrapoliert, so werden am {d1_100pz.strftime('%d.%m.%y')} alle impfwilligen Personen einmal geimpft sein. Nach diesem Zeitpunkt finden 
        nur noch Zweitimpfungen statt, und die Rate für Zweitimpfungen steigt entsprechend an. Am {d2_100pz.strftime('%d.%m.%y')} sind auch alle impfwilligen Personen zum zweiten Mal geimpft. Dabei wird noch nicht berücksichtigt, dass
        Personen, die bereits an Covid-19 erkrankt waren, nur einmal geimpft werden. 

Um die Herdenimmunität in einer Population zu erreichen, muss ein definierter Prozentsatz der Bevölkerung ({self.herd_immunity_threshold}%) immun sein. Dies bedeutet für den Kanton Basel-Stadt, dasss {"{:,d}".format(int(self.population * self.herd_immunity_threshold/100))} Personen geimpft sein müssen. 
        Das gewählte Szenario sieht vor, dass die Altersklassen `>{self.zugelassene_alter}-Jährige` geimpft werden und von dieser Bevölkerungsschicht lassen sich {self.impfwillige}% impfen. Es können somit maximal {"{:,d}".format(int(self.impfbereite_eff))} Personen geimpft werden.
        {text_threshold}   
        """
        return text[key]

    def get_threshold_lines(self, min_date, max_date, szenario_name, szenario_value):
        data = {'datum': [min_date, max_date, min_date, max_date, min_date, max_date],
            'parameter':['100% Bevölkerung','100% Bevölkerung',szenario_name,szenario_name,f'{self.herd_immunity_threshold}% der Bevölkerung', f'{self.herd_immunity_threshold}% der Bevölkerung'],
            'anzahl': [self.population, self.population, szenario_value, szenario_value, self.population * self.herd_immunity_threshold/100, self.population*self.herd_immunity_threshold/100],
        }                    
        pop_lines_df = pd.DataFrame(data)
        pop_lines_df['datum'] = pd.to_datetime(pop_lines_df['datum'])
        return pop_lines_df


    def time_series_plot(self, df: pd.DataFrame, df_prognose, df_thresholds):
        df = self.data_melted.replace('dosis1', '1x geimpft')
        df = df.replace('dosis2', '2x geimpft')
        df = df.replace('total', 'Total verimpfte Dosen')
        df = df.rename(columns={'parameter': 'Verlauf'})
        chart = alt.Chart(df).mark_line().encode(
            x= alt.X('datum:T'),
            y= alt.Y('anzahl:Q', scale=alt.Scale(domain=(0,300000))), 
            color = "Verlauf",
            tooltip=['datum','Verlauf','anzahl']    
        )
        
        df = df_thresholds.rename(columns={'parameter':'Bevölkerung'})
        #df = df.replace(self.impfbereite_szenario, f"{self.impfwillige}%  der {self.impfbereite_szenario}")
        thresholds = alt.Chart(df).mark_line(size=2).encode(
            x='datum', 
            y='anzahl', 
            color=alt.Color('Bevölkerung', scale=alt.Scale(scheme='bluepurple')),
            tooltip=['datum','Bevölkerung','anzahl']    
        )

        df = df_prognose.replace('dosis1', '1x geimpft')
        df = df.replace('dosis2', '2x geimpft')
        df = df.rename(columns={'parameter': 'Prognose'})
        prog = alt.Chart(df).mark_circle(point=True,size=5).encode(
            x='datum', 
            y='anzahl', 
            color='Prognose'
        )

        return (chart + prog + thresholds).resolve_scale(
            color='independent'
        ).configure_point(
            size=1
        )

    def get_value(self, datum, key):
        return int(self.data[self.data['datum'] == datum][key])

    def get_summe_7d(self):
        max_date = self.data['datum'].max()
        week_ago = max_date - dt.timedelta(days=self.aggregation_period)
        sum_7d_d1 = self.get_value(max_date,'dosis1') - self.get_value(week_ago,'dosis1')
        sum_7d_d2 = self.get_value(max_date,'dosis2') - self.get_value(week_ago,'dosis2')
        sum_7d_tot = self.get_value(max_date,'total') - self.get_value(week_ago,'total')

        return sum_7d_d1,sum_7d_d2,sum_7d_tot
        
    def calc_model(self, sum_d1, sum_d2, sum_tot, limit):
        df = pd.DataFrame({
            'datum': pd.Series([], dtype='datetime64[ns]'),
            'parameter': pd.Series([], dtype='str'),
            'anzahl': pd.Series([], dtype='float')
        })
        rate_d1 = sum_d1 / self.aggregation_period
        rate_d2 = sum_d2 / self.aggregation_period
        rate_tot = sum_tot / self.aggregation_period

        d1 = self.get_value(self.last_date,'dosis1')
        d2 = self.get_value(self.last_date,'dosis2')
        tot = self.get_value(self.last_date,'total')

        sim_date = self.last_date 
        # vaccinate peoople at current frequency until all are vaccinated for the first time
        while d1 <= limit:
            if d2 + rate_d2 < limit and d1 + rate_d1 > d2 + rate_d2:
                d1 += rate_d1
                d2 += rate_d2
            else:
                d1 += rate_tot
            tot += rate_tot
            sim_date += dt.timedelta(1)
            df = df.append({'datum':sim_date,'parameter': 'dosis1', 'anzahl': d1}, ignore_index=True)
            df = df.append({'datum':sim_date,'parameter': 'dosis2', 'anzahl': d2}, ignore_index=True)

        d1_100pz = sim_date
        while d2 <= limit:
            d2 += rate_tot
            tot += rate_tot
            sim_date += dt.timedelta(1)
            df = df.append({'datum':sim_date,'parameter': 'dosis1', 'anzahl': d1}, ignore_index=True)
            df = df.append({'datum':sim_date,'parameter': 'dosis2', 'anzahl': d2}, ignore_index=True)
        d2_100pz = sim_date
        return df, d1_100pz, d2_100pz


    def show_menu(self): 
        # gr10	177279
        # gr20	161875

        sum_d1, sum_d2, sum_tot = self.get_summe_7d()
        
        self.zugelassene_alter= st.sidebar.slider('Zugelassen für Impfung ab Alter', 0,90, self.zugelassene_alter)
        self.impfwillige = st.sidebar.slider('Impfwillige', 0, 100, self.impfwillige)
        self.zugelassene_num = self.age2number(self.zugelassene_alter)
        self.impfbereite_eff = self.zugelassene_num * self.impfwillige / 100
        df_prognose,d1_100pz, d2_100pz = self.calc_model(sum_d1, sum_d2, sum_tot, self.impfbereite_eff)
        self.herd_immunity_threshold = st.sidebar.slider('Hürde Herdenimmunität (% Bevölkerung)', 50, 100, self.herd_immunity_threshold)
        df_thresholds = self.get_threshold_lines(self.first_date, d2_100pz, f">{self.zugelassene_alter}-Jährige", self.impfbereite_eff)
        chart = self.time_series_plot(self.data_melted, df_prognose, df_thresholds)
        
        st.markdown("## Verlauf und Prognose der Impfungen im Kanton Basel-Stadt")
        st.markdown("### Verlauf")
        st.markdown(self.get_text('verlauf', sum_d1, sum_d2, sum_tot, d1_100pz, d2_100pz))
        st.altair_chart(chart, use_container_width=True)
        st.markdown("### Prognose")
        st.markdown(self.get_text('prognose', sum_d1, sum_d2, sum_tot, d1_100pz, d2_100pz))
        
    


    

