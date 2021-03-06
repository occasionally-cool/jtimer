"""Main module for jtimer plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python imports
from commands.typed import TypedSayCommand
from commands import CommandReturn
from players.helpers import playerinfo_from_index
from steam import SteamID

# Custom imports
from .core.timer.timer import Timer
from .core.helpers.converts import steamid_to_player
from .core.helpers.utils import is_player
from .core.map.map import Map
from .core.api.auth import on_load as auth_on_load, on_unload as auth_on_unload
from .core.hooks import *
from .core.commands.commands import register_commands

# =============================================================================
# >> FUNCTIONS
# =============================================================================
def load():
    """Called when Source.Python loads the plugin."""
    Map.get_map()
    auth_on_load()
    register_commands()
    print(f"[jtimer] Loaded!")


def unload():
    """Called when Source.Python unloads the plugin."""
    auth_on_unload()
    print(f"[jtimer] Unloaded!")
