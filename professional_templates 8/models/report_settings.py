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
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
from openerp import models, fields, api

class TemplateSettings(models.Model):
    _name = "report.template.settings"
    _description = "Report Template Settings"

    
    @api.model
    def _default_so_template(self):
        def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'SO Template' ), ('type', '=', 'qweb')], 
            order='name asc', limit=1)
        return def_tpl or self.env.ref('sale.report_saleorder_document')

    @api.model
    def _default_po_template(self):
        def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'PO Template' ), ('type', '=', 'qweb')], 
            order='name asc', limit=1)
        return def_tpl or self.env.ref('purchase.report_purchaseorder_document')

    @api.model
    def _default_rfq_template(self):
        def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'RFQ Template' ), ('type', '=', 'qweb')], 
            order='name asc', limit=1)
        return def_tpl or self.env.ref('purchase.report_purchasequotation_document')

    @api.model
    def _default_dn_template(self):
        def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Delivery Template' ), ('type', '=', 'qweb')], 
            order='name asc', limit=1)
        return def_tpl or self.env.ref('stock.report_picking')

    @api.model
    def _default_pk_template(self):
        def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Picking Template' ), ('type', '=', 'qweb')], 
            order='name asc', limit=1)
        return def_tpl or self.env.ref('stock.report_picking')

    @api.model
    def _default_inv_template(self):
        def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Invoice Template' ), ('type', '=', 'qweb')],
            order='name asc', limit=1)
        return def_tpl or self.env.ref('account.report_invoice_document')


    name = fields.Char('Name of Style', required=True, help="Give a unique name for this report style")
    template_inv = fields.Many2one('ir.ui.view', 'Invoice', default=_default_inv_template,
                    domain="[('type', '=', 'qweb'), ('name', 'like', 'Invoice Template' )]", required=False)
    template_so = fields.Many2one('ir.ui.view', 'Order/Quote', default=_default_so_template, 
                    domain="[('type', '=', 'qweb'), ('name', 'like', 'SO Template' )]", required=False)

    template_po = fields.Many2one('ir.ui.view', 'Purchase Order', default=_default_po_template, 
                    domain="[('type', '=', 'qweb'), ('name', 'like', 'PO Template' )]", required=False)

    template_rfq = fields.Many2one('ir.ui.view', 'RFQ', default=_default_rfq_template, 
                    domain="[('type', '=', 'qweb'), ('name', 'like', 'RFQ Template' )]", required=False)

    template_dn = fields.Many2one('ir.ui.view', 'Delivery Note', default=_default_dn_template, 
                    domain="[('type', '=', 'qweb'), ('name', 'like', 'Delivery Template' )]", required=False)

    template_pk = fields.Many2one('ir.ui.view', 'Picking Slip', default=_default_pk_template, 
                    domain="[('type', '=', 'qweb'), ('name', 'like', 'Picking Template' )]", required=False)

    logo = fields.Binary("Report Logo", attachment=True,
            help="This field holds the image used as logo for the reports, if non is uploaded, the company logo will be used")
    odd = fields.Char('Odd parity Color', size=7, required=True, default="#F2F2F2", help="The background color for Odd invoice lines in the invoice")       
    even = fields.Char('Even parity Color', size=7, required=True, default="#FFFFFF", help="The background color for Even invoice lines in the invoice" )   
    theme_color = fields.Char('Theme Color', size=7, required=True, default="#F07C4D", help="The Main Theme color of the invoice. Normally this\
                     should be one of your official company colors")
    text_color = fields.Char('Text Color', size=7, required=True, default="#6B6C6C", help="The Text color of the invoice. Normally this\
                     should be one of your official company colors or default HTML text color")
    name_color = fields.Char('Company Name Color', size=7, required=True, default="#F07C4D", help="The Text color of the Company Name. Normally this\
                     should be one of your official company colors or default HTML text color")
    cust_color = fields.Char('Customer Name Color', size=7, required=True, default="#F07C4D", help="The Text color of the Customer Name. Normally this\
                     should be one of your official company colors or default HTML text color")
    theme_txt_color = fields.Char('Theme Text Color', size=7, required=True, default="#FFFFFF",
                     help="The Text color of the areas bearing the theme color. Normally this should NOT be the same color as the\
                            theme color. Otherwise the text will not be visible")

    header_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Header Font(px):", default=10, required=True)
    body_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Body Font(px):", default=10,required=True)
    footer_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Footer Font(px):", default=8,required=True)
    font_family = fields.Char('Font Family:', default="sans-serif", required=True)
    aiw_report = fields.Boolean('Amount in words?', default=True, help="Check this box to enable the display of amount in words in the invoice/quote/sale order reports")
    show_img = fields.Boolean('Product Image?', default=True, help="Check this box to display product image in Sales Order, Quotation, Invoice and Delivery Note")
