# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qres
                                 A QGIS plugin
 A Simple Plugin For Vertical electrical Sounding
                             -------------------
        begin                : 2015-10-29
        copyright            : (C) 2015 by Halil BÖLÜK / Akdeniz University
        email                : halilboluk@akdeniz.edu.tr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load qres class from file qres.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qres import qres
    return qres(iface)
