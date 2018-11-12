#!/usr/bin/env python3

import os
import logging
import pandas as pd
logging.basicConfig(level=logging.DEBUG)

data_dir = "./package/data"
def_fp = "{}/definition.tsv".format(data_dir)
patch_fp = "{}/patch.tsv".format(data_dir)
backup_fp = "{}/.definition.tsv".format(data_dir)

def_df = pd.read_csv(def_fp, sep='\t')
print("found {} definitions".format(len(def_df)))
patch_df = pd.read_csv(patch_fp, sep='\t')
print("found {} patches".format(len(patch_df)))
os.rename(def_fp, backup_fp)
print("backuped {}".format(def_fp, backup_fp))

m2d = dict([(module_name, definition) for module_name, definition in zip(def_df["module_name"], def_df["definition"])])
for _, row in patch_df.iterrows():
    name = row["module_name"]
    if m2d[name] == row["patch"]:
        logging.debug("pass {}".format(name))
    elif m2d[name] == row["raw"]:
        m2d[name] = row["patch"]
        logging.debug("done {}".format(name))
    else:
        logging.error("patch for {} is outdated".format(name))

dct_lst = [{"module_name":key, "definition": val} for key, val in m2d.items()]
out_df = pd.DataFrame(dct_lst)
out_df = out_df[["module_name", "definition"]]
out_df.to_csv(def_fp, sep='\t', index=False)
print("output {}".format(def_fp))
