# -*- coding: utf-8 -*-
{
    'name': "NM - Reception With Treatment Unit",

    'summary': """
        NM - Reception With Treatment Unit""",

    'description': """
       Reception With Treatment Unit
    """,

    'author': "Nextmove",
    'website': "http://www.nextmove.com",
    'category': 'Project',
    'version': '0.1',

    'depends': ['nm_health_wellness_reception_sales','nm_treatment_unit',
                'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/disease_symptomology_data.xml',
        'data/sequences.xml',
        'views/product_views.xml',
        'views/reception_customer_view.xml',
        'views/unit_guest_views.xml',
        'views/reception_order_views.xml',
        'views/intake_form_view.xml',
        'views/lab_test_view.xml',
        'views/unit_treatmentplan_view.xml',
        'views/prescription_view.xml',
        'report/intake_form_template.xml',
        'report/lab_test_template.xml',
        'report/treatmentplan_template.xml',
        'report/guest_template.xml',
        'report/action_reports.xml',
    ],
    "installable": True,
    "auto_install": True,
    "application": True,
   
}
