import os
import sys
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

load_dotenv(os.path.join(project_root, '.env'))


project = 'Contacts App'
author  = 'Liuklian Oksana'
release = '0.1'

extensions = [
    'sphinx.ext.autodoc',           
    'sphinx.ext.napoleon',         
    'sphinx_autodoc_typehints',    
]

templates_path = ['_templates']
exclude_patterns = []


html_theme = 'alabaster'
html_static_path = ['_static']