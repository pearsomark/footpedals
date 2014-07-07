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
        self.con = None
        self.cur = None
        self.filename = None
        self.initDB()
        self.lrMax = [0,0]
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_decodePedals()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.buttonOpen,QtCore.SIGNAL("clicked()"), self.fileOpenDialog)
        QtCore.QObject.connect(self.ui.buttonSave,QtCore.SIGNAL("clicked()"), self.fileSaveDialog)
        QtCore.QObject.connect(self.ui.normCheckBox,QtCore.SIGNAL("clicked()"), self.showFile)
        
    def fileOpenDialog(self):
      fd = QtGui.QFileDialog(self)
      self.filename = fd.getOpenFileName(filter='Binary Files *.BIN(*.BIN);;All Files *(*)')
      from os.path import isfile
      if not isfile(self.filename):
        return
      self.clearDB()
      self.unpackData()
      self.lrMax = self.getLRMax()
      self.showFile()

    def unpackData(self):
        t1 = 0
        tsec = 0
        upperLimit = 1024
        with open(self.filename, 'rb') as inh:
          fb = inh.read(8)
          while fb:
            d1 = struct.unpack('<L', fb)[0]
            d2 = struct.unpack('<L', fb)[4]
            tpoint =   (d2 & 0x00FFFFFF)
            leftSw =   (d2 & 0x40000000) >> 14
            rightSw =  (d2 & 0x80000000) >> 15
            leftPos =  (d1 & 0xFFFF0000) >> 16
            rightPos = (d1 & 0x0000FFFF)
            if leftPos < upperLimit and rightPos < upperLimit:
              t1 = tp
              self.cur.execute("INSERT INTO fpdata VALUES(?,?,?,?,?)", (tpoint, leftPos, rightPos, leftSw, rightSw))
            fb = inh.read(4)
        self.con.commit()
        # Remove invalid datapoints from end of buffer
        self.cur.execute("SELECT round(max(tp)) from fpdata")
        maxtp = self.cur.fetchall()[0][0]
        self.cur.execute("DELETE FROM fpdata WHERE tp = %s AND LeftPos = 0 AND RightPos = 0" % maxtp)
        self.con.commit()
      
    def showFile(self):
        #print "%s records inserted" % records
        rows = self.getData()
        self.ui.maxLeft.setText("%s" % self.lrMax[0])
        self.ui.maxRight.setText("%s" % self.lrMax[1])
        self.ui.numberOfRows.setText("%s" % len(rows))
        tablemodel = MyTableModel(rows, self)
        self.ui.infoTableView.setModel(tablemodel)

        #if self.con:
            #self.con.close() 
     
    def fileSaveDialog(self):
        fname = self.filename[:-3] + 'CSV'
        fd = QtGui.QFileDialog(self)
        fname = fd.getSaveFileName(self, "Save CSV", fname)
        rows = self.getData()
	with open(fname, 'wb') as csvfile:
	  dbswriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	  for row in rows:
	    dbswriter.writerow(row)
       
    def initDB(self):
        self.con = lite.connect(':memory:')
        #self.con = lite.connect('test.db')
        self.cur = self.con.cursor()    
        self.cur.execute("CREATE TABLE fpdata(tp REAL, LeftPos INT, RightPos INT, LeftSw INT, RightSw INT)")
        #return cur

    def clearDB(self):
        self.cur.execute("DELETE FROM fpdata")
        self.con.commit()
      
    def getLRMax(self):
        self.cur.execute("SELECT max(leftPos), max(rightPos) from fpdata")
        row = self.cur.fetchall()
        return [row[0][0], row[0][1]]
      
    def getData(self):
      self.lrMax = self.getLRMax()
      if self.ui.normCheckBox.checkState():
	  self.cur.execute("SELECT tp, round(leftPos*(100.0/%f), 1), round(rightPos*(100.0/%f), 1), leftSw*100, rightSw*100 from fpdata"
	    % (self.lrMax[0], self.lrMax[1]))
          self.lrMax = [100,100]
      else:
	  self.cur.execute("SELECT tp, leftPos, rightPos, leftSw, rightSw from fpdata")
      return self.cur.fetchall()
    
    def plotLeft(self):
      cur.execute("SELECT tp, leftPos from fpdata")
      data = np.array(cur.fetchall())
      pg.plot(data)
 
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
