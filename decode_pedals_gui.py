# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'decode_pedals_gui.ui'
#
# Created: Tue Jan 14 08:41:49 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_decodePedals(object):
    def setupUi(self, decodePedals):
        decodePedals.setObjectName(_fromUtf8("decodePedals"))
        decodePedals.resize(743, 452)
        self.centralwidget = QtGui.QWidget(decodePedals)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.buttonOpen = QtGui.QPushButton(self.centralwidget)
        self.buttonOpen.setGeometry(QtCore.QRect(0, 2, 81, 24))
        self.buttonOpen.setObjectName(_fromUtf8("buttonOpen"))
        self.buttonExit = QtGui.QPushButton(self.centralwidget)
        self.buttonExit.setGeometry(QtCore.QRect(0, 58, 81, 24))
        self.buttonExit.setObjectName(_fromUtf8("buttonExit"))
        self.buttonSave = QtGui.QPushButton(self.centralwidget)
        self.buttonSave.setGeometry(QtCore.QRect(0, 30, 81, 24))
        self.buttonSave.setObjectName(_fromUtf8("buttonSave"))
        self.normCheckBox = QtGui.QCheckBox(self.centralwidget)
        self.normCheckBox.setGeometry(QtCore.QRect(0, 390, 111, 21))
        self.normCheckBox.setObjectName(_fromUtf8("normCheckBox"))
        self.infoTableView = QtGui.QTableView(self.centralwidget)
        self.infoTableView.setGeometry(QtCore.QRect(160, 0, 571, 421))
        self.infoTableView.setObjectName(_fromUtf8("infoTableView"))
        self.maxLeft = QtGui.QTextBrowser(self.centralwidget)
        self.maxLeft.setGeometry(QtCore.QRect(0, 120, 51, 31))
        self.maxLeft.setObjectName(_fromUtf8("maxLeft"))
        self.maxRight = QtGui.QTextBrowser(self.centralwidget)
        self.maxRight.setGeometry(QtCore.QRect(70, 120, 51, 31))
        self.maxRight.setObjectName(_fromUtf8("maxRight"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 100, 41, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 100, 51, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.numberOfRows = QtGui.QTextBrowser(self.centralwidget)
        self.numberOfRows.setGeometry(QtCore.QRect(0, 180, 81, 31))
        self.numberOfRows.setObjectName(_fromUtf8("numberOfRows"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 160, 41, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.buttonPlot = QtGui.QPushButton(self.centralwidget)
        self.buttonPlot.setGeometry(QtCore.QRect(100, 280, 51, 24))
        self.buttonPlot.setObjectName(_fromUtf8("buttonPlot"))
        self.checkBoxLP = QtGui.QCheckBox(self.centralwidget)
        self.checkBoxLP.setGeometry(QtCore.QRect(10, 250, 81, 21))
        self.checkBoxLP.setObjectName(_fromUtf8("checkBoxLP"))
        self.checkBoxRP = QtGui.QCheckBox(self.centralwidget)
        self.checkBoxRP.setGeometry(QtCore.QRect(10, 270, 81, 21))
        self.checkBoxRP.setObjectName(_fromUtf8("checkBoxRP"))
        self.checkBoxLS = QtGui.QCheckBox(self.centralwidget)
        self.checkBoxLS.setGeometry(QtCore.QRect(10, 290, 81, 21))
        self.checkBoxLS.setObjectName(_fromUtf8("checkBoxLS"))
        self.checkBoxRS = QtGui.QCheckBox(self.centralwidget)
        self.checkBoxRS.setGeometry(QtCore.QRect(10, 310, 81, 21))
        self.checkBoxRS.setObjectName(_fromUtf8("checkBoxRS"))
        decodePedals.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(decodePedals)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 743, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        decodePedals.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(decodePedals)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        decodePedals.setStatusBar(self.statusbar)

        self.retranslateUi(decodePedals)
        QtCore.QObject.connect(self.buttonExit, QtCore.SIGNAL(_fromUtf8("clicked()")), decodePedals.close)
        QtCore.QMetaObject.connectSlotsByName(decodePedals)

    def retranslateUi(self, decodePedals):
        decodePedals.setWindowTitle(_translate("decodePedals", "MainWindow", None))
        self.buttonOpen.setText(_translate("decodePedals", "Open", None))
        self.buttonExit.setText(_translate("decodePedals", "Close", None))
        self.buttonSave.setText(_translate("decodePedals", "Save", None))
        self.normCheckBox.setToolTip(_translate("decodePedals", "<html><head/><body><p>Set maximums to 100</p></body></html>", None))
        self.normCheckBox.setText(_translate("decodePedals", "Normalise", None))
        self.label.setText(_translate("decodePedals", "L Max", None))
        self.label_2.setText(_translate("decodePedals", "R Max", None))
        self.label_3.setText(_translate("decodePedals", "Rows", None))
        self.buttonPlot.setText(_translate("decodePedals", "Plot", None))
        self.checkBoxLP.setText(_translate("decodePedals", "Left Pos", None))
        self.checkBoxRP.setText(_translate("decodePedals", "Right Pos", None))
        self.checkBoxLS.setText(_translate("decodePedals", "Left Sw", None))
        self.checkBoxRS.setText(_translate("decodePedals", "Right Sw", None))

