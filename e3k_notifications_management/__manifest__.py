# -*- coding: utf-8 -*-
{
    'name': 'Followers/Notifications  Management',
    'version': '1.0.2',
    'category': 'Hidden',
    'description':
        """
        This Module add below functionality into odoo

        1.Automatically stop adding customer as follower in Sale Order\n
        2.Automatically stop adding customer as follower in Invoice\n
        3.Automatically stop adding vendor as follower in Bill\n
Stop Auto Followers in Sale/Invoice
Odoo Stop Auto Followers in Sale/Invoice
Stop auto followers in sale 
Odoo stop auto followers in sale 
Stop auto followers in invoice 
Odoo stop auto followers in invoice 
Manage stop followers 
Odoo manage stop followers 
When you confirm Sale Order or validate Invoice/Bill at that time customer/vendor will automatically added to the document as follower of the document
Odoo When you confirm Sale Order or validate Invoice/Bill at that time customer/vendor will automatically added to the document as follower of the document
you can stop adding customer/vendor as follower of the document using this application
Odoo you can stop adding customer/vendor as follower of the document using this application
Automatically stop adding customer as follower in Sale Order
Odoo Automatically stop adding customer as follower in Sale Order
Automatically stop adding customer as follower in Invoice
Odoo Automatically stop adding customer as follower in Invoice
Automatically stop adding vendor as follower in Bill
Odoo Automatically stop adding vendor as follower in Bill
Manage Automatically stop adding customer as follower in Sale Order
Odoo manage Automatically stop adding customer as follower in Sale Order
Manage Automatically stop adding customer as follower in Invoice
Odoo manage Automatically stop adding customer as follower in Invoice
Manage Automatically stop adding vendor as follower in Bill
Odoo manage Automatically stop adding vendor as follower in Bill
    """,
    'summary': 'odoo app Stop Auto Followers in Sale, Invoice, Vendor Bill',
    'depends': [
        'sale_management',
        'purchase',
        'project',
        'stock',
    ],
    'data': [
        'data/mail_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'author': 'e3k',
    'website': 'http://www.e3k.co',
    'license': 'LGPL-3'
}