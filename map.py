import folium
from folium.plugins import MarkerCluster
from flask import Flask, render_template_string, request, jsonify
import modal

app = Flask(__name__)
city_name = ""
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
                background-position: center, center;  
                margin: 20px;
            }

                #map {
                    margin-top: 5%;
                    margin-left: auto;
                    margin-right: auto;
                    width: 80%;  
                    height: 500px;
                }

                .leaflet-control-coordinates {
                    background-color: white;
                    padding: 5px;
                    border: 1px solid #ccc;
                }

                .button-container {
                    text-align: center;
                }

                #queryButton {
                    position: relative;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: #008CBA; 
                    color: white;
                    padding: 10px 24px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 2%;
                }

                #queryButton:hover {
                    background-color: #005f5f; 
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <button id="queryButton">Запрос</button>
            <script>
                var city = "";  

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
                    coordinatesDiv.innerHTML = 'Город не выбран';
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
                            var coordinatesDiv = document.querySelector('.leaflet-control-coordinates');
                            console.log(response);
                            var imageElement = document.createElement('img');
                            imageElement.src = './important_features.png';
                            imageElement.alt = 'Описание изображения';
                            coordinatesDiv.innerHTML = 'Рекомендации:<br>' + response.toString();
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
    modal.city_name = city_name
    return "City set successfully", 200

@app.route('/query_overpass', methods=['POST'])
def query_overpass():
    text = modal.model_start()
    print(text)  
    return str(text)

if __name__ == '__main__':
    app.run(debug=True)


