import pandas as pd
import streamlit as st

import impfungen_bs
import info
import const as cn

__version__ = '0.0.1' 
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2021-05-15'
my_name = 'Basel-impft'
my_kuerzel = "BS-I"
GIT_REPO = 'https://github.com/lcalmbach/basel-impft'
conn = {}
config = {} # dictionary mit allen Konfigurationseinträgen
APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """
MENU_DIC = {info: 'Info', impfungen_bs: 'Zeitreihen'}

@st.cache()
def get_data():
    data = pd.read_csv(cn.DATA_URL, sep = ";")
    fields =['Datum',
            'Total verabreichte Impfungen',
            'Total Personen mit erster Dosis',
            'Total Personen mit ausschliesslich erster Dosis',
            'Total Personen mit zweiter Dosis'
        ]
    data = data[fields].rename(columns={
        'Datum':'datum',
        'Total verabreichte Impfungen':'total',
        'Total Personen mit erster Dosis': 'dosis1',
        'Total Personen mit ausschliesslich erster Dosis': 'nur_dosis1',
        'Total Personen mit zweiter Dosis': 'dosis2',
    })
    data['datum'] = pd.to_datetime(data['datum'])
    data = data.sort_values(by=['datum'])
    data_melted = pd.melt(data, id_vars=["datum"], value_vars=["total", "dosis1", "dosis2"], var_name="parameter", value_name="anzahl")
    return data, data_melted   

def main():
    st.set_page_config(
        page_title=my_name,
        page_icon="💉",
        layout="wide",
        initial_sidebar_state="expanded")
    st.sidebar.markdown("### 💉 Basel impft")
    data, data_melted = get_data()
    my_app = st.sidebar.selectbox("Menu", options=list(MENU_DIC.keys()),
        format_func=lambda x: MENU_DIC[x])
    app = my_app.App(data, data_melted)
    app.show_menu()
    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)
if __name__ == "__main__":
    main()

