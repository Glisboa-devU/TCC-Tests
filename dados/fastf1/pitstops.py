from common import rodar, selecionar

def extrair(s, laps):
    return selecionar(laps, [
        "Driver", "LapNumber", "Stint", "Compound",
        "PitInTime", "PitOutTime",
    ])

rodar("pitstops", extrair)