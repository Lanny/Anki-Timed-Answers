from anki.hooks import addHook

def _start_timer():
    print 'hai'
    raise Exception('lol')
    pass

addHook('showQuestion', _start_timer)
