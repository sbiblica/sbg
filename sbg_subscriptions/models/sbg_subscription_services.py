# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import math

class sbg_subscription_services(models.Model):
    _name = 'sbg.subscription.services'
    _description = 'Subscription services'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
    duration_type = fields.Selection(string="Duration type", selection=[('permanent', 'Permanent'),('period','Defined period'),('fees_quantity','By fees quantity')], default='permanent')
    total_amount = fields.Float(string="Total amount", default=0)
    fees_quantity = fields.Integer(string='Fees quantity', default=1)
    start_date = fields.Date(string="Start date", default=fields.Date.today)
    end_date = fields.Date(string="End date", default=fields.Date.today)
    periodicity = fields.Selection(string="Fee periodicity", selection=[('m','Monthly'), ('b','Bimonthly'), ('q','Quarterly'), ('s','Semiannually'), ('a','Annually')], default='m')
    fee = fields.Float(string="Fee",default=0)
    statement_description = fields.Char(string="Statement description")
    product_ids = fields.Many2many("product.product", string="Related products")
    sbg_subscription_ids = fields.One2many('sbg.subscriptions', 'subscription_service_id', string='Subscriptions')
    active = fields.Boolean(string="Active", default=True)

    @api.onchange('total_amount')
    def onchange_total_amount(self):
        if self.total_amount < 0:
            self.total_amount = abs(self.total_amount)
        if self.total_amount > 0:
            if self.fees_quantity > 0:
                self.fee = round(self.total_amount / self.fees_quantity, 2)
            elif self.fee > 0:
                self.fees_quantity = math.ceil(self.total_amount / self.fee)
        else:
            self.fee = 0

    @api.onchange('fees_quantity')
    def onchange_fees_quantity(self):
        if self.fees_quantity < 0:
            self.fees_quantity = abs(self.fees_quantity)
        if self.fees_quantity > 0:
            if self.total_amount > 0:
                self.fee = round(self.total_amount / self.fees_quantity, 2)
            elif self.fee > 0:
                self.total_amount = round(self.fee * self.fees_quantity, 2)
        else:
            self.total_amount = 0

    @api.onchange('fee')
    def onchange_fee(self):
        if self.fee < 0:
            self.fee = abs(self.fee)
        if self.fee > 0:
            if self.total_amount > 0:
                self.fees_quantity = math.ceil(self.total_amount / self.fee)
            elif self.fees_quantity > 0:
                self.fee = round(self.total_amount / self.fees_quantity, 2)
        else:
            self.total_amount = 0