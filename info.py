
import pandas as pd
import streamlit as st


class App:
    def __init__(self, data, data_melted):
        self.data = data
        self.data_melted = data_melted
        self.text = """
        Diese Applikation stellt die neuesten Impfzahlen der Stadt Basel in einer Zeitreihe dar und erlaubt einfache Prognosen für den Zeitpunkt, an dem 
        ein bestimmter Anteil der Basler Bevölkerung geimpft sein wird. Die Zahl der zu impfenden Personen hängt weitgehend von zwei Faktoren ab:
- Wieviele Personen, respektive welche Altersklassen (oder Kinder ab welchem Alter), werden für die Impfung zugelassen?
- Wieviele der, für die Impfung zugelassenen Personen, entscheiden sich für die Impfung?

Die Impfung erhöht primär den Schutz der geimpften Personen. Wird ein genügend hoher Anteil der Bevölkerung immunisert, so entsteht eine [Herdenimmunität](https://de.wikipedia.org/wiki/Herdenimmunit%C3%A4t), d.h. die Übertragungsmöglichkeiten 
des Virus sind so gering, dass auch die wenigen, noch nicht geimpften Personen, geschützt sind. Die Grenze wird in der Regel bei 80% der Bevölkerung positioniert, doch kann sie in der Applikation erhöht oder gesenkt werden.
Die Applikation erlaubt auch die beiden variablen Faktoren `Berechtigte Altersklassen` und `Anteil der Impfwilligen` vorzugeben und berechnet für das gewählte Szenario den Zeitpunkt, an dem alle Impfwilligen Personen immunisiert sein werden.

Diese Applikation basiert - wie jedes Modell - auf vereinfachenden Annahmen und erhebt keinen Anspruch auf Vollständigkeit. Wählen sie im Navigationsbereich am linken Rand unter `Menu` den Menubefehl `Zeitreihen` aus.      

### Datenquellen und weitere Informationen zum Thema Covid-19-Impfung
- [Imfdaten, opendata.bs](https://data.bs.ch/explore/dataset/100111/information/?sort=datum)
- [Bevölkerung nach Altersgruppen, BAG](https://www.covid19.admin.ch/api/data/20210514-cx2d73ej/downloads/sources-csv.zip). Diese Zahlen liegen etwas tiefer als die, vom Kanton publizierten, Bevölkerungszahlen. Diese Datenquelle wurde gewählt, demit die Berechnungen auch bei einem späteren Einbzeug von anderen Kantonen konsistent bleiben.
- [Coronavirus: Covid-19 Impfung](https://www.bag.admin.ch/bag/de/home/krankheiten/ausbrueche-epidemien-pandemien/aktuelle-ausbrueche-epidemien/novel-cov/information-fuer-die-aerzteschaft/covid-19-impfung.html)
- [Impf-Dashboard BAG](https://www.covid19.admin.ch/de/epidemiologic/vacc-doses)
"""

    def show_menu(self): 
        st.markdown("### Info")
        st.markdown(self.text)
