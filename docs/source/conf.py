# docs/source/conf.py

# -- Path setup --------------------------------------------------------------
import os
import sys
from dotenv import load_dotenv

# додаємо корінь проєкту до PYTHONPATH, щоб Sphinx знаходив ваш модуль app
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# завантажуємо .env для того, щоб імпорт app.conf.config(Settings) не падав
load_dotenv(os.path.join(project_root, '.env'))


# -- Project information -----------------------------------------------------
project = 'Contacts App'
author  = 'Liuklian Oksana'
release = '0.1'


# -- General configuration ---------------------------------------------------
# Тут дуже важливо підключити sphinx.ext.autodoc!
extensions = [
    'sphinx.ext.autodoc',           # <-- дає директиву automodule
    'sphinx.ext.napoleon',          # для Google/Numpy docstring
    'sphinx_autodoc_typehints',     # автопідхват аннотацій типів
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']