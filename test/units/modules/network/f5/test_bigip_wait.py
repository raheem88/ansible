# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
import sys

from nose.plugins.skip import SkipTest
if sys.version_info < (2, 7):
    raise SkipTest("F5 Ansible modules require Python >= 2.7")

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import Mock
from ansible.compat.tests.mock import patch
from ansible.module_utils.basic import AnsibleModule

try:
    from library.modules.bigip_wait import Parameters
    from library.modules.bigip_wait import ModuleManager
    from library.modules.bigip_wait import ArgumentSpec
    from library.module_utils.network.f5.common import F5ModuleError
    from library.module_utils.network.f5.common import iControlUnexpectedHTTPError
    from test.unit.modules.utils import set_module_args
except ImportError:
    try:
        from ansible.modules.network.f5.bigip_wait import Parameters
        from ansible.modules.network.f5.bigip_wait import ModuleManager
        from ansible.modules.network.f5.bigip_wait import ArgumentSpec
        from ansible.module_utils.network.f5.common import F5ModuleError
        from ansible.module_utils.network.f5.common import iControlUnexpectedHTTPError
        from units.modules.utils import set_module_args
    except ImportError:
        raise SkipTest("F5 Ansible modules require the f5-sdk Python library")

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            delay=3,
            timeout=500,
            sleep=10,
            msg='We timed out during waiting for BIG-IP :-('
        )

        p = Parameters(params=args)
        assert p.delay == 3
        assert p.timeout == 500
        assert p.sleep == 10
        assert p.msg == 'We timed out during waiting for BIG-IP :-('

    def test_module_string_parameters(self):
        args = dict(
            delay='3',
            timeout='500',
            sleep='10',
            msg='We timed out during waiting for BIG-IP :-('
        )

        p = Parameters(params=args)
        assert p.delay == 3
        assert p.timeout == 500
        assert p.sleep == 10
        assert p.msg == 'We timed out during waiting for BIG-IP :-('


class TestManager(unittest.TestCase):
    def setUp(self):
        self.spec = ArgumentSpec()
        self.patcher1 = patch('time.sleep')
        self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_wait_already_available(self, *args):
        set_module_args(dict(
            password='passsword',
            server='localhost',
            user='admin'
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )

        # Override methods to force specific logic in the module to happen
        mm = ModuleManager(module=module)
        mm._connect_to_device = Mock(return_value=True)
        mm._device_is_rebooting = Mock(return_value=False)
        mm._is_mprov_running_on_device = Mock(return_value=False)
        mm._get_client_connection = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is False
        assert results['elapsed'] == 0
