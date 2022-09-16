# -*- coding: utf-8 -*-
{
    'name': "Reception With Treatment Unit",

    'summary': """
        Reception With Treatment Unit""",

    'description': """
       Reception With Treatment Unit
    """,

    'author': "Nextmove",
    'website': "http://www.nextmove.com",
    'category': 'Project',
    'version': '0.1',

    'depends': ['nm_health_wellness_reception_sales','nm_treatment_unit'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/disease_symptomology_data.xml',

        'views/product_views.xml',
        'views/reception_customer_view.xml',
        'views/unit_guest_views.xml',
        'views/reception_order_views.xml',
        'views/intake_form_view.xml',
        'report/intake_form_template.xml',
        'report/action_reports.xml',
    ],
    "installable": True,
    "auto_install": True,
    "application": True,
   
}
