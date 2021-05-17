
from altair.vegalite.v4.schema.channels import StrokeDash
import pandas as pd
from pandas.core.arrays import integer
import streamlit as st
import altair as alt
import datetime as dt
import locale

class App:
    def __init__(self, data, data_melted):
        self.data = data
        self.data_melted = data_melted
        
        self.first_date = self.data['datum'].min()
        self.last_date = self.data['datum'].max()
        self.status_dosis1 = int(self.data[self.data['datum'] == self.last_date]['dosis1'])
        self.status_dosis2 = int(self.data[self.data['datum'] == self.last_date]['dosis2'])
        self.status_total = int(self.data[self.data['datum'] == self.last_date]['total'])
        self.aggregation_period = 7
        self.impfwillige = 80
        self.pop_dic = self.get_pop_data()
        self.impfbereite_szenario = ''
        self.impfbereite_eff = 0
        locale.setlocale(locale.LC_ALL, 'de-ch')
        

    def get_text(self, key:str, sum_d1, sum_d2, sum_tot, d1_100pz, d2_100pz):
        text = {}
        pop80pct = "{:,d}".format(int(self.pop_dic['100% Bevölkerung'] * 0.8))

        text_threshold = f"""Die Hürde von 80% der Bevölkerung liegt bei {pop80pct} """

        if self.impfbereite_eff > self.pop_dic['100% Bevölkerung'] * 0.8:
            text_threshold += f""" und sie wird somit nach Impfen aller Impfbereiten um {"{:,d}".format(int(self.impfbereite_eff - self.pop_dic['100% Bevölkerung'] * 0.8))} überschritten. Es bestehen gute 
            Chancen, dass die Herdenimmunität erreicht wird.
            """
        else:
            text_threshold += f""" und sie wird somit nach Impfen aller Impfbereiten um {"{:,d}".format(int(self.impfbereite_eff - self.pop_dic['100% Bevölkerung'] * 0.8))} unterschritten. Zum Erreichen einer 
            Herdenimmunität müssen weitere Altersklassen für die Impfung zugelassen werden, und/oder der Anteil der Impfberechtigten muss erhöht werden. Sie können den benötigten Anteil der
            Impfwilligen Personen eruieren, indem sie den Anteil im Navigationsbereich am linken Rand erhöhen. 
            """

        text['verlauf'] = f"""Es wurden bis heute {self.status_total} Dosen verabreicht, {"{:,d}".format(self.status_dosis1)} Personen wurden einmal geimpft, {"{:,d}".format(self.status_dosis2)} 
        Personen haben bereits eine zweite Impfung erhalten. Die Rate der über die letzten {self.aggregation_period} Tage täglich geimpften Personen beträgt {"{:,d}".format(int(sum_tot / self.aggregation_period))}.
        Davon sind {"{:,d}".format(int(sum_d1 / self.aggregation_period))} pro Tag Erstimpfungen und {"{:,d}".format(int(sum_d2/self.aggregation_period))} pro Tag Zweitimpfungen. Die 80% Linie zeigt die Hürde, bei welcher gemäss [BAG](https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/konzeptpapier_3-phasen-modell.pdf.download.pdf/Konzeptpapier_Drei-Phasen-Modell_DE.pdf) 
        eine Herdenimmunität der Bevölkerung erreicht werden sollte. Die Linie `{self.impfbereite_szenario}` zeigt die, für das Szenario gewählte Altersklasse (Impfberechtigte). Die Linie `Impfwillige` zeigt den, für das Szenario angenommenen Anteil 
        der Personen, die sich impfen lassen wollen ({self.impfwillige}%).
        """

        text['prognose'] = f"""Wenn man die mittlere Impfrate der vergangenen {self.aggregation_period} Tage für Erstimpfungen extrapoliert, so werden am {d1_100pz.strftime('%d.%m.%y')} alle impfwilligen Personen einmal geimpft sein. Nach diesem Zeitpunkt finden 
        nur noch Zweitimpfungen statt, d.h. die Rate für Zweitimpfungen steigt an. Am {d2_100pz.strftime('%d.%m.%y')} sind alle impfwilligen Personen zum zweiten Mal geimpft. Dabei wird noch nicht berücksichtigt, dass
        Personen, die bereits an Covid-19 erkrankt waren, nur einmal geimpft werden. 

Um eine Herdenimmunität in der Bevölkerung zu erreichen, sollten mindestens 80% der Bevölkerung ({pop80pct}) geimpft sein. Das gewählte Szenario sieht vor, dass
        nur die Altersklassen `{self.impfbereite_szenario}` geimpft werden und von dieser Bevölkerungsschicht lassen sich {self.impfwillige}% impfen. Es können somit maximal {"{:,d}".format(self.impfbereite_eff)} Personen geimpft werden.
        {text_threshold}   
        """
        return text[key]

    def get_threshold_lines(self, min_date, max_date, szenario_name, szenario_value):
        data = {'datum': [min_date, max_date, min_date, max_date,min_date, max_date],
            'parameter':[szenario_name,szenario_name,'100% Bevölkerung','100% Bevölkerung', '80% Bevölkerung', '80% Bevölkerung'],
            'anzahl': [szenario_value, szenario_value, self.pop_dic['100% Bevölkerung'], self.pop_dic['100% Bevölkerung'], self.pop_dic['100% Bevölkerung'] * 0.8, self.pop_dic['100% Bevölkerung']*0.8],
            }
        pop_lines_df = pd.DataFrame(data)
        pop_lines_df['datum'] = pd.to_datetime(pop_lines_df['datum'] )
        return pop_lines_df

    def get_pop_data(self):
        pop_dic = dict({'>9-Jährige':177279,'>19-Jährige':161875,'100% Bevölkerung':195844,'80% Bevölkerung':195844 * 0.8},)
        
        return pop_dic

    def time_series_plot(self, df: pd.DataFrame, df_prognose, df_thresholds):
        df = self.data_melted.replace('dosis1', '1x geimpft')
        df = df.replace('dosis2', '2x geimpft')
        df = df.rename(columns={'parameter': 'Verlauf'})
        chart = alt.Chart(df).mark_line().encode(
            x= alt.X('datum:T'),
            y= alt.Y('anzahl:Q', scale=alt.Scale(domain=(0,200000))), 
            color = "Verlauf",
            tooltip=['datum','Verlauf','anzahl']    
        )
        
        df = df_thresholds.rename(columns={'parameter':'Bevölkerung'})
        df = df.replace(self.impfbereite_szenario, f"{self.impfwillige}%  der {self.impfbereite_szenario}")
        thresholds = alt.Chart(df).mark_line().encode(
            x='datum', 
            y='anzahl', 
            color = "Bevölkerung",
            tooltip=['datum','Bevölkerung','anzahl']    
        )

        df = df_prognose.replace('dosis1', '1x geimpft')
        df = df.replace('dosis2', '2x geimpft')
        df = df.rename(columns={'parameter': 'Prognose'})
        prog = alt.Chart(df).mark_circle(point=True,).encode(
            x='datum', 
            y='anzahl', 
            color = "Prognose",
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
        # vaccinate peoople at current frequency until all got vaccinated for the first time
        while d1 <= limit:
            d1 += rate_d1
            d2 += rate_d2
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
        
        self.impfbereite_szenario = st.sidebar.selectbox('Impfberechtigte', ['>9-Jährige', '>19-Jährige', '100% Bevölkerung'])
        self.impfwillige = st.sidebar.slider('Impfwillige', 0,100, self.impfwillige)
        self.impfbereite_eff = int(self.pop_dic[self.impfbereite_szenario] * self.impfwillige / 100)
        df_prognose,d1_100pz, d2_100pz = self.calc_model(sum_d1, sum_d2, sum_tot, self.impfbereite_eff)
        df_thresholds = self.get_threshold_lines(self.first_date, d2_100pz, self.impfbereite_szenario, self.impfbereite_eff)
        chart = self.time_series_plot(self.data_melted, df_prognose, df_thresholds)
        
        st.markdown("## Verlauf und Prognose der Impfungen in Basel-Stadt")
        st.markdown("### Verlauf")
        st.markdown(self.get_text('verlauf', sum_d1, sum_d2, sum_tot, d1_100pz, d2_100pz))
        st.altair_chart(chart, use_container_width=True)
        st.markdown("### Prognose")
        st.markdown(self.get_text('prognose', sum_d1, sum_d2, sum_tot, d1_100pz, d2_100pz))
        
    


    

