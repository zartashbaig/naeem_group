# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2018~2021 Dmmsys <guoyihot@outlook.com>
# All Rights Reserved
#
##############################################################################
{
    'author': 'Dmmsys 124358678@qq.com ',
    'website': 'www.bonainfo.com,www.dmmsys.com',
    'version': '14.0.1.1.0',
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'support': '124358678@qq.com, bower_guo@msn.com',
    'price': '0',
    'currency': 'EUR',
    'images': ['static/description/main_banner.png'], 
    'name': 'List item serial number V14',
    'summary': """Display a serial number before tree list item. You can control any object what you want display item number in tree list.""",
    'description': """List serial number 
    List item serial number
    Serial number
    List view search panel hide
    Kanban view search panel hide
    Colum Width,
    Page Size,
    Advance Dynamic Tree View ,
	Advance Search ,
	Best List View Apps ,
	Best Tree View Apps ,
    Dynamic List View,
    Dynamic List ,
    Dynamic Search ,
    Dynamic Column ,
	Dynamic List View Apps , 
	Drag and edit columns ,
    List View ,
    List View Manage ,
    List View Management ,
    List View Column ,
	List view Advance Search ,
	List View Apps ,
	List View Management Apps ,
	Listview ,
    Field Display Control ,
    Field Hide Show ,
	Freeze List View Header ,    
	Hide/Show list view columns ,
	Odoo List View ,
	Odoo Advanced Search ,
	Odoo Manage List View ,
	Tree View Apps ,    
	Tree/List View Apps  ,
	Tree view Advance Search ,
	Treeview ,
	Tree View ,     
    """,


    # any module necessary for this one to work correctly
    'depends': ['web', ],

    # always loaded
    'data': [
        'views/item_number_templates.xml',
    ],
    # only loaded in demonstration mode
    'qweb': ['static/src/xml/*.xml']
}

