import pandas as pd
import serpapi 
import json
from tqdm import tqdm


df = pd.read_excel('dados.xlsx')
df['comb'] = df['TIPO']+' '+df['UNIDADE']
my_list = df['comb'].to_list()



results = pd.DataFrame()
results['comb'] =  my_list
results['place_id']=''
results['lat']=''
results['long']=''
results['phone']=''
results['address']=''
# f970996954f11ba524af75569fe3917ebcf09d0b5bf3303058b136dfbf7d45e3  paid
# e4cf8f8a3b885e2649e26369fd05b8cdb067de4355eac170850b36f2257d7533 free
for place in tqdm(my_list):
    sel = place
    #sel = 'EEMEI ALTO ALEGRE sao paulo'
    params = {
    'api_key': "f970996954f11ba524af75569fe3917ebcf09d0b5bf3303058b136dfbf7d45e3",
    'engine': "google_local",
    'google_domain': "google.com.br",
    'q': sel,
    # "location_requested": "Sao Paulo, State of Sao Paulo, Brazil",
    # "location_used":"Sao Paulo,State of Sao Paulo,Brazil",
    'hl': "pt",
    'gl': "br",
    'location': "Brazil"
    }

    search = serpapi.search(params)
    try:
        results.loc[results['comb'] ==sel,'place_id'] = search['local_results'][0]['place_id']
    except:
        pass
    try:
        results.loc[results['comb'] ==sel,'lat'] = search['local_results'][0]['gps_coordinates']['latitude']
    except:
        pass
    try:
        results.loc[results['comb'] ==sel,'long'] = search['local_results'][0]['gps_coordinates']['longitude']
    except:
        pass
    try:
        results.loc[results['comb'] ==sel,'phone'] = search['local_results'][0]['phone']
    except:
        pass
    try:
        results.loc[results['comb'] ==sel,'address'] = search['local_results'][0]['address']
    except:
        pass


results.to_excel('resultado.xlsx')


resultado_geral = df.merge(results)
resultado_geral.to_excel('resultado_geral.xlsx')