import overpy
import pandas as pd
import recomendations as rc
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

tags = [["amenity","cafe",0],
         ["highway","track",0],
         ["amenity","clinic",1],
         ["highway","footway",1],
         ["footway","sidewalk",1],
         ["cycleway","track",0],
         ["cycleway","opposite_track",0],
         ["amenity","traffic_park",0],
         ["amenity","bicycle_parking",1],
         ["amenity","bar",0],
         ["amenity","fast_food",0],
         ["amenity","food_court",0],
         ["amenity","pub",0],
         ["amenity","restaurant",0],
         ["amenity","training",1],
         ["amenity","dentist",1],
         ["amenity","casino",0],
         ["amenity","police",1],         
         ["amenity","bicycle_repair_station",1],
         ["amenity","marketplace",1],
         ["boundary","national_park",1],
         ["building","farm",1],
         ["building","farm_auxiliary",1],
         ["building","sports_hall",1],
         ["building","stadium",1],
         ["landuse","farmland",1],
         ["landuse","farmyard",1],
         ["landuse","winter_sports",1],
         ["route","bicycle",1],
         ["route","horse",1],
         ["route","inline_skates",1],
         ["route","tracks",0],
         ["shop","farm",1],
         ["shop","bicycle",1],
         ["shop","sports",1],
         ["shop","swimming_pool",1]]

date_ekb = ["56.7139,60.3616,56.9555,61.1746",1112,1539371,22,"Екатеринбург"];
date_tula = ["54.0513,37.2121,54.3097,38.0251",145.8,548623,33,"Тула"];
date_cpb = ["59.4953,28.4656,60.3799,31.7175",1439,5600044,30,"Санкт-Петербург"];
city_name = ""

def model_start():
    csv_file_path = "data.csv"
    df_base = pd.read_csv(csv_file_path, index_col="Unnamed: 0")
    city = date_cpb
    if(city_name=="Екатеринбург"):
      city = date_ekb
    elif(city_name=="Тула"):
      city = date_tula
    elif(city_name=="Санкт-Петербург"):
      city = date_cpb

    data_city = collecting_date_city(city)
    df_child = pd.DataFrame([data_city],index=[f'{city[len(city)-1]}'])
    df = df_base._append(df_child)
    print(df)

    features = ['density','positive','negativ','density_positive','density_negative','air_quality']

    X = df[features]

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3)
    df['Cluster'] = kmeans.fit_predict(x_scaled)
    feature_importance = kmeans.cluster_centers_.mean(axis=0)

    importance_df = pd.DataFrame({'Feature': df.columns[:-1], 'Importance': feature_importance})
    importance_df = importance_df.sort_values(by='Importance', ascending=False)
    print(importance_df.head(6))
    
    important_features = importance_df.iloc[:2,]
    print(important_features.head())
    text = ""
    for feature_index in range(len(important_features)):
        for rec_goal in rc.recomedations:
          if(important_features.iloc[feature_index,0]==rec_goal[0]):
            text += str(rec_goal[1])+'<br>'

    plt.figure(figsize=(10, 6))
    plt.bar(importance_df['Feature'], importance_df['Importance'],color="#87CEFA")
    plt.xlabel('Feature')
    plt.ylabel('Importance')
    plt.title('Feature Importance for Clustering')
    plt.savefig('important_features.png')
    return text

def collecting_date_city(city):
  api = overpy.Overpass()
  
  count_positive = 0
  count_negative = 0
  for item in tags:
    result = api.query(f"node[{item[0]}={item[1]}]({city[0]});out;")
    len_nodes = len(result.nodes)
    if(item[2]==0):
      count_negative+=len_nodes
    elif(item[2]==1):
      count_positive+=len_nodes 
  density = city[2]/city[1]
  density_negative = count_negative/city[1]
  density_positive = count_positive/city[1]
  
  data_city = {'positive':count_positive,'negativ':count_negative,'density':density,'density_negative':density_negative,'density_positive':density_positive,'air_quality':city[3]}
  return data_city