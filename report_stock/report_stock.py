from openerp import models,fields,api,exceptions,tools

class report_stock_quants(models.Model):
    _name='report_stock.quants'
    _auto=False
    isbn=fields.Char('Isbn')
    descripcion=fields.Char('Descripcion')
    costo=fields.Float('Costo')
    precio=fields.Float('Precio')
    stock=fields.Float('Stock')
    valor=fields.Float('Valor')
    
    def init(self,cr):
        tools.drop_view_if_exists(cr,'report_stock_quants')
        cr.execute(""" 
        Create view report_stock_quants AS (
        Select pp.id AS id,pp.ean13 AS isbn
             , pp.name_template AS descripcion
             , o.costo AS costo
             , pt.list_price AS precio
, o.quanty_total AS stock
, (o.quanty_total * o.costo) AS valor
FROM product_product pp
JOIN product_template pt ON pp.product_tmpl_id = pt.id 
JOIN (SELECT product_id, AVG(cost) AS costo, SUM(qty) AS quanty_total 
FROM stock_quant inner join stock_location on stock_quant.location_id = stock_location.id where stock_location.usage != 'customer' GROUP BY product_id) o
ON pp.id = o.product_id
WHERE pt.type = 'product' AND pp.active = 't' AND o.quanty_total > 0
ORDER BY pp.default_code
        )
        """)