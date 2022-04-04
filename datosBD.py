import sys
import rrdtool
import time

tiempo_actual = int(time.time())

def fetchBD(corte):

    ret = rrdtool.fetch( "monitorSSH.rrd", "-s",str(tiempo_actual - corte), "MIN")
    return ret
    
def lastUpdate():
    ret = rrdtool.lastupdate("monitorSSH.rrd")
    return ret
