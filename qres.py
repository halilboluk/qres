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
    def des_liste(self):
        des_layer = self.dockwidget.cmbLayer,"",{"hasGeometry": True}

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
        self.dockwidget.cmbDES.clear()
        self.dockwidget.cmbDesOut.addItems(des_list)
        self.dockwidget.cmbDES.addItems(des_list)

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
            self.dockwidget.btnDesEkle.clicked.connect(self.des_ekle)
            self.dockwidget.btnOlcumEkle.clicked.connect(self.olcum_ekle)
            self.dockwidget.txtV.editingFinished.connect(self.des_hesapla)
            self.dockwidget.txtMN2.editingFinished.connect(self.k_hesapla)
            self.layer_liste()
#--------------------------------------------------------------------------


