from common import rodar, selecionar

def extrair(s, laps):
    df = selecionar(laps, ["Driver", "LapNumber", "Team", "DriverNumber"])
    df["Circuito"] = s.event["Location"]
    return df

rodar("contexto", extrair)