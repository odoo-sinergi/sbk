{
	"name": "SDT Stock Adjustment",
	"version": "1.0", 
	"depends": ["base",
		"stock",
	],
	"author": "PT. Sinergi Data Totalindo",
	"website": "www.sinergidata.co.id",
    'category': 'Inventory',
	'price':'30',
    'currency': 'USD',
	"category": "Warehouse",
	"summary" : "This modul to add stock adjustment with background process",
	"description": """

Manage
======================================================================

* this modul to add stock adjustment using background process
* after import excel file, click Activate to run schedule in background


""",
	"data": [
		"security/security.xml",
		"security/ir.model.access.csv",
		"data/schedule.xml",

		"data/sequence_data.xml",
		"view/sdt_stock_adjustment.xml",
	],
	"application": True,
	"installable": True,
	"auto_install": False,
}