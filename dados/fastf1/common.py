import time
from pathlib import Path
import fastf1
import pandas as pd

Path("cache_f1").mkdir(exist_ok=True)
fastf1.Cache.enable_cache("cache_f1")

RAIZ = Path("bruto")
ANOS = [2021, 2022]
CHAVES = ["Ano", "Ronda", "Driver", "LapNumber"]

ESPERA_S = 3600  # 1 hora entre tentativas
ERROS_TEMPORARIOS = (
    "ratelimit", "rate limit", "too many requests", "429",
    "timeout", "timed out", "connection", "temporarily",
)


def selecionar(df, colunas):
    """Seleciona colunas e tolera campos ausentes."""
    return df[[c for c in colunas if c in df.columns]].copy()


def rodar(grupo, extrair, weather=False, messages=False):
    """
    Percorre as corridas, chama extrair(session, laps) e salva
    bruto/<grupo>/ano=AAAA/ronda=NN.parquet

    Em erro de limite ou rede, espera e tenta a mesma corrida de novo.
    Em erro definitivo (corrida cancelada, dado inexistente), pula.
    """
    for ano in ANOS:
        sched = fastf1.get_event_schedule(ano, include_testing=False)
        for _, ev in sched.iterrows():
            ronda = int(ev["RoundNumber"])
            destino = RAIZ / grupo / f"ano={ano}" / f"ronda={ronda:02d}.parquet"
            if destino.exists():
                continue  # já coletado, permite retomar

            while True:
                try:
                    print(f"Coletando {grupo} {ano} R{ronda}...")
                    s = fastf1.get_session(ano, ronda, "R")
                    s.load(laps=True, weather=weather, telemetry=False, messages=messages)
                    df = extrair(s, s.laps.copy())
                    df["Ano"], df["Ronda"] = ano, ronda
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    df.to_parquet(destino, index=False)
                    print(f"OK   {grupo} {ano} R{ronda}")
                    time.sleep(2)
                    break
                except Exception as e:
                    texto = str(e).lower() + " " + type(e).__name__.lower()
                    if any(t in texto for t in ERROS_TEMPORARIOS):
                        print(f"LIMITE/REDE {grupo} {ano} R{ronda} [{type(e).__name__}]: {e}")
                        print(f"   aguardando {ESPERA_S // 60} min...")
                        time.sleep(ESPERA_S)
                    else:
                        print(f"ERRO {grupo} {ano} R{ronda} [{type(e).__name__}]: {e}")
                        break  # erro definitivo: pula esta corrida