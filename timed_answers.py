import threading

from anki.hooks import addHook
from aqt.utils import showInfo
from aqt import mw

def time_limit_hit():
    mw.reviewer._showAnswer()

def start_timer():
    mw.progress.timer(5000, time_limit_hit, False)

addHook('showQuestion', start_timer)
