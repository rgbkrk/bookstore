Bookstore
=========

Stores IPython notebooks automagically onto object storage with a cloud
provider.

**Note: Bookstore only works against IPython 1.0.0 alpha.**

Currently supports OpenStack and Rackspace.

*Add your provider with a pull request!*

Bookstore currently has generic support for OpenStack Swift and simplified
authentication for Rackspace's CloudFiles. Feel free to make a pull request if
you want a notebook manager for your implementation.

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

This version requires IPython 1.0.0a1 and will pull the `alpha release tarball<http://archive.ipython.org/testing/1.0.0/ipython-1.0.0a1.tar.gz#egg=ipython-1.0.0a1>`_ as mentioned in the `notice to IPython-dev<http://mail.scipy.org/pipermail/ipython-dev/2013-July/011994.html>`. You probably want to *install this to a virtualenv* or it will likely overwrite your current IPython installation. When the full release comes out, this should get a little easier to setup.

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
your provider.

You can create a brand new notebook profile for bookstore:

.. code-block:: bash

    $ ipython profile create swifty_ipy
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_config.py'
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_notebook_config.py'

Or just add it to your default configuration, which should be located at

.. code-block:: bash

    ~/.ipython/profile_default/ipython_notebook_config.py

Each provider has their own setup for authentication.

On OpenStack Swift using Keystone Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack (generic, non provider specific) has quite a few details you'll need
to configure, namely account name, account key, auth endpoint, and region.
You'll possibly need a tenant id and a tenant name.

Add this to your ipython notebook profile *ipython_notebook_config.py*, making
sure it comes after the config declaration.

.. code-block:: python

    c = get_config()

    ... # All your other nifty configuration can go here

    c.NotebookApp.notebook_manager_class = 'bookstore.swift.KeystoneNotebookManager'
    c.KeystoneNotebookManager.account_name = USER_NAME
    c.KeystoneNotebookManager.account_key = API_KEY
    c.KeystoneNotebookManager.container_name = u'notebooks'
    c.KeystoneNotebookManager.auth_endpoint = u'127.0.0.1:8021'
    c.KeystoneNotebookManager.tenant_id = TENANT_ID
    c.KeystoneNotebookManager.tenant_name = TENANT_NAME
    c.KeystoneNotebookManager.region = 'RegionOne'

On Rackspace's CloudFiles
~~~~~~~~~~~~~~~~~~~~~~~~~

Add this to your ipython notebook profile *ipython_notebook_config.py*, making
sure it comes after the config declaration.

.. code-block:: python

    c = get_config()

    ... # All your other nifty configuration can go here

    c.NotebookApp.notebook_manager_class = 'bookstore.cloudfiles.CloudFilesNotebookManager'
    c.CloudFilesNotebookManager.account_name = USER_NAME
    c.CloudFilesNotebookManager.account_key = API_KEY
    c.CloudFilesNotebookManager.container_name = u'notebooks'

You'll need to replace ``USER_NAME`` and ``API_KEY`` with your actual username and
api key of course. You can get the API key from the cloud control panel after logging in.

Note: If you're using Rackspace UK, you'll want to set your region to ``'LON'``.

Contributing
------------

Send a pull request on `GitHub<http://www.github.com/rgbkrk/bookstore>`. It's
that simple.

