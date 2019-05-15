# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Client',
    'version': '1.1.0',
    'author': 'Numigi',
    'maintainer': 'numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Others',
    'summary': 'Client base module',
    'depends': [
        # numigi/odoo-base
        'numipack',
        'numitech',

        # odoo/odoo
        'barcodes',
        'stock',
        'project',  # TA#1689
        'account_accountant',  # TA#1659
        'contacts',  # TA#1659
        'sale_management',  # TA#2149
        'sale_order_dates',  # TA#3078
        'document',  # TA#3191
        'crm',  # TA#3191
        'helpdesk',  # TA#3191
        'hr',  # TA#4589
        'board',  # TA#3191
        'auth_oauth',  # TA#3447
        'google_calendar',  # TA#3405

        # Numigi/aeroo_reports
        'account_check_printing_aeroo',  # TA#4585

        # Numigi/odoo-enterprise-addons
        'aged_partner_balance_invoice_date',  # TA#6826

        # Numigi/odoo-partner-addons
        'google_partner_address',  # TA#3405

        # OCA/stock-logistics-workflow
        'stock_no_negative',  # TA#6726

        # Wasabi modules
        'account_acomba_number',  # TA#5260
        'product_attribute_paint_type',
        'product_paint_batch',  # TA#1778
        'stock_move_faster',  # TA#4640
        'stock_move_list_partner',  # TA#4156
        'stock_move_list_requested_date',  # TA#4394
        'stock_move_list_reserved',  # TA#4159
        'stock_block_auto_purchase_order',  # TA#4018
        'sale_order_acomba_reference',  # TA#4582
        'purchase_order_acomba_reference',  # TA#4582
        'sale_order_search_by_client_order_ref',  # TA#6828
        'product_width_thickness',  # TA#4895
        'stock_move_origin_customer',  # TA#7272

        # OCA/commission
        # Sale commission is uninstalled for now.
        # It will likely be reinstalled in the future (see TA#6688).
        # 'sale_commission',  # TA#3075
    ],
    'installable': True,
}
