ipynb-swiftstore
=======================

Stores IPython notebooks automagically onto an OpenStack Swift implementation, including Rackspace CloudFiles.

![IPython Notebook](http://ipython.org/ipython-doc/rel-0.13/_images/ipynb_icon_128x128.png) ![->](http://i.imgur.com/kOFsLIx.jpg) ![OpenStack](http://i.imgur.com/7BeZLRq.jpg)

# Usage

Make sure you have a notebook profile setup. It's easy to set one up if you
don't have one:

```bash
$ ipython profile create swifty_ipy
[ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_config.py'
[ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_notebook_config.py'
```

## On Rackspace's CloudFiles

Add this to your ipython notebook profile (`ipython_notebook_config.py`):

```bash
c.NotebookApp.notebook_manager_class = '.OpenStackNotebookManager'
c.OpenStackNotebookManager.account_name = USER_NAME
c.OpenStackNotebookManager.account_key = API_KEY
c.OpenStackNotebookManager.container_name = u'notebooks'
c.OpenStackNotebookManager.identity_type = u'rackspace' #keystone for other OpenStack implementations
```

You'll need to replace `USER_NAME` and `API_KEY` with your actual username and
api key of course. You can get the API key from the cloud control panel after logging in.

<!-- TODO Add link to image about location of api_key -->

## On OpenStack Swift

The configuration is a bit different for OpenStack.



