# coding: utf-8
"""Tests for the notebook manager."""
from __future__ import print_function

from tornado.web import HTTPError
from IPython.nbformat import current

#
# This is TestNotebookManager from
# IPython/html/services/notebooks/tests/test_nbmanager.py slightly adapted to
# test only the NotebookManager interface without making further assumptions.
# see https://github.com/ipython/ipython/issues/5982
#


class TestNotebookManager(object):

    """
    This class tests a generic NotebookManager implementation available at
    self.notebook_manager. It's designed to subclassed and used as a mix-in.
    """

    def add_code_cell(self, nb):
        output = current.new_output(
            "display_data", output_javascript="alert('hi');")
        cell = current.new_code_cell("print('hi')", outputs=[output])
        if not nb.worksheets:
            nb.worksheets.append(current.new_worksheet())
        nb.worksheets[0].cells.append(cell)

    def new_notebook(self):
        nbm = self.notebook_manager
        model = nbm.create_notebook()
        name = model['name']
        path = model['path']

        full_model = nbm.get_notebook(name, path)
        nb = full_model['content']
        self.add_code_cell(nb)

        nbm.save_notebook(full_model, name, path)
        return nb, name, path

    def test_create_notebook(self):
        nm = self.notebook_manager
        # Test in root directory
        model = nm.create_notebook()
        assert isinstance(model, dict)
        self.assertIn('name', model)
        self.assertIn('path', model)
        self.assertEqual(model['name'], 'Untitled0.ipynb')
        self.assertEqual(model['path'], '')

        # Test in sub-directory
        sub_dir = '/foo/'
        model = nm.create_notebook(None, sub_dir)
        assert isinstance(model, dict)
        self.assertIn('name', model)
        self.assertIn('path', model)
        self.assertEqual(model['name'], 'Untitled0.ipynb')
        self.assertEqual(model['path'], sub_dir.strip('/'))

    def test_get_notebook(self):
        nm = self.notebook_manager
        # Create a notebook
        model = nm.create_notebook()
        name = model['name']
        path = model['path']

        # Check that we 'get' on the notebook we just created
        model2 = nm.get_notebook(name, path)
        assert isinstance(model2, dict)
        self.assertIn('name', model2)
        self.assertIn('path', model2)
        self.assertEqual(model['name'], name)
        self.assertEqual(model['path'], path)

        # Test in sub-directory
        sub_dir = '/foo/'
        model = nm.create_notebook(None, sub_dir)
        model2 = nm.get_notebook(name, sub_dir)
        assert isinstance(model2, dict)
        self.assertIn('name', model2)
        self.assertIn('path', model2)
        self.assertIn('content', model2)
        self.assertEqual(model2['name'], 'Untitled0.ipynb')
        self.assertEqual(model2['path'], sub_dir.strip('/'))

    def test_update_notebook(self):
        nm = self.notebook_manager
        # Create a notebook
        model = nm.create_notebook()
        name = model['name']
        path = model['path']

        # Change the name in the model for rename
        model['name'] = 'test.ipynb'
        model = nm.update_notebook(model, name, path)
        assert isinstance(model, dict)
        self.assertIn('name', model)
        self.assertIn('path', model)
        self.assertEqual(model['name'], 'test.ipynb')

        # Make sure the old name is gone
        self.assertRaises(HTTPError, nm.get_notebook, name, path)

        # Test in sub-directory
        # Create a directory and notebook in that directory
        sub_dir = '/foo/'
        model = nm.create_notebook(None, sub_dir)
        name = model['name']
        path = model['path']

        # Change the name in the model for rename
        model['name'] = 'test_in_sub.ipynb'
        model = nm.update_notebook(model, name, path)
        assert isinstance(model, dict)
        self.assertIn('name', model)
        self.assertIn('path', model)
        self.assertEqual(model['name'], 'test_in_sub.ipynb')
        self.assertEqual(model['path'], sub_dir.strip('/'))

        # Make sure the old name is gone
        self.assertRaises(HTTPError, nm.get_notebook, name, path)

    def test_save_notebook(self):
        nm = self.notebook_manager
        # Create a notebook
        model = nm.create_notebook()
        name = model['name']
        path = model['path']

        # Get the model with 'content'
        full_model = nm.get_notebook(name, path)

        # Save the notebook
        model = nm.save_notebook(full_model, name, path)
        assert isinstance(model, dict)
        self.assertIn('name', model)
        self.assertIn('path', model)
        self.assertEqual(model['name'], name)
        self.assertEqual(model['path'], path)

        # Test in sub-directory
        # Create a directory and notebook in that directory
        sub_dir = '/foo/'
        model = nm.create_notebook(None, sub_dir)
        name = model['name']
        path = model['path']
        model = nm.get_notebook(name, path)

        # Change the name in the model for rename
        model = nm.save_notebook(model, name, path)
        assert isinstance(model, dict)
        self.assertIn('name', model)
        self.assertIn('path', model)
        self.assertEqual(model['name'], 'Untitled0.ipynb')
        self.assertEqual(model['path'], sub_dir.strip('/'))

    def test_delete_notebook(self):
        nm = self.notebook_manager
        # Create a notebook
        nb, name, path = self.new_notebook()

        # Delete the notebook
        nm.delete_notebook(name, path)

        # Check that a 'get' on the deleted notebook raises and error
        self.assertRaises(HTTPError, nm.get_notebook, name, path)

    def test_copy_notebook(self):
        nm = self.notebook_manager
        path = u'å b'
        name = u'nb √.ipynb'
        orig = nm.create_notebook({'name': name}, path=path)

        # copy with unspecified name
        copy = nm.copy_notebook(name, path=path)
        self.assertEqual(
            copy['name'], orig['name'].replace('.ipynb', '-Copy0.ipynb'))

        # copy with specified name
        copy2 = nm.copy_notebook(name, u'copy 2.ipynb', path=path)
        self.assertEqual(copy2['name'], u'copy 2.ipynb')

    def test_trust_notebook(self):
        nbm = self.notebook_manager
        nb, name, path = self.new_notebook()

        untrusted = nbm.get_notebook(name, path)['content']
        assert not nbm.notary.check_cells(untrusted)

        # print(untrusted)
        nbm.trust_notebook(name, path)
        trusted = nbm.get_notebook(name, path)['content']
        # print(trusted)
        assert nbm.notary.check_cells(trusted)

    def test_mark_trusted_cells(self):
        nbm = self.notebook_manager
        nb, name, path = self.new_notebook()

        nbm.mark_trusted_cells(nb, name, path)
        for cell in nb.worksheets[0].cells:
            if cell.cell_type == 'code':
                assert not cell.trusted

        nbm.trust_notebook(name, path)
        nb = nbm.get_notebook(name, path)['content']
        for cell in nb.worksheets[0].cells:
            if cell.cell_type == 'code':
                assert cell.trusted

    def test_check_and_sign(self):
        nbm = self.notebook_manager
        nb, name, path = self.new_notebook()

        nbm.mark_trusted_cells(nb, name, path)
        nbm.check_and_sign(nb, name, path)
        assert not nbm.notary.check_signature(nb)

        nbm.trust_notebook(name, path)
        nb = nbm.get_notebook(name, path)['content']
        nbm.mark_trusted_cells(nb, name, path)
        nbm.check_and_sign(nb, name, path)
        assert nbm.notary.check_signature(nb)
