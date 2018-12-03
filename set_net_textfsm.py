import os
tmpdir = os.path.dirname(os.path.realpath(__file__))
tmpdir = os.path.join(tmpdir, 'templates')
os.environ['NET_TEXTFSM'] = tmpdir