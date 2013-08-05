Bookstore
=========

Stores IPython notebooks automagically onto OpenStack clouds through Swift.

**Note: Bookstore only works against IPython 1.0.0+**

Currently supports OpenStack Swift with Keystone authentication and Rackspace.

*Add your provider with a pull request!*

Bookstore currently has generic support for OpenStack Swift and simplified
authentication for Rackspace's CloudFiles.

Once installed and configured (added to an ipython profile), just launch
IPython notebook like normal:

.. code-block:: bash

    $ ipython notebook
    2013-08-01 13:44:19.199 [NotebookApp] Using existing profile dir: u'/Users/rgbkrk/.ipython/profile_default'
    2013-08-01 13:44:25.384 [NotebookApp] Using MathJax from CDN: http://cdn.mathjax.org/mathjax/latest/MathJax.js
    2013-08-01 13:44:25.400 [NotebookApp] Serving rgbkrk's notebooks on Rackspace CloudFiles from container: notebooks
    2013-08-01 13:44:25.400 [NotebookApp] The IPython Notebook is running at: http://127.0.0.1:9999/
    2013-08-01 13:44:25.400 [NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).

Installation
------------

This version requires IPython 1.0.0-rc1 or 1.0.0a1 and will pull the `release candidate 1 tarball <http://archive.ipython.org/testing/1.0.0/ipython-1.0.0-rc1.tar.gz#egg=ipython-1.0.0-rc1>`_ as mentioned in the `notice to IPython-dev <http://mail.scipy.org/pipermail/ipython-dev/2013-August/012058.html>`_. You probably want to *install this to a virtualenv* or it will likely overwrite your current IPython installation. When the full release comes out, this should get a little easier to setup.

Simply:

.. code-block:: bash

    $ pip install bookstore

Alternatively, you can always pull from the master branch if you're the adventurous type:

.. code-block:: bash

    $ pip install -e git+https://github.com/rgbkrk/bookstore.git

Installation isn't the end though. You need to configure your account details
as well as where you'll be storing the notebooks.

Configuration
-------------

Bookstore has to be added to an IPython profile and configured to work with
your OpenStack provider.

You can create a brand new notebook profile for bookstore:

.. code-block:: bash

    $ ipython profile create swiftstore
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_config.py'
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_notebook_config.py'

When launching, just set the custom profile you want to use

.. code-block:: bash

    $ ipython notebook --profile=swiftstore

If you want to keep it simple, just add the configuration to your default configuration located at:

.. code-block:: bash

    ~/.ipython/profile_default/ipython_notebook_config.py

Each provider has their own setup for authentication.

On OpenStack Swift using Keystone Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack (generic, non provider specific) has quite a few details you'll need
to configure, namely account name, account key, auth endpoint, and region.
You'll possibly need a tenant id and a tenant name.

Add this to your ipython notebook profile *ipython_notebook_config.py*, making
sure it comes after the config declaration ``c = get_config()``.

.. code-block:: python

    # Setup IPython Notebook to write notebooks to a Swift Cluster
    # that uses Keystone for authentication
    c.NotebookApp.notebook_manager_class = 'bookstore.swift.KeystoneNotebookManager'

    # Account details for OpenStack
    c.KeystoneNotebookManager.account_name = USER_NAME
    c.KeystoneNotebookManager.account_key = API_KEY
    c.KeystoneNotebookManager.auth_endpoint = u'127.0.0.1:8021'
    c.KeystoneNotebookManager.tenant_id = TENANT_ID
    c.KeystoneNotebookManager.tenant_name = TENANT_NAME
    c.KeystoneNotebookManager.region = 'RegionOne'

    # Container on OpenStack Swift
    c.KeystoneNotebookManager.container_name = u'notebooks'

On Rackspace's CloudFiles
~~~~~~~~~~~~~~~~~~~~~~~~~

The Rackspace CloudFileNotebookManager simply needs your ``USER_NAME`` and ``API_KEY``. You can also configure the region to store your notebooks (e.g. ``'SYD'``, ``'ORD'``, ``'DFW'``, ``'LON'``). Note: If you're using Rackspace UK, set your region to ``'LON'``.

Add this to your ipython notebook profile *ipython_notebook_config.py*, making
sure it comes after the config declaration ``c = get_config()``.

.. code-block:: python

    # Setup IPython Notebook to write notebooks to CloudFiles
    c.NotebookApp.notebook_manager_class = 'bookstore.cloudfiles.CloudFilesNotebookManager'

    # Set up your user name and password
    c.CloudFilesNotebookManager.account_name = USER_NAME
    c.CloudFilesNotebookManager.account_key = API_KEY

    # Container on CloudFiles
    c.CloudFilesNotebookManager.container_name = u'notebooks'

Contributing
------------

Send a pull request on `GitHub <http://www.github.com/rgbkrk/bookstore>`_. It's
that simple.

