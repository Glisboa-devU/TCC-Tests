from common import rodar, selecionar

def extrair(s, laps):
    return selecionar(laps, [
        "Driver", "LapNumber", "Stint",
        "Compound", "TyreLife", "FreshTyre",
    ])

# SOBRE O STINT:
#
# Stint é um período contínuo de corrida com o mesmo jogo de pneus.
# Ele é numerado em sequência por piloto: começa em 1 na largada e
# aumenta em 1 a cada parada nos boxes em que o piloto troca de pneu.
#
# Exemplo (piloto com duas paradas, corrida de 57 voltas):
#   Stint 1: voltas  1 a 18  (composto MEDIUM)
#   Stint 2: voltas 19 a 38  (composto HARD)
#   Stint 3: voltas 39 a 57  (composto SOFT)
#
# O Stint NÃO traz o início e o fim prontos. Eles são derivados no
# processar.py com um groupby por Ano, Ronda, Driver e Stint:
#   início = menor LapNumber do stint
#   fim    = maior LapNumber do stint
#
# Colunas relacionadas:
# - Compound:  composto do pneu naquela volta (SOFT, MEDIUM, HARD, INTERMEDIATE, WET).
# - TyreLife:  idade do pneu em voltas. Pode começar acima de 1 se o jogo
#              já foi usado antes (ex.: pneu usado na classificação).
# - FreshTyre: True se o jogo de pneus era novo ao entrar na pista.
#
# Cuidados:
# - Na FastF1, Stint vem como número decimal (1.0, 2.0). Converta para
#   inteiro no processamento, se for usar como chave.
# - Pode haver nulos em Stint, Compound ou TyreLife em algumas corridas.
#   Confira com df.isna().mean() antes de treinar.
# - Uma parada para trocar só a asa dianteira, sem trocar pneus, não deveria
#   mudar o Stint. Se o dado vier com falhas, a troca pode aparecer errada.

rodar("pneus", extrair)