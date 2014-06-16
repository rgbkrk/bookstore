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

If you have already set your OpenStack credentials in your environment (OS_USERNAME, OS_AUTH_URL, etc) you are good to go, just run

.. code-block:: bash

    ipython notebook --NotebookApp.notebook_manager_class=bookstore.OpenStackNotebookManager

and IPython will read/write notebooks from your cloud storage in a container called “notebooks”.

.. code-block:: bash

    $ ipython notebook
    2014-06-16 16:16:46.810 [NotebookApp] Using existing profile dir: '/Users/andreabedini/.ipython/profile_default'
    2014-06-16 16:16:48.490 [NotebookApp] Using MathJax from CDN: http://cdn.mathjax.org/mathjax/latest/MathJax.js
    2014-06-16 16:16:48.515 [NotebookApp] Serving notebooks from OpenStack Swift storage container: notebooks
    2014-06-16 16:16:48.515 [NotebookApp] 0 active kernels
    2014-06-16 16:16:48.515 [NotebookApp] The IPython Notebook is running at: http://localhost:8888/
    2014-06-16 16:16:48.515 [NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    2014-06-16 16:16:56.463 [NotebookApp] Kernel started: b750f6ee-879f-4c39-a63f-504210cc9bf6


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

Bookstore offers a general class that works with any OpenStack Swift service along with few adaptors for specific services like Rackspace CloudFiles.

OpenStackNotebookManager
------------------------

.. code-block:: python

    # Tells IPython Notebook to use the OpenStackNotebookManager class for storage
    c.NotebookApp.notebook_manager_class = 'bookstore.OpenStackNotebookManager'

    # Account credentials for OpenStack, OpenStackNotebookManager will
    # get any of these from the environment if omitted

    c.OpenStackNotebookManager.auth_endpoint = # OS_AUTH_URL
    c.OpenStackNotebookManager.user_name = # OS_USERNAME
    c.OpenStackNotebookManager.password = # OS_PASSWORD
    c.OpenStackNotebookManager.tenant_id = # OS_TENANT_ID
    c.OpenStackNotebookManager.tenant_name = # OS_TENANT_NAME

Rackspace CloudFiles
--------------------

.. code-block:: python

    # Tells IPython Notebook to use the Rackspace CloudFilesNotebookManager for storage
    c.NotebookApp.notebook_manager_class = 'bookstore.CloudFilesNotebookManager'

    c.CloudFilesNotebookManager.user_name = # your rackspace username
    c.CloudFilesNotebookManager.password = # your rackspace password

SwiftNotebookManager
--------------------

For maximum flexibility, you can use directly the class `SwiftNotebookManager`.

.. code-block:: python

    c.NotebookApp.notebook_manager_class = 'bookstore.SwiftNotebookManager'

    c.SwiftNotebookManager.connection_args = {

    }

`connection_args` is passed as-it-is to `swiftclient.client.Connection` see http://docs.openstack.org/developer/python-swiftclient/swiftclient.html#swiftclient.client.Connection for all the available arguments.

Independently from the adaptor used, you can customize the name of the container used to store the notebooks with the following configuration line:

.. code-block:: python

    c.SwiftNotebookManager.container = "here_are_the_notebooks"

Contributing
------------

Send a pull request on `GitHub <http://www.github.com/rgbkrk/bookstore>`_. It's
that simple. More than happy to respond to issues on GitHub as well.

