# This suppresses about 80% of the deprecation warnings from python 3.7.
import warnings

import yaml

# see example https://github.com/gswallow/molecule_example

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    import testinfra.utils.ansible_runner
    import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('name', [
    'python3',
    'python3-venv',
    'python3-pip'
])
def test_package(host, name):
    p = host.package(name)

    assert p.is_installed


def test_config(host):
    # all_variables = host.ansible.get_variables()
    # app_path = all_variables['application_path']
    app_path = '/home/telegram-bot/webmtogif'
    f = host.file(f'{app_path}/config/config.yml')
    assert f.is_file

    d = yaml.load(f.content)

    assert d['token']
    assert d['pikabu_cookies']


def test_service(host):
    s = host.service('webmtogif')
    # assert s.is_enabled
    # assert s.is_valid
    assert s.is_running
