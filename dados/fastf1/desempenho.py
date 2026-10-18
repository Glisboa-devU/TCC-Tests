from common import rodar, selecionar

def extrair(s, laps):
    df = selecionar(laps, [
        "Driver", "LapNumber", "LapTime",
        "Sector1Time", "Sector2Time", "Sector3Time",
        "LapStartTime", "Time", "IsAccurate",
    ])

    # Colunas em segundos (as originais, em timedelta, são mantidas)
    for c in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]:
        if c in df.columns:
            df[c + "_s"] = df[c].dt.total_seconds()

    return df

# ATENÇÃO sobre as colunas de tempo e o clima (ambiente):
#
# - LapStartTime: início da volta, em tempo decorrido desde o início da sessão.
# - Time:         fim da volta, na mesma escala.
# - LapTime:      duração da volta (aprox. Time - LapStartTime).
#
# A tabela "ambiente" (clima) também tem uma coluna "Time", na mesma escala,
# com uma medição por minuto. No processar.py, o clima é ligado a cada volta
# com merge_asof, usando LapStartTime (ou, se estiver nulo, Time - LapTime)
# para achar a medição mais próxima.
#
# Por isso LapStartTime e Time DEVEM continuar como timedelta no bruto.
# Se forem convertidos para segundos, o merge_asof com o clima deixa de funcionar.
# Toda conversão para segundos deve ser feita em novas colunas (_s),
# sem sobrescrever as originais.
#
# Obs.: "Time" aparece em várias tabelas com significados diferentes
# (fim da volta em desempenho, horário da medição em ambiente,
# horário da mensagem em race_control).

rodar("desempenho", extrair)