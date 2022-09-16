# -*- coding: utf-8 -*-
{
    'name': "Health Care and Wellness Tratment unit for Sale",

    'summary': """
        Health Care and Wellness Tratment unit for Sal
        """,

    'description': """
        Health Care and Wellness Tratment unit for Sal
    """,
    'icon':'/nm_treatment_unit/static/description/icon.png',
    'author': "Nextmove",
    'website': "http://www.nextmove.com",

    'category': 'Project',
    'version': '0.1',

    'depends': ['project'],
    'data': [
        'security/unit_security.xml',
        'security/ir.model.access.csv',

        'data/mail_template_data.xml', 

        'report/unit_report_views.xml',

        'views/unit_update_views.xml',
        'views/unit_menuitem.xml',
        'views/unit_guest_views.xml',
        'views/unit_views.xml',
        'views/unit_stage_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'nm_treatment_unit/static/src/unit_control_panel/*',
            
            'nm_treatment_unit/static/src/js/unit_control_panel.js',
            'nm_treatment_unit/static/src/js/unit_kanban.js',
        ],
        
    },
    "installable": True,
    "auto_install": True,
    "application": True,
   
}
