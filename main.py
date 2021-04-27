import requests
import json
import pandas as pd
from fastapi import FastAPI
import uvicorn


data = requests.get("https://covid-api.mmediagroup.fr/v1/cases?country=Germany")

json.loads(data.text)
data_new = data.json()
df = pd.DataFrame(data_new)
df_all = df['All']
df = df.drop(['All'], axis=1)
data_df = df.stack()
data_df = data_df.unstack(level=0)
data_df=data_df.drop(index='Unknown')
data_df = data_df.drop(['lat'], axis=1)
data_df = data_df.drop(['long'], axis=1)
data_df = data_df.drop(['updated'], axis=1)

#top 3 data
top_3_confirmed = data_df[['confirmed']].sort_values(by=['confirmed'], ascending = False).head(3)
top_3_deaths = data_df[['deaths']].sort_values(by=['deaths'], ascending = False).head(3)
top_3_recovered = data_df[['recovered']].sort_values(by=['recovered'], ascending = False).head(3)

#add percentage recovered
data_df['%recovered'] = (data_df['recovered']/data_df['confirmed'])*100
perc_recovered_mean = (data_df['%recovered'].mean())
list_perc_recovered = []
list_index_perc_recovered = []
for index,row in data_df.iterrows():
    if row['%recovered'] >= perc_recovered_mean:
        list_perc_recovered.append(row['%recovered'])
        list_index_perc_recovered.append(index)
city_recovered = pd.Series(list_perc_recovered, index =list_index_perc_recovered)
            
#add percentage deaths
data_df['%deaths'] = (data_df['deaths']/data_df['confirmed'])*100
perc_deaths_mean = (data_df['%deaths'].mean())
list_perc_deaths = []
list_index_perc_deaths = []
for index,row in data_df.iterrows():
    if row['%deaths'] >= perc_deaths_mean:
        list_perc_deaths.append(row['%deaths'])
        list_index_perc_deaths.append(index)
city_deaths = pd.Series(list_perc_deaths, index =list_index_perc_deaths)

#builld API
app =FastAPI()

@app.get("/")
def read_menu():
	return{ "Greetings": "Welcome to Germany's Covid Report", "Menu ": "Link", "Master Table" : "http://127.0.0.1:8000/master", "Top 3 City Confirmed" : "http://127.0.0.1:8000/top_3_confirmed", "Top 3 City Deaths" : "http://127.0.0.1:8000/top_3_deaths", "Top 3 City Recovered" : "http://127.0.0.1:8000/top_3_recovered", "% Deaths" : "http://127.0.0.1:8000/percen_deaths", "List of deaths cases per city that more than average" : "http://127.0.0.1:8000/perc_deaths_city",  "% Recovered" : "http://127.0.0.1:8000/percen_recovered", "List of recovered cases per city that more than average" : "http://127.0.0.1:8000/perc_recovered_city" }

@app.get("/master")
def read_root():
	return  {"Data of summary covid cases in Germany": json.loads(data_df.to_json(orient="columns")),
          "Analisis": "Secaara umum Kota Nordhein-Westfalen merupakan kota dengan jumlah kasus covid tertinggi (baik itu kasus terkonfirmasi, kematian, maupun kesembuhan). Namun kota dengan nilai persentase kesembuhan tertinggi ada pada Kota Berlin, dan Kota dengan nilai persentase kasus kematian tertinggi ada pada Kota Bradenburg. Ini artinya kota dengan jumlah kasus tertinggi (kesembuhan/kematian) belum tentu memiliki nilai persentase (kesembuhan/kematian) yang tinggi juga."}

@app.get("/top_3_confirmed")
def read_root():
	return  {"Top 3 city with higher confirmed cases": json.loads(top_3_confirmed.to_json(orient="columns")),
          "Analisis" : " 3 kota dengan kasus terkonfirmasi covid tertingi dipegang oleh Nordhein-Westfalen, Bayren, dan Baden-Wurttemburg dengan konfirmasi kasus tertinggi ada pada kota Nordhein-Westfalen dengn 15.287 ribu kasus terkonfirmasi covid"}
	
@app.get("/top_3_deaths")
def read_root():
	return  {"Top 3 city with higher deaths cases" : json.loads(top_3_deaths.to_json(orient="columns")),
          "Analisis": "3 Kota dengan kasus kematian akita covid terbanyak juga dipegang oleh Nordhein-Westfalen, Bayren, dan Baden-Wurttemburg"}
	
@app.get("/top_3_recovered")
def read_root():
	return  {"Top 3 city with higher recovered rate" : json.loads(top_3_recovered.to_json(orient="columns")),
          "Analisis" : "Sama seperti kasus terkonfirmasi covid dan kasus kematian akibat covid, 3 kota dengan jumlah penduduk yang sembuh dari covid dipegang oleh Nordhein-Westfalen, Bayren, dan Baden-Wurttemburg. Ini berarti pada ketiga kota tersebut jumlah kasus kematian akibat covid yang tinggi juga diimbangi dengan jumlah kesembuhan dari covid."}

@app.get("/percen_deaths")
def read_root():
	return {"Percent average of deaths cases (%)" : perc_deaths_mean, 
         "Analisis": "Nilai tersebut merupakan nilai rata-rata persentase kasus kematian akibat covid dari seluruh kasus yg terjadi"}
	
@app.get("/perc_deaths_city")
def read_root():
	return {"List of deaths cases per city that more than average" :json.loads(city_deaths.to_json(orient="columns")),
         "Analisis" : "7 dari 16 kota di Jerman memiliki persentase kematian akibat covid lebih dari rata-rata. Kota Brandenburg merupakan kota paling tinggi dengan nilai persentase kematian akibat covid sebanyak 3.5%"}
	
@app.get("/percen_recovered")
def read_root():
	return {"Percent average of recovered cases (%)" : perc_recovered_mean,
         "Analisis": "Nilai tersebut merupakan nilai rata-rata persentase kasus sembuh covid dari seluruh kasus yg terjadi"}
    
@app.get("/perc_recovered_city")
def read_root():
	return {"List of recovered cases per city that more than average": json.loads(city_recovered.to_json(orient="columns")),
         "Analisis" : "Hanya ada 6 dari 16 kota di Jerman yang memiliki persetase kesembuhan covid diatas persentase ksembuhan covid rata-rata. Selain itu persentase kesembuhan tertinggi ada pada kota Berlin dengan nilai 92.12% "}
