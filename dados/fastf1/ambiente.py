from common import rodar

def extrair(s, laps):
    return s.weather_data.copy()   # Time, AirTemp, TrackTemp, Humidity, Rainfall, WindSpeed...

rodar("ambiente", extrair, weather=True)