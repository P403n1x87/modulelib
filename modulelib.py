import sys
from types import ModuleType
from typing import Any, Callable, Iterator, Tuple


def origin(module: ModuleType) -> str:
    """Get the origin of the module."""
    try:
        return module.__file__
    except AttributeError:
        # Module is porbably only partially initialised, so we look at its
        # spec instead
        try:
            return module.__spec__.origin
        except Exception:
            return "<unknown origin>"


class ModuleWatchdog(dict):
    """Module watchdog.

    Allows you to replace the standard ``sys.modules`` dictionary to watch
    for when modules are loaded and unloaded.

    Can be used as a context manager.
    """

    def __init__(
        self,
        on_module_loaded: Callable[[str, ModuleType], None] = None,
        on_module_unloaded: Callable[[str], None] = None,
    ) -> None:
        self._on_load = on_module_loaded
        self._on_unload = on_module_unloaded

        self._modules = sys.modules

    def __enter__(self) -> "ModuleWatchdog":
        sys.modules = self
        return self

    def __exit__(self, *exc: Tuple[Any]) -> None:
        sys.modules = self._modules

    def __getitem__(self, item: str) -> ModuleType:
        return self._modules.__getitem__(item)

    def __setitem__(self, item: str, value: ModuleType) -> None:
        if self._on_load:
            self._on_load(item, value)
        self._modules[item] = value

    def __delitem__(self, item: str) -> None:
        if self._on_unload:
            self._on_unload(item)
        del self._modules[item]

    def __getattribute__(self, name: str) -> Any:
        try:
            return (
                super(ModuleWatchdog, self)
                .__getattribute__("_modules")
                .__getattribute__(name)
            )
        except AttributeError:
            return super(ModuleWatchdog, self).__getattribute__(name)

    def __contains__(self, item: str) -> bool:
        return item in self._modules

    def __len__(self) -> int:
        return len(self._modules)

    def __iter__(self) -> Iterator:
        return iter(self._modules)

    @classmethod
    def install(
        cls,
        on_module_loaded: Callable[[str, ModuleType], None] = None,
        on_module_unloaded: Callable[[str], None] = None,
    ) -> None:
        """Install a module watchdog.

        This class method accepts two optional callbacks. If passed, they get
        called after a module has been loaded or unloaded respectively. Note
        that a call to this method with no callbacks is pretty pointless
        (unless you are planning on adding unnecessary overheads).

        Calls to ``install`` can be nested and, in theory, should be matched
        by the same number of ``uninstall`` to get back to the original
        value for ``sys.modules``.
        """
        sys.modules = cls(on_module_loaded, on_module_unloaded)

    @staticmethod
    def uninstall() -> None:
        """Uninstall the module watchdog."""
        sys.modules = sys.modules._modules
