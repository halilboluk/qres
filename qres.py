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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QInputDialog, QLineEdit
from PyQt4.QtCore import * 
from PyQt4.QtCore import QVariant,  QDir
# Initialize Qt resources from file resources.py
import resources
from qgis.gui import *
from qgis.core import *
from qgis.gui import QgsMessageBar
# Import the code for the DockWidget
from qres_dockwidget import qresDockWidget
import os.path


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

    def layerEkle(self):
        vl = QgsVectorLayer("Point", "temporary_points", "memory")
        pr = vl.dataProvider()
        vl.startEditing()
        pr.addAttributes( [ QgsField("name", QVariant.String),
                QgsField("age",  QVariant.Int),
                QgsField("size", QVariant.Double) ] )
        fet = QgsFeature()
        fet.setGeometry( QgsGeometry.fromPoint(QgsPoint(10,10)) )
        fet.setAttributeMap( { 0 : QVariant("Johny"),
                   1 : QVariant(20),
                   2 : QVariant(0.3) } )
        pr.addFeatures( [ fet ] )
        vl.commitChanges()
    #--------------------------------------------------------------------------
    def layer_ekle(self):
        # create layer for overview line
        text, ok = QtGui.QInputDialog.getText(self, "QInputDialog.getText()",
                "User name:", QtGui.QLineEdit.Normal,
                QtCore.QDir.home().dirName())
        vl = QgsVectorLayer("Point",report_title, "memory")
        self.dockwidget.txtKatmanAdi.setText("")
        pr = vl.dataProvider()
        vl.startEditing()
        vl.addAttribute(QgsField("id", QVariant.Int))
        vl.addAttribute(QgsField("x", QVariant.Double))
        vl.updateFields()
        vl.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(vl)

       
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
#--------------------------------------------------------------------------

	

