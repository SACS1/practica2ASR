import rrdtool

def crearRRD():
    ret = rrdtool.create("monitorSSH.rrd",
                     "--start",'N',
                     "--step",'60',
                     "DS:tcpInSegs:COUNTER:120:U:U",
                     "DS:tcpOutSegs:COUNTER:120:U:U",
                     "RRA:AVERAGE:0.5:1:20",
                     "RRA:AVERAGE:0.5:1:20")
    if ret:
        print (rrdtool.error())

def vistaXML():
    rrdtool.dump('monitorSSH.rrd','test.xml')
