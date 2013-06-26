# -*- coding: utf-8 -*-

import sys
import rq
from rq import Queue,Connection,Worker


# why this?  it can use the sqlalchemy's connection poll  from rq  Performance notes  
# add by notedit  2013-01-24

with Connection():

    qs = map(rq.Queue, sys.argv[1:]) or [rq.Queue()]
    
    w = rq.Worker(qs)
    w.work()


