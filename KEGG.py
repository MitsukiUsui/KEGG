import logging


class Mapper:
    """
    na: the number of achievement of blocks
    nb: the number of blocks
    """

    def __init__(self, text):
        self.text = text + '$' #append non-digit sentinal to force stop k-number extension search

    def evaluate(self, kos):
        self.cur = 0 # reset cursor position
        self.kos = kos
        return self._expression()

    def _get(self):
        return self.text[self.cur]

    def _number(self):
        cur_start = self.cur
        logging.debug("num@{}:".format(cur_start))

        ontology = self._get()
        self.cur += 1
        if ontology == '?': #orphan gene
            na, nb = 0, 1
        elif ontology in ('K', 'M'): #k-number or m-number
            while self._get().isdigit():
                ontology += self._get()
                self.cur += 1
            na, nb = int(ontology in self.kos), 1
        else:
            logging.error("undefined number start with {}".format(ontology))
            assert False

        logging.debug("num@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
        return na, nb

    def _factor(self):
        cur_start = self.cur
        logging.debug("fac@{}:".format(cur_start))
        if self._get() == '(':
            self.cur += 1
            na, nb = self._expression()
            assert self._get() == ')'
            self.cur += 1
        else:
            na, nb = self._number()
        logging.debug("fac@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
        return na, nb

    def _term(self):
        cur_start = self.cur
        logging.debug("ter@{}:".format(cur_start))

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

        logging.debug("ter@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
        return na, nb

    def _expression(self):
        cur_start = self.cur
        logging.debug("exp@{}:".format(cur_start))

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
            logging.error("AND & OR co-exists in {}".format(self.text[cur_start:self.cur]))
            raise SyntaxError

        logging.debug("exp@{0}:{1}=({2},{3})".format(cur_start, self.text[cur_start:self.cur], na, nb))
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
        print("DEFINITION line not found. Aborting...")
        return None

    if end - stt == 1:
        ret = clean(lines[stt])
    else:
        ret = ' '.join(["({})".format(clean(line)) for line in lines[stt:end]])
    return ret


