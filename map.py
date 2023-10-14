import folium
from folium.plugins import MarkerCluster
from flask import Flask, render_template_string, request, jsonify
import overpy
from numpy import square
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


cordinates = ["43.5739,39.6841,43.6138,39.7857","44.5251,33.3212,44.6823,33.7277","69.3246,87.9878,69.4024,88.3943","55.1100,61.2409,55.2360,61.6474","58.5104,31.1777,58.5680,31.3809","52.2504,104.191,52.3179,104.394"]
cordinates_ekb = ["56.7139,60.3616,56.9555,61.1746",1112,1539371,22];
cordinates_tula = ["54.0513,37.2121,54.3097,38.0251",145.8,548623,33];
corsinates_cpb = ["59.4953,28.4656,60.3799,31.7175",1439,5600044,30];

array = [["amenity","cafe",0],
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

city_square = [176.8,864,23.16,530,460,280]
population_array = [466078,340075,183299,1187960,1253030,61115]
air_quality = [35,45,25,23,35,24]
result_array = []
count = []
density_array = []
density_positive = []
density_negative = []

api = overpy.Overpass()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Веб-приложение с картой России</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
            <style>
            body {
                background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 50%, #d0f0c0 50%),
                background-position: center, center;  /* позиционирует изображение и градиент по центру */
                margin: 20px;
            }

                #map {
                    margin-top: 20px;
                    margin-left: auto;
                    margin-right: auto;
                    width: 80%;  /* или другой процент по вашему усмотрению */
                    height: 500px;
                }

                .leaflet-control-coordinates {
                    background-color: white;
                    padding: 5px;
                    border: 1px solid #ccc;
                }

                .button-container {
                    text-align: center;
                    margin-top: 10px; /* можно увеличить значение для большего отступа сверху */
                }

                #queryButton {
                    position: relative;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: #008CBA; /* Blue color */
                    color: white;
                    padding: 10px 24px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 2ф0px
                }

                #queryButton:hover {
                    background-color: #005f5f; /* Darker blue on hover */
                }

            </style>
        </head>
        <body>
            <div id="map"></div>
            <button id="queryButton">Запрос</button>
            <script>
                var city = "";  // глобальная переменная для хранения выбранного города

                function setCityVariable(cityName) {
    city = cityName;
    console.log("Выбранный город: " + city);
    // Отправка выбранного города на сервер
    $.ajax({
        url: '/set_city',
        method: 'POST',
        data: { cityName: city },
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.error(error);
        }
    });
}


                function onMarkerClick(e) {
                    var marker = e.target;
                    setCityVariable(marker.options.title);  // устанавливаем переменную city в значение имени города

                    var coordinatesDiv = document.querySelector('.leaflet-control-coordinates');
                    var coords = e.latlng;
                    var north = coords.lat + 0.01;
                    var south = coords.lat - 0.01;
                    var east = coords.lng + 0.01;
                    var west = coords.lng - 0.01;
                    coordinatesDiv.innerHTML = 'Координаты: ' + coords.toString() +
                                                  '<br>Север: ' + north.toFixed(4) + ', ' + coords.lng.toFixed(4) +
                                              '<br>Юг: ' + south.toFixed(4) + ', ' + coords.lng.toFixed(4) +
                                              '<br>Восток: ' + coords.lat.toFixed(4) + ', ' + east.toFixed(4) +
                                              '<br>Запад: ' + coords.lat.toFixed(4) + ', ' + west.toFixed(4);
                }

                var map = L.map('map', {
                    center: [61.5240, 105.3188],
                    zoom: 3,
                    maxBounds: [
                        [-90, -180],
                        [90, 180]
                    ],
                    maxBoundsViscosity: 1.0,
                    minZoom: 2,
                    maxZoom: 16
                });

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    noWrap: true
                }).addTo(map);

                var coordinatesControl = L.control({position: 'topright'});

                coordinatesControl.onAdd = function(map) {
                    var coordinatesDiv = L.DomUtil.create('div', 'leaflet-control-coordinates');
                    coordinatesDiv.innerHTML = 'Координаты: не выбраны';
                    return coordinatesDiv;
                };

                coordinatesControl.addTo(map);

                var markerTula = L.marker([54.2048, 37.6182], { title: "Тула" }).addTo(map)
                    .bindPopup('Тула')
                    .on('click', onMarkerClick);

                var markerEkaterinburg = L.marker([56.8389, 60.6057], { title: "Екатеринбург" }).addTo(map)
                    .bindPopup('Екатеринбург')
                    .on('click', onMarkerClick);

                var markerStPetersburg = L.marker([59.9343, 30.3351], { title: "Санкт-Петербург" }).addTo(map)
                    .bindPopup('Санкт-Петербург - Культурная столица России')
                    .on('click', onMarkerClick);

                $("#queryButton").click(function(){
                    $.ajax({
                        url: '/query_overpass',
                        type: 'POST',
                        success: function(response){
                            console.log(response);
                            // Действия с ответом сервера
                        },
                        error: function(error){
                            console.log(error);
                        }
                    });
                });
            </script>
        </body>
        </html>
    """)

@app.route('/set_city', methods=['POST'])
def set_city():
    city_name = request.form['cityName']
    print(f'Выбранный город: {city_name}')
    test()
    return "City set successfully", 200

@app.route('/query_overpass', methods=['POST'])
def query_overpass():
    result2 = api.query("node[amenity=cafe]({{bbox}});out;")
    print(result2)
    # Обработка результатов запроса
    return "Query was successful"  # возвращение ответа на клиент

if __name__ == '__main__':
    app.run(debug=True)

def test():
   print("есть")
def click(rer):
   for cordinate in cordinates:
      new_array=[]
      count_positive = 0
      count_negative = 0
      for item in array:
        result = api.query(f"node[{item[0]}={item[1]}]({cordinate});out;")
        len_nodes = len(result.nodes)
        new_array.append(len_nodes)
      if(item[2]==0):
         count_negative+=len_nodes
      elif(item[2]==1):
         count_positive+=len_nodes
      count.append([count_positive, count_negative])
      result_array.append(new_array)
      
   df = pd.DataFrame(count, columns=["positive","negativ"], index=["Сочи","Севастополь","Норильск","Челябинск","Нижний Новгород","Иркутск"])
   for i in range(len(city_square)):
      density_array.append(population_array[i]/city_square[i])
   df = df.assign(density=density_array)
   for i in range(len(count)):
      density_negative.append(count[i][0]/city_square[i])
      density_positive.append(count[i][1]/city_square[i])
   df = df.assign(density_negative=density_negative)
   df = df.assign(density_positive=density_positive)
   df = df.assign(air_quality=air_quality)
   features = ['density','positive','negativ','density_positive','density_negative','air_quality']
   X = df[features]
   scaler = StandardScaler()
   X_scaled = scaler.fit_transform(X)
   num_clusters = 3
   kmeans = KMeans(n_clusters=num_clusters, random_state=42)
   df['Cluster'] = kmeans.fit_predict(X_scaled)
   print(df)