from common import rodar, selecionar

def extrair_status(s, laps):
    return selecionar(laps, ["Driver", "LapNumber", "TrackStatus"])

def extrair_msgs(s, laps):
    return s.race_control_messages.copy()   # Time, Category, Message, Flag...

rodar("eventos", extrair_status)
rodar("race_control", extrair_msgs, messages=True)

# SOBRE O TRACKSTATUS:
#
# É o estado da pista durante a volta, como texto com códigos:
#   1 = pista livre (corrida normal)
#   2 = bandeira amarela
#   3 = pouco documentado (não costuma aparecer)
#   4 = Safety Car
#   5 = bandeira vermelha (corrida parada)
#   6 = Virtual Safety Car (VSC) acionado
#   7 = VSC terminando
#
# Os códigos se ACUMULAM na mesma volta: o valor lista todos os estados
# que ocorreram durante ela. Exemplos:
#   "1"   -> volta normal do início ao fim
#   "12"  -> normal e depois bandeira amarela
#   "124" -> normal, amarela e depois Safety Car
#   "45"  -> Safety Car seguido de bandeira vermelha
#
# No processar.py, SafetyCar = TrackStatus contém 4, 5, 6 ou 7
# (regex "[4567]"). Essas voltas são bem mais lentas e distorcem o
# modelo de ritmo, então ficam fora do treino (VoltaLimpa), mas continuam
# na tabela porque o Digital Twin precisa delas.
#
# Cuidados:
# - A amarela (2) não entra nessa regra. Para um treino mais rigoroso,
#   use "[24567]".
# - O código é por volta e não diz em que ponto da volta o evento ocorreu.
# - Pode vir nulo em algumas corridas. Confira com df.isna().mean().
#
# SOBRE O RACE_CONTROL:
#
# São as mensagens da direção de prova, uma por linha (Time, Category,
# Message, Flag), como "SAFETY CAR DEPLOYED". Elas dizem o que aconteceu
# e quando, e o TrackStatus resume o efeito em cada volta. A coluna Time
# está na mesma escala do clima e das voltas (tempo desde o início da sessão).