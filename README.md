# Impf-Prognose-BS

## Introduction 

This applicaton allows to estimate the current status of covid-19 vaccinations of the population of Basel/Switzerland. Current vaccination and population data is read from the opendata portal data.bs.ch. The app visualizes time series diagrams for first and second vaccinations as well as for the total number of doses given as per today. The progress of the last 7 days is used to extrapolate future vaccinations until all elegible (according to age) and willing persons are vaccinated. The age threshold for elegible persons as well as the percentage of willing persons can adjusted and the horizontal line representing the number of persons to be vacccinated is accordingly adjusted. The second horizontal line represents herd immunity representing the percentage of the population that has to be immunue to assure that the virus is unlikely to spread among the few non immune. 

## Components
The application is implemented in Python and uses the framework [streamlit](https://streamlit.io/) and [altair](https://altair-viz.github.io/).

## Installation
Impf-Prognose-BS can be launched from [impf-prognose-bs](https://impf-prognose-bs.herokuapp.com/). To install the program locally, Python 3.6 or newer (y 3.9) must be installed on your target machine. Proceed as follows:

```
> git clone https://github.com/lcalmbach/basel-impft.git
> cd basel-impft
> pip -m venv env
> env\scripts\activate.bat
> pip install -r requirements.txt
> streamlit run app.py
``` 

