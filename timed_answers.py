from anki.hooks import addHook, wrap
from aqt import mw
from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf
from aqt.utils import showInfo

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

def timeLimitHit():
    mw.reviewer._showAnswer()

def startTimer():
    card = mw.reviewer.card
    deckConf = mw.col.decks.confForDid(card.odid or card.did)
    answerTime = deckConf['rev'].get('timeToAnswer', 0)

    if answerTime:
        mw.progress.timer(answerTime * 1000, timeLimitHit, False)

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
