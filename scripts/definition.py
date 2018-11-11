#!/usr/bin/env python3

import os
import sys
import pandas as pd
sys.path.append("{}/../".format(os.path.dirname(os.path.abspath(__file__))))
from KEGG import scrape_definition

mod_fp = "./data/module.tsv"
def_fp = "./data/definition.tsv"
mod_dir = "./data/module"

mod_df = pd.read_csv(mod_fp, sep='\t')
print("found {} modules".format(len(mod_df)))

dct_lst = []
for _, row in mod_df.iterrows():
    fp = "{}/{}.txt".format(mod_dir, row["module_name"])
    html = open(fp).read()
    dct = {
        "module_name": row["module_name"],
        "definition": scrape_definition(html)
    }
    dct_lst.append(dct)

def_df = pd.DataFrame(dct_lst)
def_df = def_df[["module_name", "definition"]]
def_df.to_csv(def_fp, sep='\t', index=False)
print("output {}".format(def_fp))

