#!/usr/bin/env python
'''
Created on 21/12/2013
 -----------------------------------------------------------------------------------------------
|31|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |15|  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0|
 -----------------------------------------------------------------------------------------------
|                                               |                                               |

31 - 16 Left pos
15 - 00 Right pos

 -----------------------------------------------------------------------------------------------
|31|30|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0|
 -----------------------------------------------------------------------------------------------
|  |  |                                                                                         |

31      Left Switch
30      Right Switch
29 - 00 timestamp

@author: markp
'''


import sys
import struct
import sqlite3 as lite
import csv
from PyQt4 import QtCore, QtGui
from decode_pedals_gui import Ui_decodePedals
import pyqtgraph as pg
import numpy as np

class FPData:
  pass

fp = FPData()
MAXVAL = 1024.0

'''The following section is necessary for py2exe to create an executable on windws'''
from pyqtgraph.graphicsItems import TextItem
def dependencies_for_myprogram():
    from scipy.sparse.csgraph import _validation


class StartQT4(QtGui.QMainWindow):
  def __init__(self, parent=None):
    self.filename = None
    self.db = DbData()
    self.isPlotted = False
    self.unpackVersion = 'unpackDataVersion1'
    fp.leftMaxPedal = 0
    fp.rightMaxPedal = 0
    fp.leftOff = 0; fp.leftOn = 0
    fp.rightOff = 0; fp.rightOn = 0
    fp.leftMaxFile = 0; fp.rightMaxFile = 0
    fp.leftScale = 1.0
    fp.rightScale = 1.0
    fp.swScale = 1
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_decodePedals()
    self.ui.setupUi(self)
    self.updateStatus()
    self.ui.numRowsVal.setText("0")
    self.pFlags = [False, False, False, False, False]
    
    QtCore.QObject.connect(self.ui.buttonOpen,QtCore.SIGNAL("clicked()"), self.fileOpenDialog)
    QtCore.QObject.connect(self.ui.buttonSave,QtCore.SIGNAL("clicked()"), self.fileSaveDialog)
    QtCore.QObject.connect(self.ui.normCheckBox,QtCore.SIGNAL("clicked()"), self.dataNorm)
    QtCore.QObject.connect(self.ui.actionLeft_Pos,QtCore.SIGNAL("triggered()"), self.updatePlotFlags)
    QtCore.QObject.connect(self.ui.actionRight_Pos,QtCore.SIGNAL("triggered()"), self.updatePlotFlags)
    QtCore.QObject.connect(self.ui.buttonPlot,QtCore.SIGNAL("clicked()"), self.makePlot)
    QtCore.QObject.connect(self.ui.checkBoxLP,QtCore.SIGNAL("clicked()"), self.updatePlotFlags)
    QtCore.QObject.connect(self.ui.checkBoxRP,QtCore.SIGNAL("clicked()"), self.updatePlotFlags)
    QtCore.QObject.connect(self.ui.checkBoxLS,QtCore.SIGNAL("clicked()"), self.updatePlotFlags)
    QtCore.QObject.connect(self.ui.checkBoxRS,QtCore.SIGNAL("clicked()"), self.updatePlotFlags)
    QtCore.QObject.connect(self.ui.checkBoxKbd,QtCore.SIGNAL("clicked()"), self.updatePlotFlags)
    QtCore.QObject.connect(self.ui.actionCase_1,QtCore.SIGNAL("triggered()"), self.analyseBothOne)
    QtCore.QObject.connect(self.ui.radioVersion1,QtCore.SIGNAL("clicked()"), self.setUnpackVersion)
    QtCore.QObject.connect(self.ui.radioVersion2,QtCore.SIGNAL("clicked()"), self.setUnpackVersion)

  def updateProgressLog(self, msg):
    '''Add entry to progress log
    '''
    self.ui.infoBox.append(msg)

  def fileOpenDialog(self):
    #print("StartQT4::fileOpenDialog()")
    fd = QtGui.QFileDialog(self)
    self.filename = fd.getOpenFileName(filter='Binary Files *.BIN(*.BIN);;All Files *(*)')
    from os.path import isfile
    if not isfile(self.filename):
      return
    self.db.clearDB()
    getattr(self, self.unpackVersion)()
    #self.lrMax = self.db.getLRFileMax()
    #self.db.getInfo()
    self.updateProgressLog('Load %s' % self.filename)
    self.showFile()
    #self.dumpData()

  def dataNorm(self):
    #print("StartQT4::dataNorm()")
    if self.ui.normCheckBox.checkState():
      self.db.setNormFlag(True)
      fp.leftScale = fp.leftScaleNorm
      fp.rightScale = fp.rightScaleNorm
      fp.swScale = 1024
    else:
      self.db.setNormFlag(False)
      fp.leftScale = 1.0
      fp.rightScale = 1.0
      fp.swScale = 1
    #self.lrMax = self.db.getLRFileMax()
    #self.db.getInfo()
    self.showFile()
    self.updatePlot()

  def setUnpackVersion(self):
    if self.ui.radioVersion1.isChecked():
      self.unpackVersion = 'unpackDataVersion1'
    if self.ui.radioVersion2.isChecked():
      self.unpackVersion = 'unpackDataVersion2'

  def unpackDataVersion1(self):
    fp.leftOff = 0; fp.leftOn = 0
    fp.rightOff = 0; fp.rightOn = 0
    fp.leftScale = 1.0
    fp.rightScale = 1.0
    fp.swScale = 1
    rows = 0
    lmax = 0
    rmax = 0
    upperLimit = 1024
    with open(self.filename, 'rb') as inh:
      fb = inh.read(4)
      while fb:
        d1 = struct.unpack('<L', fb)[0]
        fb = inh.read(4)
        d2 = struct.unpack('<L', fb)[0]
        if (d1 & 0x0FFFF0000) == 0xFFFF0000:
          print('skip')
        else:
          tpoint =   (d2 & 0x00FFFFFF)
          leftSw =   (d2 & 0x40000000) >> 30
          rightSw =  (d2 & 0x80000000) >> 31
          leftPos =  (d1 & 0xFFFF0000) >> 16
          rightPos = (d1 & 0x0000FFFF)
          if leftPos < upperLimit and rightPos < upperLimit:
            if leftPos > lmax:
              lmax = leftPos
            if rightPos > rmax:
              rmax = rightPos
            self.db.addRow([tpoint, leftPos, rightPos, leftSw, rightSw, 0])
            rows += 1
        fb = inh.read(4)
    self.db.fixDataEnd()
    lrMax = self.db.getLRFileMax()
    if lrMax[0] is None:
      fp.leftMaxPedal = 1.0; fp.leftMaxFile = 1.0
    else:
      fp.leftMaxPedal = lrMax[0]; fp.leftMaxFile = lrMax[0]
    if lrMax[1] is None:
      fp.rightMaxPedal = 1.0; fp.rightMaxFile = 1.0
    else:
      fp.rightMaxPedal = lrMax[1]; fp.leftMaxFile = lrMax[1]
    fp.leftScaleNorm = MAXVAL/fp.leftMaxPedal
    fp.rightScaleNorm = MAXVAL/fp.rightMaxPedal
    print(fp.leftMaxPedal, fp.leftOn, fp.leftOff, fp.rightMaxPedal, fp.rightOn, fp.rightOn)
    self.db.addInfo((fp.leftMaxPedal, fp.leftOn, fp.leftOff, fp.rightMaxPedal, fp.rightOn, fp.rightOn))

  def unpackDataVersion2(self):
    #print("StartQT4::unpackData()")
    t1 = 0
    tsec = 0
    upperLimit = 1024
    with open(self.filename, 'rb') as inh:
      fb = inh.read(4)
      version = struct.unpack('<L', fb)[0]
      #print(version)
      fb = inh.read(4)
      lr_max = struct.unpack('<L', fb)[0]
      fp.leftMaxPedal = (lr_max & 0xFFFF0000) >> 16
      fp.rightMaxPedal = (lr_max & 0x0000FFFF)
      fp.leftScaleNorm = MAXVAL/fp.leftMaxPedal
      fp.rightScaleNorm = MAXVAL/fp.rightMaxPedal
      fb = inh.read(4)
      left_th = struct.unpack('<L', fb)[0]
      fp.leftOn = (left_th & 0xFFFF0000) >> 16
      fp.leftOff = (left_th & 0x0000FFFF)
      fb = inh.read(4)
      right_th = struct.unpack('<L', fb)[0]
      fp.rightOn = (right_th & 0xFFFF0000) >> 16
      fp.rightOff = (right_th & 0x0000FFFF)
      fb = inh.read(4)
      while fb:
        d1 = struct.unpack('<L', fb)[0]
        fb = inh.read(4)
        d2 = struct.unpack('<L', fb)[0]
        if (d1 & 0x0FFFF0000) == 0xFFFF0000:
          print('skip')
        else:
          tpoint =   (d2 & 0x00FFFFFF)
          sendKey =  (d2 & 0x20000000) >> 29
          leftSw =   (d2 & 0x40000000) >> 30
          rightSw =  (d2 & 0x80000000) >> 31
          leftPos =  (d1 & 0xFFFF0000) >> 16
          rightPos = (d1 & 0x0000FFFF)
          if leftPos < upperLimit and rightPos < upperLimit:
            self.db.addRow([tpoint, leftPos, rightPos, leftSw, rightSw, sendKey])
        fb = inh.read(4)
    self.db.fixDataEnd()
    print(fp.leftMaxPedal, fp.leftOn, fp.leftOff, fp.rightMaxPedal, fp.rightOn, fp.rightOn)
    self.db.addInfo((fp.leftMaxPedal, fp.leftOn, fp.leftOff, fp.rightMaxPedal, fp.rightOn, fp.rightOn))

  def updateStatus(self):
    self.ui.leftMaxFile.setText("%s" % int(fp.leftMaxFile*fp.leftScale))
    self.ui.rightMaxFile.setText("%s" % int(fp.rightMaxFile*fp.rightScale))
    self.ui.leftMaxPedal.setText("%s" % int(fp.leftMaxPedal*fp.leftScale))
    self.ui.rightMaxPedal.setText("%s" % int(fp.rightMaxPedal*fp.rightScale))
    self.ui.leftOff.setText("%s" % int(fp.leftOff*fp.leftScale))
    self.ui.leftOn.setText("%s" % int(fp.leftOn*fp.leftScale))
    self.ui.rightOff.setText("%s" % int(fp.rightOff*fp.rightScale))
    self.ui.rightOn.setText("%s" % int(fp.rightOn*fp.rightScale))

  def showFile(self):
    #print("StartQT4::showFile()")
    rows = self.db.getData()
    self.updateStatus()
    self.ui.numRowsVal.setText("%s" % len(rows))
    tablemodel = PedTableModel(rows, self)
    self.ui.infoTableView.setModel(tablemodel)

  def dumpData(self):
    #print("StartQT4::dumpData()")
    rows = self.db.getData()
    for row in rows:
      print(hex(row[0]), row[1], row[2])
   
  def fileSaveDialog(self):
    fname = self.filename[:-3] + 'CSV'
    fd = QtGui.QFileDialog(self)
    fname = fd.getSaveFileName(self, "Save CSV", fname)
    rows = self.db.getData()
    with open(fname, 'wb') as csvfile:
      dbswriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
      for row in rows:
        dbswriter.writerow(row)
      
  def updatePlotFlags(self):
    #print('updatePlotFlags()')
    self.pFlags = [False, False, False, False, False]
    if self.ui.checkBoxLP.checkState():
      self.pFlags[0] = True
    if self.ui.checkBoxRP.checkState():
      self.pFlags[1] = True
    if self.ui.checkBoxLS.checkState():
      self.pFlags[2] = True
    if self.ui.checkBoxRS.checkState():
      self.pFlags[3] = True
    if self.ui.checkBoxKbd.checkState():
      self.pFlags[4] = True
    if self.isPlotted == True:
      self.updatePlot()
    
  def updatePlot(self):
    #print('StartQT4::updatePlot()')
    self.plot.removePlotLines()
    if self.pFlags[0] == True:
      self.plot.addPlotline(self.db.getPosition('leftPos', fp.leftScale), 'r')
    if self.pFlags[1] == True:
      self.plot.addPlotline(self.db.getPosition('rightPos', fp.rightScale), 'g')
    if self.pFlags[2] == True:
      self.plot.addPlotline(self.db.getSwitch('leftSw'), 'b')
    if self.pFlags[3] == True:
      self.plot.addPlotline(self.db.getSwitch('rightSw'), 'y')
    if self.pFlags[4] == True:
      self.plot.addPlotline(self.db.getSendKey(), 'w')

  def makePlot(self):
    #print('makePlot()')
    if self.isPlotted == True:
      self.plot.closeWindow()
      self.plot = None
      self.isPlotted = False
      return
    self.plot = footPlots(self.db)
    self.updatePlot()
    self.isPlotted = True

  def analyseBothOne(self):
    tps = self.db.bothOne()
    if len(tps) < 2:
      return
    #start = int([tps[0][0]])
    start = [int(tps[0][0])]
    end = []
    olen = []
    oldval = tps[0]
    #print(oldval[0])
    for tp in tps:
      if tp - oldval > 5:
	end.append(int(oldval[0]))
	olen.append(end[-1] - start[-1])
	start.append(int(tp[0]))
        #print(oldval[0], tp[0])
      oldval = tp
    end.append(int(tps[-1][0]))
    olen.append(end[-1] - start[-1])
    arr = np.array(zip(start, end, olen))
    #print(zip(start, end))
    #self.updateProgressLog('%s' % arr)
    count = len(arr)
    ostart = arr[:,0]
    olen = arr[:,2]
    self.updateProgressLog('%s' % (count))
    self.updateProgressLog('%s' % (zip(ostart, olen)))
      
    
class footPlots:
  def __init__(self, db):
    #self.parent = parent
    self.win = pg.GraphicsLayoutWidget()
    self.win.show()
    self.db = db
    self.plotitems = []
    QtCore.QObject.connect(self.win, QtCore.SIGNAL('triggered()'), self.closeWindow)
    self.win.resize(800,400)
    self.p1 = self.win.addPlot(row=0, col=0)
    #self.p2 = self.win.addPlot(row=1, col=0)

  def addPlotline(self, data, colr):
    p = pg.PlotDataItem(data, pen=colr)
    self.plotitems.append(p)
    self.p1.addItem(p)

  def removePlotLines(self):
    for p in self.plotitems:
      self.p1.removeItem(p)
    self.plotitems = []

  def plotLeft(self):
    data = self.db.getLeftPos()
    p = pg.PlotDataItem(data)
    self.p1.addItem(p)
    #pg.plot(data)

  def plotRight(self):
    p = pg.PlotDataItem(self.db.getRightPos())
    self.p1.addItem(p)

  def closeWindow(self):
    self.win.close()
      
    
class DbData:
  def __init__(self, parent=None):
    self.con = None
    self.cur = None
    self.normalised = False
    self.initDB()
    self.realMax = [0.0,0.0]

  def initDB(self):
    self.con = lite.connect(':memory:')
    #self.con = lite.connect('/tmp/test.db')
    self.cur = self.con.cursor()    
    self.cur.execute("CREATE TABLE fpdata(tp REAL, LeftPos INT, RightPos INT, LeftSw INT, RightSw INT, SendKey INT)")
    self.cur.execute("CREATE TABLE fpinfo(LeftMax INT, LeftOn INT, LeftOff INT, RightMax INT, RightOn INT, RightOff INT)")
    #return cur

  def addRow(self, vals):
    if len(vals) != 6:
      return
    self.cur.execute("INSERT INTO fpdata VALUES(?,?,?,?,?,?)", (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5]))
    self.con.commit()

  def addInfo(self, vals):
    print(vals)
    self.cur.execute("INSERT INTO fpinfo VALUES(?,?,?,?,?,?)", (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5]))

  def commitDb(self):
    self.con.commit()
    
  def fixDataEnd(self):
    # Remove invalid datapoints from end of buffer
    self.cur.execute("SELECT round(max(tp)) from fpdata")
    maxtp = self.cur.fetchall()[0][0]
    self.cur.execute("DELETE FROM fpdata WHERE tp = 0 AND LeftPos = 0 AND RightPos = 0")
    self.con.commit()
    self.realMax = self.getRealFileMax()

  def setNormFlag(self, state):
    self.normalised = state
  
  def clearDB(self):
    self.cur.execute("DELETE FROM fpdata")
    self.con.commit()
  
  #def getAllData(self):
    
  def getLRFileMax(self):
    maxs = [1024,1024]
    if not self.normalised:
      self.cur.execute("SELECT max(leftPos), max(rightPos) from fpdata")
      row = self.cur.fetchall()
      maxs = [row[0][0], row[0][1]]
    return maxs
    
  def getRealFileMax(self):
    self.cur.execute("SELECT max(leftPos), max(rightPos) from fpdata")
    row = self.cur.fetchall()
    return [row[0][0], row[0][1]]
    
  def getData(self):
    #print("DbData::getData()")
    (fp.leftMaxFile, fp.rightMaxFile) = self.getRealFileMax()
    #print self.lrMax
    sql = "SELECT tp, round(leftPos*%f, 1), round(rightPos*%f, 1), leftSw*%d, rightSw*%d, SendKey*%d from fpdata" % (fp.leftScale, fp.leftScale, fp.swScale, fp.swScale, fp.swScale)
    self.cur.execute(sql)
    return self.cur.fetchall()

  def getInfo(self):
    leftScale = fp.leftScale
    rightScale = fp.rightScale
    if self.normalised:
      leftScale = fp.leftScaleNorm
      rightScale = fp.rightScaleNorm
    sql = "SELECT cast(LeftMax*%f as integer), cast(LeftOn*%f as integer), cast(LeftOff*%f as integer), cast(RightMax*%f aS integer),  cast(RightOn*%f as integer), cast(RightOff*%f as integer) FROM fpinfo" % (leftScale, leftScale, leftScale, rightScale, rightScale, rightScale)
    self.cur.execute(sql)
    info = self.cur.fetchall()
      
    fp.leftMax = info[0][0]
    fp.leftOn = info[0][1]
    fp.leftOff = info[0][2]
    fp.rightMax = info[0][3]
    fp.rightOn = info[0][4]
    fp.rightOff = info[0][5]
    #print(info)

  def getPosition(self, side, scale):
    sql = "SELECT tp, round(%s*%f, 1) from fpdata" % (side, scale)
    #print(sql)
    #self.cur.execute("SELECT tp, leftPos, rightPos, leftSw, rightSw, SendKey from fpdata")
    self.cur.execute(sql)
    return(np.array(self.cur.fetchall()))
        
  def getSwitch(self, side):
    sql = "SELECT tp, %s from fpdata" % side
    if self.normalised:
      sql = "SELECT tp, %s*1024 from fpdata" % side
    self.cur.execute(sql)
    return(np.array(self.cur.fetchall()))
   
  def getSendKey(self):
    sql = "SELECT tp, SendKey from fpdata"
    if self.normalised:
      sql = "SELECT tp, SendKey*1024 from fpdata"
    self.cur.execute(sql)
    return(np.array(self.cur.fetchall()))

  def bothOne(self):
    sql = "select tp from fpdata where LeftSw == 1 and RightSw == 1"
    self.cur.execute(sql)
    #tp = self.cur.fetchall()
    #print(tp)
    return(np.array(self.cur.fetchall()))
    
 
class PedTableModel(QtCore.QAbstractTableModel):
  def __init__(self, mylist, parent, *args):
    QtCore.QAbstractTableModel.__init__(self, parent, *args)
    self.mylist = mylist
    self.header = ['Time', 'Left Pos', 'Right Pos', 'Left SW', 'Right SW', 'Send Key']

  def rowCount(self, parent):
    return len(self.mylist)

  def columnCount(self, parent):
    return len(self.mylist[0])

  def data(self, index, role):
    if not index.isValid():
      return None
    elif role != QtCore.Qt.DisplayRole:
      return None
    return self.mylist[index.row()][index.column()]

  def headerData(self, col, orientation, role):
    if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
      return self.header[col]
    return None

  def sort(self, col, order):
    """sort table by given column number col"""
    self.emit(SIGNAL("layoutAboutToBeChanged()"))
    self.mylist = sorted(self.mylist,
    key=operator.itemgetter(col))
    if order == QtCore.Qt.DescendingOrder:
      self.mylist.reverse()
    self.emit(SIGNAL("layoutChanged()"))


def main():
    #con = lite.connect('test.db')
    app = QtGui.QApplication(sys.argv)
    ex = StartQT4()
    ex.show()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()
    pass
