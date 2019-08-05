import os
tasks = []
for taskid in tasks:
    os.system('earthengine  task cancel ' + taskid + " &")