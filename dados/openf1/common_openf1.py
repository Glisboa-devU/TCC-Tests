import time
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import requests

BASE = "https://api.openf1.org/v1"
RAIZ = Path("../openf1/bruto")
ANOS = [2023]

ESPERA_S = 120    # espera entre tentativas após limite/rede
PAUSA_REQ = 1.0   # pausa entre requisições (o plano gratuito tem limite por segundo/minuto)
ERROS_TEMPORARIOS = (
    "ratelimit", "rate limit", "too many requests", "429",
    "timeout", "timed out", "connection", "temporarily",
    "server error", "502", "503", "504",
)


def selecionar(df, colunas):
    """Seleciona colunas e tolera campos ausentes."""
    return df[[c for c in colunas if c in df.columns]].copy()


def get(endpoint, **params):
    """GET na OpenF1 e retorna DataFrame (vazio se não houver resultados)."""
    r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=60)
    time.sleep(PAUSA_REQ)
    if r.status_code == 404:  # a OpenF1 responde 404 quando não há resultados
        return pd.DataFrame()
    r.raise_for_status()
    return pd.DataFrame(r.json())


def com_retentativa(rotulo, fn):
    """Executa fn(); em erro de limite/rede espera e repete. Em erro definitivo, retorna None."""
    while True:
        try:
            return fn()
        except Exception as e:
            texto = str(e).lower() + " " + type(e).__name__.lower()
            if any(t in texto for t in ERROS_TEMPORARIOS):
                print(f"LIMITE/REDE {rotulo} [{type(e).__name__}]: {e}")
                print(f"   aguardando {ESPERA_S // 60} min...")
                time.sleep(ESPERA_S)
            else:
                print(f"ERRO {rotulo} [{type(e).__name__}]: {e}")
                return None


def preparar_voltas(laps, pos, drivers):
    """
    Devolve um DataFrame com Driver, LapNumber, Position (posição ao fim da volta)
    mais as colunas originais da OpenF1.
    """
    laps = laps.copy()
    laps["date_start"] = pd.to_datetime(laps["date_start"], utc=True, format="ISO8601")
    laps = laps.sort_values(["driver_number", "lap_number"]).reset_index(drop=True)

    # fim da volta = início da próxima; na última, início + duração
    prox = laps.groupby("driver_number")["date_start"].shift(-1)
    calc = laps["date_start"] + pd.to_timedelta(laps["lap_duration"], unit="s")
    laps["fim_volta"] = prox.fillna(calc)

    pos = pos.copy()
    pos["date"] = pd.to_datetime(pos["date"], utc=True, format="ISO8601")
    pos = pos.sort_values("date")[["date", "driver_number", "position"]]

    ok = laps["fim_volta"].notna()
    a = laps[ok].sort_values("fim_volta")
    m = pd.merge_asof(
        a, pos, left_on="fim_volta", right_on="date",
        by="driver_number", direction="backward",
    )
    out = pd.concat([m, laps[~ok]], ignore_index=True)
    out = out.sort_values(["driver_number", "lap_number"]).reset_index(drop=True)

    sigla = drivers.drop_duplicates("driver_number").set_index("driver_number")["name_acronym"]
    out["Driver"] = out["driver_number"].map(sigla).fillna(out["driver_number"].astype(str))
    out["LapNumber"] = out["lap_number"]
    out["Position"] = out["position"].astype("Int64")
    return out


def rodar(grupo, extrair):
    """
    Percorre as corridas, chama extrair(session, laps) e salva
    bruto/<grupo>/ano=AAAA/ronda=NN.parquet

    Em erro de limite ou rede, espera e tenta a mesma corrida de novo.
    Em erro definitivo, pula.
    """
    for ano in ANOS:
        def listar():
            sess = get("sessions", year=ano, session_name="Race")
            meet = get("meetings", year=ano)
            return sess, meet

        r = com_retentativa(f"calendário {ano}", listar)
        if r is None:
            continue
        sess, meet = r
        sess = sess[~sess["is_cancelled"]].sort_values("date_start").reset_index(drop=True)
        meet = meet.set_index("meeting_key")

        for i, row in sess.iterrows():
            ronda = i + 1
            destino = RAIZ / grupo / f"ano={ano}" / f"ronda={ronda:02d}.parquet"
            if destino.exists():
                continue  # já coletado, permite retomar

            sk, mk = int(row["session_key"]), int(row["meeting_key"])
            print(f"Coletando {grupo} {ano} R{ronda}...")

            def coletar():
                laps = get("laps", session_key=sk)
                pos = get("position", session_key=sk)
                drv = get("drivers", session_key=sk)
                s = SimpleNamespace(
                    event={
                        "Location": row["location"],
                        "EventName": meet.loc[mk, "meeting_name"],
                    },
                    laps=preparar_voltas(laps, pos, drv),
                )
                df = extrair(s, s.laps.copy())
                df["Ano"], df["Ronda"] = ano, ronda
                destino.parent.mkdir(parents=True, exist_ok=True)
                df.to_parquet(destino, index=False)
                return True

            if com_retentativa(f"{grupo} {ano} R{ronda}", coletar):
                print(f"OK   {grupo} {ano} R{ronda}")