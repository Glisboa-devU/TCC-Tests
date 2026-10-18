from common_openf1 import rodar, selecionar

def extrair(s, laps):
    df = selecionar(laps, ["Driver", "LapNumber", "Position"])
    df["Circuito"] = s.event["Location"]
    df["Evento"] = s.event["EventName"]
    df["TotalVoltas"] = laps["LapNumber"].max()
    return df

rodar("corrida", extrair)