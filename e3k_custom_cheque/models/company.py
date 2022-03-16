# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    check_inv_line_per_page = fields.Integer('5: Number of invoices lines in check page', default=7)
    is_currency = fields.Boolean('25: Add currency in field Payment amount 2', default=True)

    image_top = fields.Integer('Image : Top distance', default=350)
    image_width = fields.Integer('Image : width', default=1000)
    image_height = fields.Integer('Image : height', default=400)

    check_background = fields.Selection([('show', 'Show check background'), ('hidden', 'Hide check background')],
                                        string="Background", required=True, default="hidden")

    date_format = fields.Char("10: Date Format ", default='%d%m%Y')
    payment_date_top = fields.Integer('15: Payment date : Top distance', default=50)
    payment_date_left = fields.Integer('20: Payment date : Left distance', default=1020)

    display_date_format = fields.Boolean(string="30: Display date format text")
    display_date_format_top = fields.Integer('35: Date format text : Top distance', default=300)
    display_date_format_left = fields.Integer('40: Date format text : Left distance', default=1020)
    display_date_format_font_size = fields.Integer('45: Date format text : font size', default=20)

    amount1_top = fields.Integer('50: Payment amount 1 : Top distance', default=75)
    amount1_left = fields.Integer('55: Payment amount 1 : Left distance', default=100)

    amount2_top = fields.Integer('60: Payment amount 2 : Top distance', default=125)
    amount2_right = fields.Integer('65: Payment amount 2 : Right distance', default=90)

    amount_in_world_font_size = fields.Integer('80: Amount in world font size', default=20)
    amount_in_world_width = fields.Integer('80: Amount in world width', default=700)

    address_top = fields.Integer('70: Address : Top distance', default=175)
    address_left = fields.Integer('75: Address : Left distance', default=100)

    check_font_size = fields.Integer('85: Check: font size', default=20)
    check_area_width = fields.Integer('90: Check in the middle: width', default=1200)

    check_table_font_size = fields.Integer('95: Check table: font size', default=16)
    check_table_width = fields.Integer('100: Check table: width', default=1150)

    check_table1_top = fields.Integer('105: Check table 1: Top distance', default=-150)
    check_table1_left = fields.Integer('110: Check table 1: Left distance', default=0)

    check_table2_top = fields.Integer('115: Check table 2: Top distance', default=115)
    check_table2_left = fields.Integer('120: Check table 2: Left distance', default=0)

    table_1_partner_name_top = fields.Integer('125: Table-1 Partner name: Top distance', default= 115)
    table_1_partner_name_left = fields.Integer('130: Table-1 Partner name: Left distance', default=400)

    table_1_payment_date_top = fields.Integer('135: Table-1 Payment date: Top distance', default=-115)
    table_1_payment_date_left = fields.Integer('140: Table-1 Payment date: Left distance', default=800)

    table_1_amount_top = fields.Integer('145: Table-1 Amount: Top distance', default=600)
    table_1_amount_left = fields.Integer('150: Table-1 Amount: Left distance', default=380)

    table_2_partner_name_top = fields.Integer('155: Table-2 Partner name: Top distance', default=350)
    table_2_partner_name_left = fields.Integer('160: Table-2 Partner name: Left distance', default=50)

    table_2_payment_date_top = fields.Integer('165: Table-2 Payment date: Top distance', default=350)
    table_2_payment_date_left = fields.Integer('170: Table-2 Payment date: Left distance', default=325)

    table_2_amount_top = fields.Integer('175: Table-2 Amount: Top distance', default=800)
    table_2_amount_left = fields.Integer('180: Table-2 Amount: Left distance', default=250)

    print_check_number = fields.Boolean(string="Print Check Number")

    table_1_check_number_top = fields.Integer('185: Table-1 Check number: Top distance', default=300)
    table_1_check_number_left = fields.Integer('190: Table-1 Check number: Left distance', default=350)

    table_2_check_number_top = fields.Integer('195: Table-2 Check number: Top distance', default=500)
    table_2_check_number_left = fields.Integer('200: Table-2 Check number: Left distance', default=1100)
