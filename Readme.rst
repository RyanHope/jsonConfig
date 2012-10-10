==========
jsonConfig
==========

``jsonConfig`` is a Python package that provides sparse JSON based config files with GUI editor.
The config files are referred to as being sparse because only those settings which are different than
the default values are stored in the config files. Default config options are defined programmatically
which allows defaults to be updated with out overwriting a users options.

Usage
=====

Creating defaults
-----------------
::

  from jsonConfig import *

  cfg = Config()
  cfg.add_setting( 'Category 1', 'option1', 'Value1', alias = 'Option #1', options = ['Value1', 'Value2'], type = CT_COMBO, about = 'An example option.' )
  cfg.add_setting( 'Category 1', 'option2', True, alias = 'Option #2', type = CT_CHECKBOX )
  cfg.add_setting( 'Category 2', 'option1', 'value', type = CT_LINEEDIT)
  

Accessing values
----------------
::
 
  >>> cfg
  {'Category 2': {'option1': 'value'}, 'Category 1': {'option2': True, 'option1': 'Value1'}}
  
  >>> cfg['Category 1']['option1']
  'Value1'
  
Loading config file
-------------------

config.json
::

  {
    "Category 1": {
      "option1": {
        "value": "Value2"
      }
    }
  }
  
::

  cfg.set_user_file("config.json")
  >>> cfg
  {'Category 2': {'option1': 'value'}, 'Category 1': {'option2': True, 'option1': 'Value2'}}
  
GUI Editor
----------
::

  from PySide.QtGui import *
  from jsonConfig import ConfigEditor

  app = QApplication([])
  editor = ConfigEditor(app, cfg, 'Demo Config Editor')
  editor.setup()
  app.exec_()
  
.. image:: http://ompldr.org/vZnRscg