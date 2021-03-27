from contextlib import contextmanager
import sys

import mock
from modulelib import ModuleWatchdog


@contextmanager
def watchdog(*args, **kwargs):
    ModuleWatchdog.install(*args, **kwargs)

    yield

    ModuleWatchdog.uninstall()


@contextmanager
def unloaded_modules(modules):
    module_loaded = [module in sys.modules for module in modules]
    for module in modules:
        try:
            del sys.modules[module]
        except KeyError:
            pass
        assert module not in sys.modules

    yield

    for module, was_loaded in zip(modules, module_loaded):
        if was_loaded:
            __import__(module)


def test_install_uninstall():
    with watchdog():
        assert isinstance(sys.modules, ModuleWatchdog)
    assert not isinstance(sys.modules, ModuleWatchdog)


def test_hooks():
    on_load = mock.Mock()
    on_unload = mock.Mock()

    with unloaded_modules(["json"]), watchdog(on_load, on_unload):
        assert "json" not in sys.modules
        import json

        assert "json" in sys.modules
        assert json.dumps
        on_load.assert_called_with("json", json)

        del sys.modules["json"]
        assert "json" not in sys.modules
        on_unload.assert_called_with("json")


def test_dict_magic():
    with watchdog():
        assert iter(sys.modules)
        assert len(sys.modules)
        assert list(sys.modules)
        assert sys.modules.keys()


def test_hooks_multiple_installs():
    on_load = mock.Mock()
    on_unload = mock.Mock()

    on_load2 = mock.Mock()
    on_unload2 = mock.Mock()

    with unloaded_modules(["json"]), watchdog(on_load, on_unload), watchdog(
        on_load2, on_unload2
    ):
        assert "json" not in sys.modules
        import json

        assert "json" in sys.modules
        assert json.dumps
        on_load.assert_called_with("json", json)
        on_load2.assert_called_with("json", json)

        del sys.modules["json"]
        assert "json" not in sys.modules
        on_unload.assert_called_with("json")
        on_unload2.assert_called_with("json")


def test_watchdog_context():
    assert not isinstance(sys.modules, ModuleWatchdog)
    with ModuleWatchdog():
        assert isinstance(sys.modules, ModuleWatchdog)
