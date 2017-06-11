from anki.hooks import addHook, wrap
from aqt import mw
from aqt.qt import *
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

    return ret

def time_limit_hit():
    mw.reviewer._showAnswer()

def start_timer():
    card = mw.reviewer.card
    deck_conf = mw.col.decks.confForDid(card.odid or card.did)
    answer_time = deck_conf.get('answer_time', 0)

    if answer_time:
        mw.progress.timer(answer_time * 1000, time_limit_hit, False)

dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi,
                               customFormSetupUi, 'around')
addHook('showQuestion', start_timer)
