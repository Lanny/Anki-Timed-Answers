import random

from anki.hooks import addHook, wrap
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf
from aqt.utils import showInfo

LIVE_TIMER = None

timerJs = """
    ;(function(seconds, killHook) {
        var startTime = Date.now();
        var timerElement = $('<span class="answer-timer">')
            .prependTo('table .stat:first')
            .css('margin-left', '5px');

        window.killHooks = window.killHooks || {};
        window.killHooks[killHook] = function() {
            timerElement.remove();
            delete window.killHooks[killHook];
        };

        function formatTime(seconds) {
            var minutes = ~~(seconds / 60),
                seconds = ('0' + ~~(seconds %% 60)).substr(-2);

            return minutes + ':' + seconds;
        }


        ;(function tick() {
            var timeRemaining = seconds - (Date.now() - startTime) / 1000;

            if (timeRemaining <= 0) {
                if (killHook in window.killHooks) {
                    window.killHooks[killHook]();
                }

                return;
            }

            timerElement.text(formatTime(timeRemaining));

            setTimeout(tick, 1000);
        })();
    })(%s, '%s');
"""

class AnswerTimer(object):
    def __init__(self, card):
        self._card = card
        deckConf = mw.col.decks.confForDid(card.odid or card.did)
        self.answerTime = deckConf['rev'].get('timeToAnswer', 0)
        self.killHook = str(random.randint(0, 2**32))
        self.timerHasBeenInjected = False

    def isNeeded(self):
        return bool(self.answerTime)

    def start(self):
        mw.progress.timer(self.answerTime * 1000, self._timeLimitUp, False)
        self.injectTimer()

    def onQuestionAnswered(self):
        mw.bottomWeb.eval('window.killHooks["%s"]()' % self.killHook);

    def injectTimer(self):
        if (self.timerHasBeenInjected):
            return

        self.timerHasBeenInjected = True
        mw.bottomWeb.eval(timerJs % (self.answerTime, self.killHook));

    def _isRolling(self):
        return mw.reviewer.state == 'question' and mw.reviewer.card == self._card

    def _advanceTimer(self):
        if self._isRolling():
            mw.progress.timer(1000, self._advanceTimer, False)

    def _timeLimitUp(self):
        # Make sure we haven't answered or moved onto a different question.
        if self._isRolling():
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
    global LIVE_TIMER

    card = mw.reviewer.card

    if (LIVE_TIMER and LIVE_TIMER._card == card):
        return

    LIVE_TIMER = AnswerTimer(card)

    if LIVE_TIMER.isNeeded():
        LIVE_TIMER.start()

def stopTimer():
    global LIVE_TIMER
    LIVE_TIMER.onQuestionAnswered()

DeckConf.saveConf = wrap(
    DeckConf.saveConf,
    customDeckConfSaveConf,
    'before')

DeckConf.loadConf = wrap(
    DeckConf.loadConf,
    customDeckConfLoadConf,
    'after')

Reviewer._showAnswerButton = wrap(
    Reviewer._showAnswerButton,
    lambda *args, **kwargs: startTimer(),
    'after')

dconf.Ui_Dialog.setupUi = wrap(
    dconf.Ui_Dialog.setupUi,
    customFormSetupUi,
    'around')

addHook('showAnswer', stopTimer)
