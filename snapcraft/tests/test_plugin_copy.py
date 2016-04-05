# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2015 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
from unittest.mock import Mock

from snapcraft.plugins.copy import (
    CopyPlugin,
    _recursively_link
)
from snapcraft.tests import TestCase


class TestCopyPlugin(TestCase):

    def setUp(self):
        super().setUp()
        self.mock_options = Mock()
        self.mock_options.source = '.'
        self.mock_options.source_subdir = None
        self.mock_options.files = {}
        # setup the expected target dir in our tempdir
        self.dst_prefix = 'parts/copy/install/'
        os.makedirs(self.dst_prefix)

    def test_copy_plugin_any_missing_src_raises_exception(self):
        # ensure that a bad file causes a warning and fails the build even
        # if there is a good file last
        self.mock_options.files = {
            'src': 'dst',
            'zzz': 'zzz',
        }
        open('zzz', 'w').close()
        c = CopyPlugin('copy', self.mock_options)
        c.pull()

        with self.assertRaises(EnvironmentError) as raised:
            c.build()

        self.assertEqual(
            str(raised.exception),
            "[Errno 2] No such file or directory: '{}/src'".format(
                c.builddir))

    def test_copy_glob_does_not_match_anything(self):
        # ensure that a bad file causes a warning and fails the build even
        # if there is a good file last
        self.mock_options.files = {
            'src*': 'dst',
        }
        c = CopyPlugin('copy', self.mock_options)
        c.pull()

        with self.assertRaises(EnvironmentError) as raised:
            c.build()

        self.assertEqual(raised.exception.__str__(), "no matches for 'src*'")

    def test_copy_plugin_copies(self):
        self.mock_options.files = {
            'src': 'dst',
        }
        open('src', 'w').close()

        c = CopyPlugin('copy', self.mock_options)
        c.pull()
        c.build()
        self.assertTrue(os.path.exists(os.path.join(self.dst_prefix, 'dst')))

    def test_copy_plugin_handles_leading_slash(self):
        self.mock_options.files = {
            'src': '/dst',
        }
        open('src', 'w').close()

        c = CopyPlugin('copy', self.mock_options)
        c.pull()
        c.build()
        self.assertTrue(os.path.exists(os.path.join(self.dst_prefix, 'dst')))

    def test_copy_plugin_handles_dot(self):
        self.mock_options.files = {
            'src': '.',
        }
        open('src', 'w').close()

        c = CopyPlugin('copy', self.mock_options)
        c.pull()
        c.build()
        self.assertTrue(os.path.exists(os.path.join(self.dst_prefix, 'src')))

    def test_copy_plugin_creates_prefixes(self):
        self.mock_options.files = {
            'src': 'dir/dst',
        }
        open('src', 'w').close()

        c = CopyPlugin('copy', self.mock_options)
        c.pull()
        c.build()
        self.assertTrue(os.path.exists(os.path.join(self.dst_prefix,
                                                    'dir/dst')))

    def test_copy_directories(self):
        self.mock_options.files = {
            'dirs1': 'dir/dst',
        }
        os.mkdir('dirs1')
        file = os.path.join('dirs1', 'f')
        open(file, 'w').close()

        c = CopyPlugin('copy', self.mock_options)
        c.pull()
        c.build()
        self.assertTrue(
            os.path.exists(os.path.join(self.dst_prefix, 'dir', 'dst', 'f')))

    def test_copy_plugin_glob(self):
        self.mock_options.files = {
            '*.txt': '.',
        }

        for filename in ('file-a.txt', 'file-b.txt', 'file-c.notxt'):
            with open(filename, 'w') as datafile:
                datafile.write(filename)

        c = CopyPlugin('copy', self.mock_options)
        c.pull()
        c.build()

        self.assertTrue(os.path.exists(
            os.path.join(self.dst_prefix, 'file-a.txt')))
        self.assertTrue(os.path.exists(
            os.path.join(self.dst_prefix, 'file-b.txt')))
        self.assertFalse(os.path.exists(
            os.path.join(self.dst_prefix, 'file-c.notxt')))

    def test_copy_plugin_glob_with_folders(self):
        self.mock_options.files = {
            'foo/*': '.',
        }

        os.makedirs(os.path.join('foo', 'directory'))
        open(os.path.join('foo', 'file1'), 'w').close()
        open(os.path.join('foo', 'directory', 'file2'), 'w').close()

        c = CopyPlugin('copy', self.mock_options)
        c.pull()
        c.build()

        self.assertTrue(os.path.isfile(os.path.join(c.installdir, 'file1')))
        self.assertTrue(os.path.isdir(os.path.join(c.installdir, 'directory')))
        self.assertTrue(os.path.isfile(
            os.path.join(c.installdir, 'directory', 'file2')))

    def test_copy_with_source(self):
        self.mock_options.source = 'src'
        self.mock_options.files = {'foo/bar': 'baz/qux'}

        c = CopyPlugin('copy', self.mock_options)
        os.makedirs(os.path.join('src', 'foo'))
        open(os.path.join('src', 'foo', 'bar'), 'w').close()

        c.pull()
        self.assertTrue(
            os.path.isfile(os.path.join(c.sourcedir, 'foo', 'bar')))

        c.build()
        self.assertTrue(os.path.isfile(os.path.join(c.builddir, 'foo', 'bar')))
        self.assertTrue(
            os.path.isfile(os.path.join(c.installdir, 'baz', 'qux')))

    def test_copy_with_source_and_glob(self):
        self.mock_options.source = 'src'
        self.mock_options.files = {'foo/*': 'baz/'}

        c = CopyPlugin('copy', self.mock_options)
        os.makedirs(os.path.join('src', 'foo'))
        open(os.path.join('src', 'foo', 'bar'), 'w').close()

        c.pull()
        self.assertTrue(
            os.path.isfile(os.path.join(c.sourcedir, 'foo', 'bar')))

        c.build()
        self.assertTrue(os.path.isfile(os.path.join(c.builddir, 'foo', 'bar')))
        self.assertTrue(
            os.path.isfile(os.path.join(c.installdir, 'baz', 'bar')))

    def test_copy_with_source_doesnt_use_cwd(self):
        self.mock_options.source = 'src'
        self.mock_options.files = {'foo/bar': 'baz/qux'}

        c = CopyPlugin('copy', self.mock_options)
        os.mkdir('src')
        os.mkdir('foo')
        open(os.path.join('foo', 'bar'), 'w').close()

        c.pull()

        with self.assertRaises(EnvironmentError) as raised:
            c.build()

        self.assertEqual(
            str(raised.exception),
            "[Errno 2] No such file or directory: '{}/foo/bar'".format(
                c.builddir))


class TestRecursivelyLink(TestCase):

    def setUp(self):
        super().setUp()

        os.makedirs('foo/bar/baz')
        open('1', 'w').close()
        open(os.path.join('foo', '2'), 'w').close()
        open(os.path.join('foo', 'bar', '3'), 'w').close()
        open(os.path.join('foo', 'bar', 'baz', '4'), 'w').close()

    def test_recursively_link_file_to_file(self):
        _recursively_link('1', 'qux')
        self.assertTrue(os.path.isfile('qux'))

    def test_recursively_link_file_into_directory(self):
        os.mkdir('qux')
        _recursively_link('1', 'qux')
        self.assertTrue(os.path.isfile(os.path.join('qux', '1')))

    def test_recursively_link_directory_to_directory(self):
        _recursively_link('foo', 'qux')
        self.assertTrue(os.path.isfile(os.path.join('qux', '2')))
        self.assertTrue(os.path.isfile(os.path.join('qux', 'bar', '3')))
        self.assertTrue(os.path.isfile(os.path.join('qux', 'bar', 'baz', '4')))

    def test_recursively_link_directory_into_directory(self):
        os.mkdir('qux')
        _recursively_link('foo', 'qux')
        self.assertTrue(os.path.isfile(os.path.join('qux', 'foo', '2')))
        self.assertTrue(os.path.isfile(os.path.join('qux', 'foo', 'bar', '3')))
        self.assertTrue(
            os.path.isfile(os.path.join('qux', 'foo', 'bar', 'baz', '4')))

    def test_recursively_link_directory_overwrite_file_raises(self):
        open('qux', 'w').close()
        with self.assertRaises(NotADirectoryError) as raised:
            _recursively_link('foo', 'qux')

        self.assertEqual(
            str(raised.exception),
            "Cannot overwrite non-directory 'qux' with directory 'foo'")

    def test_recursively_link_subtree(self):
        _recursively_link('foo/bar', 'qux')
        self.assertTrue(os.path.isfile(os.path.join('qux', '3')))
        self.assertTrue(os.path.isfile(os.path.join('qux', 'baz', '4')))
