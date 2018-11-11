#!/usr/bin/env python3

import sys
import logging
import pandas as pd
from KEGG import Mapper
#logging.basicConfig(level=logging.DEBUG)

def_fp = "./data/definition.tsv"
def_df = pd.read_csv(def_fp, sep='\t')
m2d = dict([(key, val) for key, val in zip(def_df["module_name"], def_df["definition"])])

def load_kos(input_fp):
    kos = []
    for line in open(input_fp, 'r'):
        line_split = line.strip().split('\t')
        if len(line_split) == 2:
            kos.append(line_split[1])
    return set(kos)


test_name = sys.argv[1]
input_fp = "./test/input{}.txt".format(test_name)
result_fp = "./test/result{}.csv".format(test_name)
print("loaded {} & {}".format(input_fp, result_fp))

kos = load_kos(input_fp)
result_df = pd.read_csv(result_fp)

#map
dct_lst = []
for _, row in def_df.iterrows():
    dct = {"module_name": row["module_name"]}
    mapper = Mapper(row["definition"])
    try:
        dct["na"], dct["nb"] = mapper.evaluate(kos)
        dct_lst.append(dct)
    except SyntaxError:
        logging.error("malformed definition found for {}".format(row["module_name"]))
        sys.exit(1)
map_df = pd.DataFrame(dct_lst)
map_df["myloss"] = map_df["nb"] - map_df["na"]
join_df = pd.merge(result_df, map_df, on="module_name", how="outer")

print("INCONSISTANT")
msk = (~join_df["loss"].isnull()) & (join_df["loss"]!=join_df["myloss"])
print(join_df[msk])
print()

print("LACK")
msk = (join_df["loss"].isnull()) & (join_df["myloss"] <= 2) & (join_df["na"] > 0)
print(join_df[msk])
print()