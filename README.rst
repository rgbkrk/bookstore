Bookstore
=========

.. image:: https://badge.fury.io/py/bookstore.png
   :target: http://badge.fury.io/py/bookstore

.. image:: https://travis-ci.org/rgbkrk/bookstore.png?branch=master
   :target: https://travis-ci.org/rgbkrk/bookstore

Stores IPython notebooks automagically onto OpenStack clouds through Swift.

**Note: Bookstore requires IPython 2.0+**

.. image:: https://pbs.twimg.com/media/BVD3olXCMAA2rzb.png
   :alt: Multiple checkpoints


Installation
------------

Simply:

.. code-block:: bash

    $ pip install bookstore

Alternatively, you can always pull from the master branch if you're the adventurous type:

.. code-block:: bash

    $ pip install git+https://github.com/rgbkrk/bookstore.git

If you have already set your OpenSwift credentials in your environment (OS_USERNAME, OS_AUTH_URL, etc) you are good to go, just run

.. code-block:: bash

    ipython notebook --NotebookApp.notebook_manager_class=bookstore.SwiftNotebookManager

and IPython will read/write notebooks from your cloud storage in a container called “notebooks”.


Configuration
-------------

You can add bookstore to any IPython Notebook profile. Just add your configuration to the default configuration located at:

.. code-block:: bash

    ~/.ipython/profile_default/ipython_notebook_config.py

Alternatively, you can create a brand new notebook profile for bookstore:

.. code-block:: bash

    $ ipython profile create bookstore
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_bookstore/ipython_config.py'
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_bookstore/ipython_notebook_config.py'

When launching, just set the custom profile you want to use

.. code-block:: bash

    $ ipython notebook --profile=bookstore

Add this to your ipython notebook profile *ipython_notebook_config.py*, making sure it comes after the config declaration ``c = get_config()``.

.. code-block:: python

    # Setup IPython Notebook to write notebooks to a OpenSwift storage
    c.NotebookApp.notebook_manager_class = 'bookstore.SwiftNotebookManager'

    # Container on OpenStack Swift, defaults to notebooks.
    
    c.SwiftNotebookManager.container_name = u'notebooks'

    # Account credentials for OpenStack
    # SwiftNotebookManager will get any of these from the environment if omitted

    c.SwiftNotebookManager.account_name = OS_USERNAME
    c.SwiftNotebookManager.account_key = OS_PASSWORD
    c.SwiftNotebookManager.auth_endpoint = OS_AUTH_URL
    c.SwiftNotebookManager.tenant_id = OS_TENANT_ID
    c.SwiftNotebookManager.tenant_name = OS_TENANT_NAME

Once installed and configured (added to an ipython profile), just launch IPython notebook like normal:

.. code-block:: bash

    $ ipython notebook
    2013-08-01 13:44:19.199 [NotebookApp] Using existing profile dir: u'/Users/theuser/.ipython/profile_default'
    2013-08-01 13:44:25.384 [NotebookApp] Using MathJax from CDN: http://cdn.mathjax.org/mathjax/latest/MathJax.js
    2013-08-01 13:44:25.400 [NotebookApp] Serving theuser's notebooks from OpenStack Swift storage container: notebooks
    2013-08-01 13:44:25.400 [NotebookApp] The IPython Notebook is running at: http://127.0.0.1:8888/
    2013-08-01 13:44:25.400 [NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).


Contributing
------------

Send a pull request on `GitHub <http://www.github.com/rgbkrk/bookstore>`_. It's
that simple. More than happy to respond to issues on GitHub as well.

