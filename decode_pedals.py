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

class StartQT4(QtGui.QMainWindow):
  def __init__(self, parent=None):
    self.filename = None
    self.db = DbData()
    self.isPlotted = False
    self.lrMax = [0,0]
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_decodePedals()
    self.ui.setupUi(self)
    self.ui.maxLeftVal.setText("%s" % self.lrMax[0])
    self.ui.maxRightVal.setText("%s" % self.lrMax[1])
    self.ui.numRowsVal.setText("0")
    self.pFlags = [False, False, False, False]
    
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
      
  def fileOpenDialog(self):
    fd = QtGui.QFileDialog(self)
    self.filename = fd.getOpenFileName(filter='Binary Files *.BIN(*.BIN);;All Files *(*)')
    from os.path import isfile
    if not isfile(self.filename):
      return
    self.db.clearDB()
    self.unpackData()
    self.lrMax = self.db.getLRMax()
    self.showFile()
    #self.dumpData()

  def dataNorm(self):
    print("dataNorm")
    if self.ui.normCheckBox.checkState():
      self.db.setNormFlag(True)
    else:
      self.db.setNormFlag(False)
    self.lrMax = self.db.getLRMax()
    self.showFile()
    
  def unpackData(self):
    t1 = 0
    tsec = 0
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
            self.db.addRow([tpoint, leftPos, rightPos, leftSw, rightSw])
        fb = inh.read(4)
    self.db.fixDataEnd()
    
  def showFile(self):
    print("showFile")
    #print "%s records inserted" % records
    rows = self.db.getData()
    self.ui.maxLeftVal.setText("%s" % self.lrMax[0])
    self.ui.maxRightVal.setText("%s" % self.lrMax[1])
    self.ui.numRowsVal.setText("%s" % len(rows))
    tablemodel = MyTableModel(rows, self)
    self.ui.infoTableView.setModel(tablemodel)

  def dumpData(self):
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
    self.pFlags = [False, False, False, False]
    if self.ui.checkBoxLP.checkState():
      self.pFlags[0] = True
    if self.ui.checkBoxRP.checkState():
      self.pFlags[1] = True
    if self.ui.checkBoxLS.checkState():
      self.pFlags[2] = True
    if self.ui.checkBoxRS.checkState():
      self.pFlags[3] = True
    if self.isPlotted == True:
      self.updatePlot()
    
  def updatePlot(self):
    print('updatePlot()')
    if self.pFlags[0] == True:
      self.plot.addPlotline(self.db.getPosition('leftPos'), 'r')
    if self.pFlags[1] == True:
      self.plot.addPlotline(self.db.getPosition('rightPos'), 'g')
    if self.pFlags[2] == True:
      self.plot.addPlotline(self.db.getSwitch('leftSw'), 'b')
    if self.pFlags[3] == True:
      self.plot.addPlotline(self.db.getSwitch('rightSw'), 'y')

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
    
class footPlots:
  def __init__(self, db):
    #self.parent = parent
    self.win = pg.GraphicsLayoutWidget()
    self.win.show()
    self.db = db
    QtCore.QObject.connect(self.win, QtCore.SIGNAL('triggered()'), self.closeWindow)
    self.win.resize(800,400)
    self.p1 = self.win.addPlot(row=0, col=0)
    #self.p2 = self.win.addPlot(row=1, col=0)

  def addPlotline(self, data, colr):
    p = pg.PlotDataItem(data, pen=colr)
    self.p1.addItem(p)
      
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
    self.cur.execute("CREATE TABLE fpdata(tp REAL, LeftPos INT, RightPos INT, LeftSw INT, RightSw INT)")
    #return cur

  def addRow(self, vals):
    if len(vals) != 5:
      return
    self.cur.execute("INSERT INTO fpdata VALUES(?,?,?,?,?)", (vals[0], vals[1], vals[2], vals[3], vals[4]))
    self.con.commit()

  def commitDb(self):
    self.con.commit()
    
  def fixDataEnd(self):
    # Remove invalid datapoints from end of buffer
    self.cur.execute("SELECT round(max(tp)) from fpdata")
    maxtp = self.cur.fetchall()[0][0]
    self.cur.execute("DELETE FROM fpdata WHERE tp = 0 AND LeftPos = 0 AND RightPos = 0")
    self.con.commit()
    self.realMax = self.getRealMax()

  def setNormFlag(self, state):
    self.normalised = state
  
  def clearDB(self):
    self.cur.execute("DELETE FROM fpdata")
    self.con.commit()
  
  #def getAllData(self):
    
  def getLRMax(self):
    maxs = [1024,1024]
    if not self.normalised:
      self.cur.execute("SELECT max(leftPos), max(rightPos) from fpdata")
      row = self.cur.fetchall()
      maxs = [row[0][0], row[0][1]]
    return maxs
    
  def getRealMax(self):
    self.cur.execute("SELECT max(leftPos), max(rightPos) from fpdata")
    row = self.cur.fetchall()
    return [row[0][0], row[0][1]]
    
  def getData(self):
    print("getData")
    self.lrMax = self.getLRMax()
    print self.lrMax
    if self.normalised:
      print("SELECT tp, round(leftPos*(1024.0/%f), 1), round(rightPos*(1024.0/%f), 1), leftSw*1024, rightSw*1024 from fpdata" % (self.lrMax[0], self.lrMax[1]))
      self.cur.execute("SELECT tp, round(leftPos*(1024.0/%f), 1), round(rightPos*(1024.0/%f), 1), leftSw*1024, rightSw*1024 from fpdata"
        % (self.lrMax[0], self.lrMax[1]))
      self.lrMax = [1024,1024]
    else:
      self.cur.execute("SELECT tp, leftPos, rightPos, leftSw, rightSw from fpdata")
    return self.cur.fetchall()

  def getPosition(self, side):
    sql = "SELECT tp, %s from fpdata" % side
    if self.normalised:
      sql = "SELECT tp, round(%s*(1024.0/%f), 1) from fpdata" % (side, self.realMax[1])
    self.cur.execute(sql)
    return(np.array(self.cur.fetchall()))
        
  def getSwitch(self, side):
    sql = "SELECT tp, %s from fpdata" % side
    if self.normalised:
      sql = "SELECT tp, %s*1024 from fpdata" % side
    self.cur.execute(sql)
    return(np.array(self.cur.fetchall()))
   
    
 
class MyTableModel(QtCore.QAbstractTableModel):
  header_labels = ['Time', 'Left Pos', 'Right Pos', 'Left SW', 'Right SW']
  def __init__(self, datain, parent=None, *args):
      QtCore.QAbstractTableModel.__init__(self, parent, *args)
      self.arraydata = datain

  def rowCount(self, parent):
      return len(self.arraydata)

  def columnCount(self, parent):
      return len(self.arraydata[0])

  def data(self, index, role):
      if not index.isValid():
          return QtCore.QVariant()
      elif role != QtCore.Qt.DisplayRole:
          return QtCore.QVariant()
      return QtCore.QVariant(self.arraydata[index.row()][index.column()])

  def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
    if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
      return self.header_labels[section]
    return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)


def main():
    #con = lite.connect('test.db')
    app = QtGui.QApplication(sys.argv)
    ex = StartQT4()
    ex.show()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()
    pass
