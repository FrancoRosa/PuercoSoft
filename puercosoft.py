#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
from redisworks import Root
import numpy as np
import pyqtgraph as pg
import time, serial, csv
import sys, glob
import os
#import qdarkstyle

##########################################################
# Sample Frecuency: 3.315Hz
samplingFrecuency = 3315
samplingPeriod = 0.00030166
voltageamplitude = 3.3
buffersamples = 663
buffertime = 10
plotLen =  buffertime*buffersamples*5 #Numero de Muestras totales
sliceLen = 663
threshold = 50
ksamples = 40
msamples = plotLen/ksamples
geophone = "Out"
recordFlag = False
runningFlag = True
quitFlag =False
plotingFlag = True
flagCh1 = True
flagCh2 = True
recordCounter=0

saveX = []
saveY = []
listX = []
listY = []
##########################################################

root = Root()

def matrixInit():
    global plotX,plotY,plotT
    plotX = [0]*plotLen # Geophone 2 data
    plotY = [0]*plotLen # Geophone 2 data
    plotT = np.arange(0.0, plotLen*1.0/samplingFrecuency, 1.0/samplingFrecuency) # time data

matrixInit()


#############################
# Grapichs Layout
#############################
app = QtGui.QApplication([])
win = QtGui.QMainWindow()
#app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())
win.setWindowTitle('Electrooculograma')
win.resize(1000,600)
pg.setConfigOptions(antialias=True)

#############################
# Layout
win1 = pg.LayoutWidget()
win.setCentralWidget(win1)

fig2 = pg.PlotWidget(title='<div style="text-align: center;"><span style="color: #FF0; font-size: 14pt;">Electrooculograma</span></div>')
fig2.setLabel(axis="bottom",text="Tiempo",units="s")
fig2.setLabel(axis="left",text="Amplitud",units="V")
fig2.setLabel(axis="top",text='<span style="color: #FF0; font-size: 12pt;">Señales Eléctricas</span>')
fig2.setYRange(0,3.3);
fig2.showGrid(x=True, y=True)
fig2.addLegend()

lineR = pg.InfiniteLine(movable = True, label = "T1")
lineG = pg.InfiniteLine(movable = True, label = "T2")
fig2.addItem(lineG)
fig2.addItem(lineR)

curve1f1 = fig2.plot(pen='r',name="Canal 1")
curve1f1.setData(plotT,plotX)

curve2f1 = fig2.plot(pen='g',name="Canal 2")
curve2f1.setData(plotT,plotY)


processlabel = QtGui.QLabel(">>> Adquiriendo señales")
graphlabel = QtGui.QLabel("Grafica:")
thresEdit = QtGui.QLineEdit(str(threshold))
timeLabel = QtGui.QLabel("Duracion: 0s")
diflabel = QtGui.QLabel("T1-T2:  0.00ms")
strstpBtn = QtGui.QPushButton('Inicio/Pausa')
recordBtn = QtGui.QPushButton('Grabar')
saveBtn = QtGui.QPushButton('Guardar')
exitBtn = QtGui.QPushButton('Salir')

graphSel = QtGui.QComboBox()
graphSel.addItem('Ch1 & Ch2')
graphSel.addItem('Ch1')
graphSel.addItem('Ch2')

processlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
graphlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
timeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

win.showFullScreen()
win1.addWidget(fig2,0,0,1,14)
win1.nextRow()
win1.addWidget(processlabel,col=0)
win1.addWidget(graphlabel,col=3)
win1.addWidget(graphSel,col=4)
win1.addWidget(timeLabel,col=6)
win1.addWidget(diflabel,col=8)
win1.addWidget(strstpBtn,col=10)
win1.addWidget(recordBtn,col=11)
win1.addWidget(saveBtn,col=12)
win1.addWidget(exitBtn,col=13)

def changeThreshold():
    global threshold
    threshold = int(thresEdit.text())

def startstop():
    global runningFlag
    runningFlag = not(runningFlag)
    if runningFlag:
        processlabel.setText(">>> Adquiriendo señales")
    else:
        processlabel.setText(">>> Adquisicion pausada")

def recorddata():
    global recordFlag, recordCounter
    recordFlag = not(recordFlag)
    if recordFlag:
        recordCounter = time.time()
        recordBtn.setText("Detener")
        if runningFlag:
            processlabel.setText(">>> Adquiriendo señales - Grabando")
        else:
            processlabel.setText(">>> Adquisicion pausada - Grabando")
    else:
        recordBtn.setText("Grabar")


def verifyLen(timestamp):
    samples = buffersamples
    try:
        if (len(root.data_ch1) == samples) and (len(root.data_ch2) == samples):
            if root.timestamp>timestamp:
                return True
        else:
            return False
    except:
        return False

timestamp = 0

def getData():
    global cPort, threshold
    global plotX,plotY,plotT,plotLen,saveX,saveY
    global startFlag, quitFlag, plotingFlag
    global curve1f1
    global curve2f1
    global timestamp
    global recordCounter
    sliceCounter = 0
    sliceplotX = [0]*sliceLen
    sliceplotY = [0]*sliceLen
    sliceplotT = [0]*sliceLen
    root.flush()
    if verifyLen(timestamp):
        timestamp = root.timestamp
        plotX[:(plotLen - sliceLen)]=plotX[sliceLen:plotLen]
        plotY[:(plotLen - sliceLen)]=plotY[sliceLen:plotLen]
        plotX[(plotLen - sliceLen):]=root.data_ch1
        plotY[(plotLen - sliceLen):]=root.data_ch2
        if recordFlag:
            saveX.append(root.data_ch1)
            saveY.append(root.data_ch2)
            timeLabel.setText("Duracion %2.2fs"%(time.time()-recordCounter))

        if runningFlag:
            if flagCh1:
                curve1f1.setData(plotT,plotX)
            else:
                curve1f1.clear()
            if flagCh2:
                curve2f1.setData(plotT,plotY)
            else:
                curve2f1.clear()

timer = QtCore.QTimer()
timer.timeout.connect(getData)
timer.start(100)


def savecsv(self):
    global saveX, saveY, listX, listY
    z = 0
    for x in saveX:
        listX = listX + list(x)
    for y in saveY:
        listY = listY + list(y)


    path = QtGui.QFileDialog.getSaveFileName(
        parent = None,
        caption='Guardar Archivo',
        directory='',
        filter='CSV(*.csv)')
    datetime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    print(path)
    newfile = path[0]+'_%s.csv'%datetime
    with open(newfile, 'w') as stream:
        writer = csv.writer(stream)
        writer.writerow(['Fecha:',time.strftime("%Y/%m/%d", time.localtime())])
        writer.writerow(['Hora:',time.strftime("%H:%M:%S", time.localtime())])
        #writer.writerow(['Geofono:',geoSel.currentText()])
        writer.writerow(['Muestreo:',"3.315Khz"])

        writer.writerow(['t(ms)','Canal_1','Canal_2'])
        t = 0
        s= samplingPeriod
        for row in range(len(listX)):
            rawdata = [t, listX[row], listY[row]]
            t = t + s

            writer.writerow(rawdata)
    saveX = []
    saveY = []
    listX = []
    listY = []

def grapSelector():
    global flagCh1, flagCh2
    plotSelection = str(graphSel.currentText())
    if "Ch1" in plotSelection:
        flagCh1 = True
    else:
        flagCh1 = False

    if "Ch2" in plotSelection:
        flagCh2 = True
    else:
        flagCh2 = False

def lineMoved(evt):
    t1 = lineG.value()
    t2 = lineR.value()
    diferencia = t1-t2
    diflabel.setText('T1-T2: % 2.4fs'%diferencia)

lineG.sigPositionChangeFinished.connect(lineMoved)
lineR.sigPositionChangeFinished.connect(lineMoved)

def exit():
    global quitFlag
    quitFlag = True
    os.system('pkill -f serial2puerco.py')
    app.quit()

strstpBtn.clicked.connect(startstop)
recordBtn.clicked.connect(recorddata)
saveBtn.clicked.connect(savecsv)
exitBtn.clicked.connect(exit)
thresEdit.textEdited.connect(changeThreshold)
graphSel.activated[str].connect(grapSelector)

## Start Qt event loop unless running in interactive mode or using pyside.
QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("windowsvista"))
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
