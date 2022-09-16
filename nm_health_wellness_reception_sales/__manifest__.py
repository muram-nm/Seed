# -*- coding: utf-8 -*-
{
    'name': "NM - Health Care and Wellness Reception Sales",
    'summary': "summary...",
    'icon': '/nm_health_wellness_reception_sales/static/description/icon.png',
    'description': "description...",
    'author': "Smart Way Business Solutions",
    'website': "http://www.smartway.co",
    'category': 'Sales',
    'version': '1.0',
    'depends': ['base', 'mail', 'sale', 'product', 'account', 'sale_project'],
    'license': "Other proprietary",
    'data': [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/mail_template_data.xml",
       
        "views/reception_customer_view.xml",
        "views/reception_order_view.xml",
        "views/product_view.xml",

         "views/menu_views.xml",
        # "views/reception_relative_view.xml",
        "report/layout.xml",
        "report/templates.xml",
        "report/reports.xml",
    ],
}
