# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qres
                                 A QGIS plugin
 A Simple Plugin For Vertical electrical Sounding
                              -------------------
        begin                : 2015-10-29
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Halil BÖLÜK / Akdeniz University
        email                : halilboluk@akdeniz.edu.tr
 ***************************************************************************/

/***************************************************************************
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
# Initialize Qt resources from file resources.py
import resources
from qgis.gui import *
from qgis.core import *
from qgis.gui import QgsMessageBar
# Import the code for the DockWidget
from qres_dockwidget import qresDockWidget
import os.path
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline
from scipy.interpolate import Rbf
class qres:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'qres_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QRES')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'qres')
        self.toolbar.setObjectName(u'qres')

        #print "** INITIALIZING qres"
        
        self.pluginIsActive = False
        self.dockwidget = None



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('qres', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/qres/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'QRES'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING qres"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        #print "** UNLOAD qres"
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&QRES'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

#---------


    def layer_ekle(self):
        text, ok = QInputDialog.getText(QInputDialog(),'QRes Bilgi Girisi','DES  icin katman adi giriniz:: ',QLineEdit.Normal,'DES')
        # create layer for overview line


        vl2 = QgsVectorLayer("Point",text + "_data", "memory")
        pr2 = vl2.dataProvider()
        vl2.startEditing()
        vl2.addAttribute(QgsField("des_ad", QVariant.String))
        vl2.addAttribute(QgsField("ab2", QVariant.Double))
        vl2.addAttribute(QgsField("mn2", QVariant.Double))
        vl2.addAttribute(QgsField("k", QVariant.Double))
        vl2.addAttribute(QgsField("sp", QVariant.Double))
        vl2.addAttribute(QgsField("v", QVariant.Double))
        vl2.addAttribute(QgsField("vt", QVariant.Double))
        vl2.addAttribute(QgsField("i", QVariant.Double))
        vl2.addAttribute(QgsField("ra", QVariant.Double))
        vl2.updateFields()
        vl2.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(vl2)

        vl = QgsVectorLayer("Point",text, "memory")
        pr = vl.dataProvider()
        vl.startEditing()
        vl.addAttribute(QgsField("ad", QVariant.String))
        vl.addAttribute(QgsField("z", QVariant.Double))
        vl.addAttribute(QgsField("tarih", QVariant.String))
        vl.updateFields()
        vl.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(vl)


        self.layer_liste()

    def des_liste(self):
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dockwidget.cmbLayer.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        des_list = []
        print selectedLayer.name()
        for f in selectedLayer.getFeatures():
            des_list.append(f['ad'])
        self.dockwidget.cmbDesOut.clear()
        self.dockwidget.cmbDesIn.clear()
        self.dockwidget.cmbDES.clear()
        self.dockwidget.cmbDesGrafik.clear()
        self.dockwidget.cmbDesOut.addItems(des_list)
        self.dockwidget.cmbDES.addItems(des_list)
        self.dockwidget.cmbDesIn.addItems(des_list)
        self.dockwidget.cmbDesGrafik.addItems(des_list)

    def des_ekle(self):
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dockwidget.cmbLayer.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        print selectedLayer.name()
        fet = QgsFeature()
        xx = self.dockwidget.txtX.text()
        yy = self.dockwidget.txtY.text()
        zz = self.dockwidget.txtZ.text()
        desName = self.dockwidget.txtDES.text()
        tarih = self.dockwidget.txtTarih.text()
        self.dockwidget.txtX.clear()
        self.dockwidget.txtY.clear()
        self.dockwidget.txtZ.clear()
        self.dockwidget.txtDES.clear()
        self.dockwidget.txtTarih.clear()
        fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(xx),float(yy))))
        fet.setAttributes([desName,zz,tarih])
        pr = selectedLayer.dataProvider()
        pr.addFeatures([fet])
        selectedLayer.updateExtents()

    def olcum_ekle(self):
        ab2 = self.dockwidget.txtAB2.text()
        mn2 = self.dockwidget.txtMN2.text()
        k = self.dockwidget.txtK.text()
        ra = self.dockwidget.txtRa.text()
        sp = self.dockwidget.txtSP.text()
        i = self.dockwidget.txtI.text()
        v = self.dockwidget.txtV.text()
        vt = self.dockwidget.txtVT.text()
        des_ad = unicode(self.dockwidget.cmbDES.currentText())
        print des_ad
        self.dockwidget.txtAB2.clear()
        self.dockwidget.txtMN2.clear()
        self.dockwidget.txtK.clear()
        self.dockwidget.txtRa.clear()
        self.dockwidget.txtI.clear()
        self.dockwidget.txtV.clear()
        self.dockwidget.txtVT.clear()
        self.dockwidget.txtSP.clear()
        cur_layer = self.dockwidget.cmbLayer.currentText()
        print cur_layer

        layers = self.iface.legendInterface().layers()
        mainLayerIndex = self.dockwidget.cmbLayer.currentIndex()
        mainLayer= layers[mainLayerIndex]

        for f in mainLayer.getFeatures():
            if f['ad'] == des_ad:
                geom = f.geometry()
        print geom.asPoint()
        for ly in layers:
            if ly.name() == cur_layer + "_data":
                selectedLayer = ly
        fet = QgsFeature()
        fet.setGeometry(geom)
        fet.setAttributes([des_ad,ab2,mn2,k,sp,v,vt,i,ra])
        pr = selectedLayer.dataProvider()
        pr.addFeatures([fet])
        selectedLayer.updateExtents()
        print selectedLayer.name()

    def layer_liste(self):
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dockwidget.cmbLayer.clear()
        self.dockwidget.cmbLayer.addItems(layer_list)

    def des_hesapla(self):
         self.dockwidget.txtVT.setText(str(abs(float( self.dockwidget.txtV.text()) - float( self.dockwidget.txtSP.text()))))
         self.dockwidget.txtRa.setText(str(abs(float( self.dockwidget.txtK.text()) * float( self.dockwidget.txtVT.text()) / float( self.dockwidget.txtI.text()))))

    def k_hesapla(self):
        ab = float(self.dockwidget.txtAB2.text())*2
        mn = float(self.dockwidget.txtMN2.text())*2
        sonuc = ab*ab - mn*mn
        sonuc = sonuc / (4 * mn)
        sonuc = sonuc * math.pi
        self.dockwidget.txtK.setText(str(sonuc))

    def r1d_disari_aktar(self):
        des_ad = unicode(self.dockwidget.cmbDES.currentText())
        dosya_adi = des_ad + ".dat"
        print dosya_adi
        filename = QFileDialog.getSaveFileName(self.dockwidget,"Kaydetmek icin dosya secin", dosya_adi, ".dat")
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dockwidget.cmbLayer.currentIndex()
        cur_layer = layers[selectedLayerIndex]


        for ly in layers:
            if ly.name() == cur_layer.name() + "_data":
                selectedLayer = ly
        bas = des_ad + '\n'
        bas = bas + 'Array Type (Wenner or Schlumbeger)' + '\n'
        bas = bas + 'Schlumberger' + '\n'
        bas = bas + 'Number of data points' + '\n'
        say = 0
        line=""
        for f in selectedLayer.getFeatures():
            if f['des_ad'] == des_ad:
                a= float(f['ab2'])
                b= float(f['mn2'])*2
                ohm = float(f['ra'])
                line = line + str(a) + '\t' + str(b) + '\t' + str(ohm) + '\n'
                say = say + 1
        bas = bas + str(say) + '\n'
        bas = bas + 'Data Type (Resistivity,IP,SIP)' + '\n'
        bas = bas + 'Resistivity' + '\n'
        bas = bas + 'Error in measurements included (Yes,No)' + '\n'
        bas = bas + 'No' + '\n'
        bas = bas + 'Data section' + '\n'
        bas = bas + line
        bas = bas + 'User Starting Model Available (Yes/No)' + '\n'
        bas = bas + 'No' + '\n'
        bas = bas + 'Fix Parameters (Yes/No)' + '\n'
        bas = bas + 'No'
        veri = unicode(bas)
        yaz = open(filename , 'w')
        yaz.write(veri)
        yaz.close()

    def ipi2Win_disari_aktar(self):
        des_ad = unicode(self.dockwidget.cmbDES.currentText())
        dosya_adi = des_ad + ".TXT"
        print dosya_adi
        filename = QFileDialog.getSaveFileName(self.dockwidget,"Kaydetmek icin dosya secin", dosya_adi, ".TXT")
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dockwidget.cmbLayer.currentIndex()
        cur_layer = layers[selectedLayerIndex]

        for ly in layers:
            if ly.name() == cur_layer.name() + "_data":
                selectedLayer = ly
        yaz = open(filename , 'w')
        line= 'AB/2' + '\t' + 'MN' + '\t' + 'Ro_a' + '\r\n'
        yaz.write(unicode(line))
        yaz.close()
        yaz = open(filename , 'a')
        for f in selectedLayer.getFeatures():
            if f['des_ad'] == des_ad:
                a= float(f['ab2'])
                b= float(f['mn2'])*2
                ohm = float(f['ra'])
                line = str(a) + '\t' + str(b) + '\t' + str(ohm) + '\r\n'
                yaz.write(line)
        yaz.close()


    def r1d_Iceri_aktar(self):
        filename = QFileDialog.getOpenFileName(self.dockwidget,"Açmak icin dosya secin", '/', '*.INV')
        f = open(filename, 'r')
        readData = f.readlines()
        
        say = 0
        inv_rev_list = []
        inv_rev=[]

        for l in reversed(readData):
            if l[:4] == "Data":
                break
            cleaned_data = l.replace('    ', ';').strip().replace(' ', '')
            splitted_data = cleaned_data.split(',')
            say = say + 1
            if say > 2:
                inv_rev_list.append(cleaned_data)
                splitted_data
        f.close()
        inv_list = reversed(inv_rev_list)


        durum = 'yok'
        layers = self.iface.legendInterface().layers()
        mainLayerName = self.dockwidget.cmbLayer.currentText()
        
        des_ad = self.dockwidget.cmbDesIn.currentText()
        
        for ly in layers:
            if ly.name() == mainLayerName:
                dataLayer = ly
            if ly.name() == 'r1d_in_data':
                vl2 = ly
                durum ='var'

        geom =  QgsGeometry()
        for f in dataLayer.getFeatures():
            if f['ad'] == des_ad:
                geom = f.geometry()
                break

        if durum == 'yok':
            crs = dataLayer.crs().authid()
            text = "r1d_in"
            vl2 = QgsVectorLayer("Point?crs=" + crs, text + "_data", "memory")
            pr2 = vl2.dataProvider()
            vl2.startEditing()
            vl2.addAttribute(QgsField("des_ad", QVariant.String))
            vl2.addAttribute(QgsField("ab2", QVariant.Double))
            vl2.addAttribute(QgsField("mn", QVariant.Double))
            vl2.addAttribute(QgsField("ra", QVariant.Double))
            vl2.updateFields()
            vl2.commitChanges()
            QgsMapLayerRegistry.instance().addMapLayer(vl2)

        fets=[]

        for d in inv_list:
            fet = QgsFeature(vl2.pendingFields())
            sp = d.split(';')
            des='des'
            ab2 = float(sp[1])
            mn = float(sp[2])
            ra = float(sp[3])
            fet.setAttributes([des_ad,ab2,mn,ra])
            fet.setGeometry(geom)
            fets.append(fet)
        print des_ad + 'added'

        vl2.dataProvider().addFeatures(fets)
        vl2.updateExtents()
    def ipi2win_in(self):
        QMessageBox.about(self.dockwidget, "UYARI", "BU FONKSIYON HENUZ EKLENMEDI")
    def getGPS(self):
            QMessageBox.warning(self.dockwidget, "UYARI", "BU FONKSIYON DENEME ASAMASINDA")
    def des_grafik(self):
        layers = self.iface.legendInterface().layers()
        des_ad = self.dockwidget.cmbDesGrafik.currentText()

        for ly in layers:
            if ly.name() == 'r1d_in_data':
                vl2 = ly



        xx=[]
        yy=[]
        for f in vl2.getFeatures():
            if f['des_ad'] == des_ad:
                xx.append(f['ab2'])
                yy.append(f['ra'])


        # make up some data in the interval ]0, 1[
        # plot with various axes scales
        plt.figure(1)
        x =  np.array(xx)
        y =  np.array(yy)

        xnew = np.linspace(x.min(),x.max(),1000000)
        power_smooth = spline(x,y,xnew)
        plt.plot(x,y, 'bo', xnew,power_smooth,'r')
        plt.axis([25, 4000, 1, 1000])
        plt.yscale('log')
        plt.xscale('log')

        plt.title('DES - ' + des_ad)
        plt.ylabel(unicode('Gorunur Ozdirenc (Ohm.m)'))
        plt.xlabel(unicode('AB/2 (metre)'))
        plt.grid(True, which='both')
        plt.show()

    def coRes(self):
        layers = self.iface.legendInterface().layers()
        for ly in layers:
            if ly.name() == 'r1d_in_data':
                vl2 = ly
        print vl2.name()
        x=[]
        y=[]
        values =[]
        ab = self.dockwidget.txtAB2CoRes.text()
        print ab

        for f in vl2.getFeatures():
            #print f['ab2']
            if f['ab2'] == float(ab):
                geom = f.geometry()
                x.append(geom.asPoint().x())
                y.append(geom.asPoint().y())
                values.append(f['ra'])

        #Creating the output grid (100x100, in the example)
        #x = [10,60,40,70,10,50,20,70,30,60]
        #y = [10,20,30,30,40,50,60,70,80,90]
        #values = [1,2,2,3,4,6,7,7,8,10]
        print x
        print y
        #print xx

        txi = np.linspace(min(x), max(x), 10000)
        tyi = np.linspace(min(y), max(y), 10000)
        XI, YI = np.meshgrid(ti, ti)

        #Creating the interpolation function and populating the output matrix value
        rbf = Rbf(x, y, values, function='inverse')
        ZI = rbf(XI, YI)

        # Plotting the result
        n = plt.normalize(0.0, 1000.0)
        plt.subplot(1, 1, 1)
        plt.pcolor(XI, YI, ZI)
        plt.scatter(x, y, 1000, values)
        plt.title('RBF interpolation')
        plt.xlim(min(x), max(x))
        plt.ylim(min(y), max(y))
        plt.colorbar()

        plt.show()


    def run(self):
        """Run method that loads and starts the plugin"""
        if not self.pluginIsActive:
            self.pluginIsActive = True
            #print "** STARTING qres"
            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = qresDockWidget()
            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
           
            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            self.dockwidget.btnAddLayer.clicked.connect(self.layer_ekle)
            self.dockwidget.btnDesGuncelle.clicked.connect(self.des_liste)
            self.dockwidget.btnDesGuncelle2.clicked.connect(self.des_liste)
            self.dockwidget.btnDesGuncelle3.clicked.connect(self.des_liste)
            self.dockwidget.btnDesGuncelle4.clicked.connect(self.des_liste)
            self.dockwidget.btnDesEkle.clicked.connect(self.des_ekle)
            self.dockwidget.btnOlcumEkle.clicked.connect(self.olcum_ekle)
            self.dockwidget.txtV.editingFinished.connect(self.des_hesapla)
            self.dockwidget.txtMN2.editingFinished.connect(self.k_hesapla)
            self.dockwidget.btnR1dOut.clicked.connect(self.r1d_disari_aktar)
            self.dockwidget.btnR1dIn.clicked.connect(self.r1d_Iceri_aktar)
            self.dockwidget.btnIPIOut.clicked.connect(self.ipi2Win_disari_aktar)
            self.dockwidget.btnIPIIn.clicked.connect(self.ipi2win_in)
            self.dockwidget.btnGPS.clicked.connect(self.getGPS)
            self.dockwidget.btnDesGrafik.clicked.connect(self.des_grafik)
            self.dockwidget.btnCoResMap.clicked.connect(self.coRes)
            self.layer_liste()
#--------------------------------------------------------------------------


