import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import haversine_distances
from geopy.geocoders import Nominatim
from geopy.distance import geodesic as geodesic_geopy
from geographiclib.geodesic import Geodesic as geodesic_gglib
from geokernels.geodesics import geodesic_vincenty
import numpy as np
import plotly.express as px
import streamlit as st
from PIL import Image
from io import BytesIO
# nads

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def do_stuff_on_page_load():
    st.set_page_config(layout="wide", page_title = 'Real-Time Data Dashboard', page_icon='Active')
do_stuff_on_page_load()


df = pd.read_excel('resultado_geral.xlsx')


st.markdown('# Encontre as melhores unidades')

image = Image.open('qrcode.png')


col1, col2, col3 = st.columns([3,1,3])

col1.markdown('#### Digite seu endereço:')
col1.markdown('Endereço dever servir como referencia para o descolcamento.')
col1.markdown('Por exemplo, pode ser seu local de trabalho ou sua casa. :blue[**Rua Heitor Diniz Campello, 248, São Paulo**]')

title = col1.text_input('Escreva aqui', '')
col1.markdown('''Como padrão colocamos 6Km o limite de deslocamento, mas você pode alterar como preferir.
              :blue[**Sugerimos entre 6-8Km, pois essa distância é equivalente a 30 minutos de viajem.**]''')
number = col1.number_input("Insira o limite de Km...", value=6, placeholder="Insira o limite de Km...")
col1.markdown('''Este tempo de viagem pode ser estimado via google e é dependentente de uma 
              séria de fatores como, transito, clima dentre outros.''')
col1.markdown('''A tabela abaixo mostra as unidades mais próximas de acordo com o limite de 
              deslocamento escolhido. :blue[**Você pode baixa-la clicando no botão abaixo.**]''')




if number:
    if title:
        # create a Nominatim object
        geolocator = Nominatim(user_agent="tutorial")
        location = geolocator.geocode(title)

        # print(location.raw)
        # print(location.address)
        # print((location.latitude, location.longitude))

        distance_geopy = []
        distance_gglib = []
        distance_geokernels = []

        for i in range(df.shape[0]):

            coord1 = (location.latitude, location.longitude)  
            coord2 = (df['lat'][i], df['long'][i])   

            distance_geopy.append(float(geodesic_geopy(coord1, coord2).meters))
            distance_gglib.append(float(geodesic_gglib.WGS84.Inverse(coord1[0], coord1[1], coord2[0], coord2[1])['s12']))
            distance_geokernels.append(float(geodesic_vincenty(coord1, coord2)))


        df['distancias'] = distance_geopy
        df['distancias'] = df['distancias'].astype(float)
        df['distancias'] = df['distancias']/1000

        #df[df['distancias']<=10]



        df2 = df[df['distancias']<=number][['lat', 'long', 'UNIDADE']]
        df2 = df2.set_axis(['lat', 'lon', 'UNIDADE'], axis=1)

        # Example 1: Add Row to DataFrame
        new_row = {"lat": location.latitude, "lon" :location.longitude}
        new_df = pd.DataFrame([new_row],index=[df2.tail(1).index+1],columns=df2.columns)
        df2 = pd.concat([df2, new_df], axis=0)
        df2['data'] = ['Demais Unidades'] * (df2.shape[0]-1) + ['Seu Local']
        df2['size'] = 10

        #st.map(df2)



    

        fig = px.scatter_mapbox(df2, lat="lat", lon="lon", zoom=10, color_discrete_sequence=['blue', 'red'],
                                color="data", size = 'size', size_max=10, width=600, height=600,
                                text = 'UNIDADE')

        fig.update_layout(mapbox_style="open-street-map", 
                          showlegend=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        col3.markdown('''**Abaixo você pode verificar no mapa de são paulo o endereço fornecido em :red[vermelho]
                      e as demais unidades em :blue[azul].**''')
        col3.plotly_chart(fig)
        
        

        
        
        df_sel = df[df['distancias']<=number]  
        csv = to_excel(df_sel)
        col1.download_button(
            label="Baixar excel",
            data=csv,
            file_name='unidades.xlsx',
            mime='text/csv',
        )
        col1.markdown(f'''Total unidades: :red[**{df_sel.shape[0]}**]''')
        col1.markdown(f'''Total de vagas: :red[**{df_sel['VAGA DEFITIVA'].sum()}**]''')        
        col1.dataframe(df_sel[['DRE', 'TIPO', 'UNIDADE', 'VAGA DEFITIVA', 'VAGA PRECÁRIA','distancias']])
        col31, col32 = col3.columns([2,1])
        
        col31.markdown(':blue[**Esse é um trabalho voluntário**]. Se puder faça um PIX de 8, 10 ou 15 reais')
        col31.markdown('Leia o qrcode PIX ao lado com seu app do banco ou use a chave PIX: :red[**jaques.zanon@gmail.com**]')
        col32.image(image,use_column_width=False, width=200)
