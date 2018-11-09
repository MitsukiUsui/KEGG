import logging

class DefinitionParser:
    def __init__(self, text):
        self.text = text + '$' #append sentinal (non digit)

    def evaluate(self, kos):
        self.cur = 0 # reset cursor position
        self.kos = kos
        return self._expression()

    def _get(self):
        return self.text[self.cur]

    def _number(self):
        cur_start = self.cur
        logging.debug("num@{}:".format(cur_start))
        assert self._get() in ('K', 'M')
        ko = self._get()
        self.cur += 1
        while self._get().isdigit():
            ko += self._get()
            self.cur += 1
        ret = ko in self.kos
        logging.debug("num@{0}:{1}={2}".format(cur_start, self.text[cur_start:self.cur], ret))
        return ret

    def _factor(self):
        cur_start = self.cur
        logging.debug("fac@{}:".format(cur_start))
        if self._get() == '(':
            self.cur += 1
            ret = self._expression()
            assert self._get() == ')'
            self.cur += 1
            return ret
        else:
            return self._number()

    def _term(self):
        cur_start = self.cur
        logging.debug("ter@{}:".format(cur_start))

        ret = self._factor()
        while True:
            if self._get() == '+':
                self.cur += 1
                ret = self._factor() and ret
            elif self._get() == '-':
                self.cur += 1
                self._factor()# skip non-essential component
            else:
                break
        logging.debug("ter@{0}:{1}={2}".format(cur_start, self.text[cur_start:self.cur], ret))
        return ret

    def _expression(self):
        cur_start = self.cur
        logging.debug("exp@{}:".format(cur_start))

        ret = self._term()
        while True:
            if self._get() == ' ':
                self.cur += 1
                ret =  self._term() and ret
            elif self._get() == ',':
                self.cur += 1
                ret = self._term() or ret #keep this order to force evaluate
            else: #like )
                break
        logging.debug("exp@{0}:{1}={2}".format(cur_start, self.text[cur_start:self.cur], ret))
        return ret


def scrape_blocks(html):
    found = False
    for line in html.split('\n'):
        if "DEFINITION" in line:
            found = True
            break
    if not(found):
        print("DEFINITION line not found. Aborting...")
        return []

    text = line
    text = text.replace("DEFINITION", '').replace("--", '')
    text = ' '.join(text.strip().split()) #merge whitespaces
    for ch in (',', '+', '-'): #characters not allowed to have whitespace before
        text = text.replace(' '+ch, ch)

    blocks = []
    cnt = 0
    stt = 0
    for end, c in enumerate(text + ' '): # add whitespace as a sentinal
        if c == '(':
            cnt += 1
        elif c == ')':
            cnt -= 1
            assert cnt >= 0
        elif c == ' ':
            if cnt == 0:
                blocks.append(text[stt:end])
                stt = end + 1
    assert cnt == 0
    return blocks
