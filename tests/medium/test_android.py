# -*- coding: utf-8 -*-
# Copyright (C) 2014 Canonical
#
# Authors:
#  Didier Roche
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""Tests for basic CLI commands"""

from . import ContainerTests
import os
import pexpect
from ..large import test_android
from ..tools import get_data_dir, swap_file_and_restore, UMAKE


class AndroidStudioInContainer(ContainerTests, test_android.AndroidStudioTests):
    """This will install Android Studio inside a container"""

    TIMEOUT_START = 20
    TIMEOUT_STOP = 10
    TEST_CHECKSUM_ANDROID_STUDIO_FAKE_DATA = "d8362a0c2ffc07b1b19c4b9001c8532de5a4b8c3"

    def setUp(self):
        self.hostname = "developer.android.com"
        self.port = "443"
        self.apt_repo_override_path = os.path.join(self.APT_FAKE_REPO_PATH, 'android')
        super().setUp()
        # override with container path
        self.installed_path = os.path.expanduser("/home/{}/tools/android/android-studio".format(self.DOCKER_USER))

    # additional test with fake md5sum
    def test_android_studio_install_with_wrong_md5sum(self):
        """Install android studio requires a md5sum, and a wrong one is rejected"""
        android_studio_file_path = os.path.join(get_data_dir(), "server-content", "developer.android.com",
                                                "sdk", "index.html")
        with swap_file_and_restore(android_studio_file_path) as content:
            with open(android_studio_file_path, "w") as newfile:
                newfile.write(content.replace(self.TEST_CHECKSUM_ANDROID_STUDIO_FAKE_DATA,
                                              "c8362a0c2ffc07b1b19c4b9001c8532de5a4b8c3"))
            self.child = pexpect.spawnu(self.command('{} android android-studio'.format(UMAKE)))
            self.expect_and_no_warn("Choose installation path: {}".format(self.installed_path))
            self.child.sendline("")
            self.expect_and_no_warn("\[I Accept.*\]")  # ensure we have a license question
            self.child.sendline("a")
            self.expect_and_no_warn([pexpect.EOF, "Corrupted download? Aborting."],
                                    timeout=self.TIMEOUT_INSTALL_PROGRESS, expect_warn=True)

            # we have nothing installed
            self.assertFalse(self.launcher_exists_and_is_pinned(self.desktop_filename))


class AndroidNDKContainer(ContainerTests, test_android.AndroidNDKTests):
    """This will install Android NDK inside a container"""

    def setUp(self):
        self.hostname = "developer.android.com"
        self.port = "443"
        self.apt_repo_override_path = os.path.join(self.APT_FAKE_REPO_PATH, 'android')
        super().setUp()
        # override with container path
        self.installed_path = os.path.expanduser("/home/{}/tools/android/android-ndk".format(self.DOCKER_USER))
