#!/usr/bin/env python3

import re
import sys
from bs4 import BeautifulSoup
import pandas as pd

def parse(text):
    soup = BeautifulSoup(text, 'html.parser')
    dct = {
        "module_name": soup.find("a").text,
        "result": text.split("&nbsp;")[-1].replace("<br>", '')
    }
    return dct

def result2loss(result):
    pattern = r"(\d+) block"
    m = re.search(pattern , result)
    if m is None:
        assert result == "(complete)"
        return 0
    else:
        return int(m.group(1))

html_fp = sys.argv[1]
out_fp = sys.argv[2]

html = open(html_fp, "r").read()
dct_lst = []
for line in html.split('\n'):
    prefix = "&nbsp;"*8 + "<a href=\'/kegg-bin/show_module"
    if line[:len(prefix)] == prefix:
        dct_lst.append(parse(line))
out_df = pd.DataFrame(dct_lst)
print("found {} results".format(len(out_df)))

out_df["loss"] = [result2loss(result) for result in out_df["result"]]
out_df.to_csv(out_fp, index=False)
print("output {}".format(out_fp))
