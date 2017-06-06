# -*- coding: utf-8 -*-
# © <2015> <Miguel Chuga>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Reportes de ventas",
    "summary": "Genera los repotes de ventas en un xls",
    "version": "8.0.1.0.0",
    "category": "Report",
    "website": "https://mcsistemas.net",
    "author": "Miguel Chuga,"
              "MC-Sistemas",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        'report/generate_ventas_wizard.xml',
        'report/generate_facturas_wizard.xml',
        'report/generate_detalle_clientes_wizard.xml',
        'report/generate_recibos_wizard.xml',

    ],
    "demo": [
    ],
}
