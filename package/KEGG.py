import os
import sys
from logging import getLogger
import pandas as pd

logger = getLogger(__name__)
PACKAGE_DIREC = os.path.dirname(os.path.abspath(__file__))
mod_fp = "{}/data/module.tsv".format(PACKAGE_DIREC)
def_fp = "{}/data/definition.tsv".format(PACKAGE_DIREC)

mod_df = pd.read_csv(mod_fp, sep='\t')
def_df = pd.read_csv(def_fp, sep='\t')
assert mod_df["module_name"].equals(def_df["module_name"])


class ModuleMapper:
    """
    na: the number of achievement of blocks
    nb: the number of blocks
    """

    def __init__(self, ignore_orphan=False):
        self.ignore_orphan = ignore_orphan

    def map(self, kos):
        dct_lst = []
        for _, row in def_df.iterrows():
            dct = {"module_name": row["module_name"]}
            try:
                dct["na"], dct["nb"] = self.evaluate(kos, row["definition"])
                dct_lst.append(dct)
            except SyntaxError:
                logger.error("malformed definition found for {}".format(row["module_name"]))
                sys.exit(1)
        map_df = pd.DataFrame(dct_lst)
        ret_df = pd.merge(mod_df, map_df, on="module_name")
        ret_df = ret_df[["module_name", "na", "nb", "desc"]]
        return ret_df

    def evaluate(self, kos, text):
        self.kos = kos
        self.text = text + '$' #append non-digit sentinal to force stop k-number extension search
        self.cur = 0 # reset cursor position
        return self._expression()

    def _get(self):
        return self.text[self.cur]

    def _number(self):
        cur_start = self.cur
        logger.debug("num@{}:".format(cur_start))

        ontology = self._get()
        self.cur += 1
        if ontology == '?': #orphan gene
            if self.ignore_orphan:
                na, nb = 1, 1
            else:
                na, nb = 0, 1
        elif ontology in ('K', 'M'): #k-number or m-number
            while self._get().isdigit():
                ontology += self._get()
                self.cur += 1
            na, nb = int(ontology in self.kos), 1
        else:
            logger.error("undefined number start with {}".format(ontology))
            assert False

        logger.debug("num@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
        return na, nb

    def _factor(self):
        cur_start = self.cur
        logger.debug("fac@{}:".format(cur_start))
        if self._get() == '(':
            self.cur += 1
            na, nb = self._expression()
            assert self._get() == ')'
            self.cur += 1
        else:
            na, nb = self._number()
        logger.debug("fac@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
        return na, nb

    def _term(self):
        cur_start = self.cur
        logger.debug("ter@{}:".format(cur_start))

        na, nb = self._factor()
        while self._get() in ('+', '-'):
            op = self._get()
            self.cur += 1
            na_, nb_ = self._factor()
            assert na <= 1 and nb == 1 and na_ <= 1 and nb_ == 1 # + and - can only be applicable between k-numbers
            if op == '+':
                na *= na_
                nb *= nb_
            elif op == '-': # ignore non-essential component
                pass

        logger.debug("ter@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
        return na, nb

    def _expression(self):
        cur_start = self.cur
        logger.debug("exp@{}:".format(cur_start))

        na, nb = self._term()
        ops = set()
        while self._get() in (' ', ','):
            op = self._get()
            ops.update(op)
            self.cur += 1

            na_, nb_ =  self._term()
            if op == ' ':
                na += na_
                nb += nb_
            elif op == ',':
                if (nb_-na_) < (nb-na) or ((nb_-na_) == (nb-na) and na_ > na): # prioritise smaller loss or higher achievement
                    na, nb = na_, nb_

        if len(ops) == 2:
            logger.error("AND & OR co-exists in {}".format(self.text[cur_start:self.cur]))
            raise SyntaxError

        logger.debug("exp@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
        return na, nb


def scrape_definition(html):
    def clean(line):
        text = line
        text = text.replace("DEFINITION", '')
        text = text.replace("--", '?') #parser prefer single character
        text = ' '.join(text.strip().split()) #merge whitespaces
        for ch in (',', '+', '-'): #characters not allowed to have whitespace before
            text = text.replace(' '+ch, ch)
        return text

    lines = html.split('\n')
    stt, end = -1, -1
    for idx, line in enumerate(lines):
        if line[:10] == "DEFINITION":
            stt = idx
        elif stt != -1 and line[0]!=' ':
            end = idx
            break
    if stt == -1 or end == -1:
        logger.error("DEFINITION line not found. Aborting...")
        return None

    if end - stt == 1:
        ret = clean(lines[stt])
    else:
        ret = ' '.join(["({})".format(clean(line)) for line in lines[stt:end]])
    return ret


