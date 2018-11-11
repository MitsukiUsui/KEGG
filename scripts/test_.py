#!/usr/bin/env python3

import os
import sys
import logging
import pandas as pd
sys.path.append("{}/../".format(os.path.dirname(os.path.abspath(__file__))))
from KEGG import ModuleMapper
#logging.basicConfig(level=logging.DEBUG)


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

mapper = ModuleMapper()
map_df = mapper.map(kos)
map_df["myloss"] = map_df["nb"] - map_df["na"]

#compare result
join_df = pd.merge(result_df, map_df, on="module_name", how="outer")
print("INCONSISTANT")
msk = (~join_df["loss"].isnull()) & (join_df["loss"]!=join_df["myloss"])
print(join_df[msk])
print()

print("LACK")
msk = (join_df["loss"].isnull()) & (join_df["myloss"] <= 2) & (join_df["na"] > 0)
print(join_df[msk])
print()
