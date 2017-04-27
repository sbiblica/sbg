.. _changelog:

Changelog
=========

`Version 1.0 (2017-01-08 09:40)` - Major release
------------------------------------------------
- NOTE: To upgrade to this major release, please uninstall the older version 0.X and do a fresh installation of this version 1.0

- You can now create as many Report styles as you want and save them for use in different situations or per partner

- You can now associate/assign a report style to each Odoo Partner(customer,vendor,company,etc)

- The Report style assigned to a Partner will be used to print the report

- If partner does not have a report style assigned, The is a default report style to use 

- Read the module description for details on how to configure and assign report styles

`Version 0.8`
----------------
- Introduced product image in invoice, sales order, quote, picking slip and delivery notes

`Version 0.7`
----------------
- Introduced more Invoice status

`Version 0.6 (2016-10-15)`
----------------
- Added an ``Amount in Words`` feature to display the Total Amount for Invoice,Purchase Order,Sales Order/Quote in words..You can disable if you dont want it.
- This ``Amount in Words`` is available in 13 languages ..check the module description for details
- Added ``Customer signature`` and ``Stamp`` section just in case its useful to some users but you can request us to remove it if you dont want...support is free
- Few more bugs fixed and templates optimized to look better


`Version 0.5 (2016-06-10)`
----------------

- Added a setting to allow user to specify the ``Font-Family`` for the reports. Default font-family is configured in the company profile.

- Added a feature to automatically hide 'Taxes' column when there is not tax to charge

- Minor changes in the ``Iconography`` to be compatible with Windows Server Installations


`Version 0.4 (2016-05-24)`
----------------

- Added Parameter for user to adjust ``Font-size`` in each report header, body and footer

- Now fully compatible with the any version of ``wkhtmltopdf`` including the latest stable release: 0.12.3 (with patched qt)

- Removed the ``120 pixel`` height limit on Logo images. Now user can  use larger images

- Improved design to maximize space utilization

- Added Barcode images in Picking list and Delivery templates


`Version 0.3 (2016-03-26)`
----------------

- removed ``Required`` field feature in all Template Selection drop-down lists. This was to avoid some templates not getting 
  deleted when module is ``un-installed`` then ``re-installed`` and hence avoided seeing ``duplicate`` or ``triplicate`` templates 
  in the drop-down list.

- When ``Social Media IDs`` are not defined, the bar is no longer displaying hence the report looks neat.

- Further improvements done and known bugs fixed in all the templates.

- Added this Changelog to help clients to figure out whats new in the latest release.
