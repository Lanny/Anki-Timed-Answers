from anki.hooks import addHook, wrap
from aqt import mw
from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf
from aqt.utils import showInfo

class AnswerTimer(object):
    def __init__(self, card):
        self._card = card
        deckConf = mw.col.decks.confForDid(card.odid or card.did)
        self.answerTime = deckConf['rev'].get('timeToAnswer', 0)

    def isNeeded(self):
        return bool(self.answerTime)

    def start(self):
        mw.progress.timer(self.answerTime * 1000, self._timeLimitUp, False)

    def _timeLimitUp(self):
        # Make sure we haven't answered or moved onto a different question.
        if mw.reviewer.state == 'question' and mw.reviewer.card == self._card:
            mw.reviewer._showAnswer()

def customFormSetupUi(self, *args, **kwargs):
    _old = kwargs['_old']
    del kwargs['_old']
    ret = _old(self, *args, **kwargs)

    row = self.gridLayout_3.rowCount()
    spinBox = QSpinBox()
    spinBox.setMinimum(0)

    self.gridLayout_3.addWidget(QLabel('Time to Answer'), row, 0)
    self.gridLayout_3.addWidget(spinBox, row, 1)
    self.gridLayout_3.addWidget(QLabel('seconds'), row, 2)

    self.timeToAnswer = spinBox

    return ret

def customDeckConfSaveConf(self, *args, **kwargs):
    self.conf['rev']['timeToAnswer'] = self.form.timeToAnswer.value()

def customDeckConfLoadConf(self, *args, **kwargs):
    self.form.timeToAnswer.setValue(self.conf['rev'].get('timeToAnswer', 0))

def startTimer():
    card = mw.reviewer.card
    timer = AnswerTimer(card)

    if timer.isNeeded():
        timer.start()

DeckConf.saveConf = wrap(
    DeckConf.saveConf,
    customDeckConfSaveConf,
    'before')

DeckConf.loadConf = wrap(
    DeckConf.loadConf,
    customDeckConfLoadConf,
    'after')

dconf.Ui_Dialog.setupUi = wrap(
    dconf.Ui_Dialog.setupUi,
    customFormSetupUi,
    'around')
addHook('showQuestion', startTimer)
