# -*- coding: utf-8 -*-
import time
from openerp import api, models
from openerp.osv import osv
from openerp.report import report_sxw

class sbg_subscription_statement_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sbg_subscription_statement_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        'time': time,
        })

class sbg_subscription_statement_qweb(models.AbstractModel):
    _name = 'report.sbg_subscriptions.sbg_subscription_statement_qweb'
    _inherit = 'report.abstract_report'
    _template = 'sbg_subscriptions.sbg_subscription_statement_qweb'
    _wrapped_report_class = sbg_subscription_statement_report
