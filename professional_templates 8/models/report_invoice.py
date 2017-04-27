# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
#This software and associated files (the "Software") may only be used (executed,
#modified, executed after modifications) if you have purchased a valid license
#from the authors, typically via Odoo Apps, or if you have received a written
#agreement from the authors of the Software (see the COPYRIGHT section below).
#
#You may develop Odoo modules that use the Software as a library (typically
#by depending on it, importing it and using its resources), but without copying
#any source code or material from the Software. You may distribute those
#modules under the license of your choice, provided that this license is
#compatible with the terms of the Odoo Proprietary License (For example:
#LGPL, MIT, or proprietary licenses similar to this one).
#
#It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#or modified copies of the Software.
#
#The above copyright notice and this permission notice must be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2016 Bernard K Too<bernard.too@optima.co.ke>

import time
from datetime import datetime
from openerp.osv import osv
from openerp.report import report_sxw
import logging
_logger = logging.getLogger(__name__)

class invoice_lines_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_lines_report, self).__init__(cr, uid, name, context)

    def set_context(self, objects, data, ids, report_type=None):
        #### Important to set the language to be that of the invoice partner for proper formating of data and translation
        self.localcontext['lang']= objects.partner_id.lang
        return super(invoice_lines_report, self).set_context(objects, data, ids, report_type=report_type)

class wrapped_report_contribution_register(osv.AbstractModel):
    _name = 'report.professional_templates.report_invoice'
    _inherit = 'report.abstract_report'
    _template = 'professional_templates.report_invoice'
    _wrapped_report_class = invoice_lines_report
