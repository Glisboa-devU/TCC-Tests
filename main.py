import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
#
# df = pd.read_parquet("dados/bruto/corrida/ano=2022/ronda=22.parquet")
#
# print(df.shape)
# print(df.dtypes)
# print(df.head(-1))
#

# import requests
#
# for ano in range(2018, 2027):
#     r = requests.get(f"https://livetiming-mirror.fastf1.dev/static/{ano}/Index.json")
#     print(ano, r.status_code)

df = pd.read_parquet("dados/fastf1/bruto/desempenho/ano=2022/ronda=01.parquet")
print(df.dtypes)
print(df[["Driver", "LapNumber", "LapTime"]].head())