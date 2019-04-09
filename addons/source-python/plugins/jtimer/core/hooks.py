"""Module for hooking in-game events."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
import os
from threading import Thread

# Source.Python Imports
from listeners import (
    OnTick,
    OnClientActive,
    OnClientDisconnect,
    OnLevelInit,
    OnLevelEnd,
)
from events import Event
from events.hooks import PreEvent, EventAction
from players.helpers import playerinfo_from_index
from steam import SteamID
from cvars import ConVar
from engines.server import server
from engines.sound import engine_sound
from memory import DataType, Convention, get_object_pointer
from memory.hooks import PreHook

# Custom Imports
from .timer.timer import Timer
from .helpers.utils import is_player, get_players
from .helpers.converts import userid_to_player
from .players.player import Player
from .map.map import Map
from .players.state import PlayerClass

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
emit_sound_offset = 4 if os.name == "nt" else 5

""" CEngineSoundServer::EmitSound(
        IRecipientFilter&,
        int,
        int,
        char const*,
        float,
        soundlevel_t,
        int,
        int,
        int,
        Vector const*,
        Vector const*,
        CUtlVector<Vector, CUtlMemory<Vector, int> >*,
        bool,
        float,
        int
    )"""

EMIT_SOUND_FUNC = get_object_pointer(engine_sound).make_virtual_function(
    emit_sound_offset,
    Convention.THISCALL,
    (
        DataType.POINTER,  # this pointer
        DataType.POINTER,
        DataType.INT,
        DataType.INT,
        DataType.STRING,
        DataType.FLOAT,
        DataType.USHORT,
        DataType.INT,
        DataType.INT,
        DataType.INT,
        DataType.POINTER,
        DataType.POINTER,
        DataType.POINTER,
        DataType.BOOL,
        DataType.FLOAT,
        DataType.INT,
    ),
    DataType.VOID,
)

blocked_sounds = ["items/regenerate.wav"]

engine_sound.precache_sound("vo/null.wav")

# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def on_level_init(level):
    """Called when a new map is loaded."""
    Timer.instance().clear()
    Map.get_map()
    for player in get_players():
        Player.add_player(player.playerinfo, player.index)


@OnLevelEnd
def on_level_end():
    """Called when a map is unloaded."""
    Timer.instance().clear()


@OnTick
def on_tick():
    """Called every engine tick."""
    Timer.instance().update_timers()
    if server.tick % 67 == 0:
        if Timer.instance().current_map:
            Timer.instance().current_map.start_zone.draw()
            Timer.instance().current_map.end_zone.draw()
            for checkpoint in Timer.instance().current_map.checkpoints:
                checkpoint.draw()


@OnClientActive
def on_client_active(index):
    """Called when a client has fully joined the game."""
    playerinfo = playerinfo_from_index(index)
    if is_player(playerinfo):
        Thread(target=Player.add_player, args=(playerinfo, index)).start()
    else:
        return


@OnClientDisconnect
def on_client_disconnect(index):
    """Called when a client leaves the game."""
    playerinfo = playerinfo_from_index(index)
    if is_player(playerinfo):
        Timer.instance().remove_player(SteamID.parse(playerinfo.steamid).to_steamid2())
    else:
        return


# =============================================================================
# >> PRE-EVENTS
# =============================================================================
@PreEvent("player_death")
def pre_player_death(game_event):
    """Called before a player dies."""
    # Don't broadcast to other players.
    return EventAction.STOP_BROADCAST


@PreEvent("player_team")
def pre_player_team(game_event):
    """Called before a player joins a team."""
    # Don't broadcast to other players.
    return EventAction.STOP_BROADCAST


# =============================================================================
# >> EVENTS
# =============================================================================
@Event("player_spawn")
def on_player_spawn(game_event):
    """Called when a player spawns."""
    cancel_wait = ConVar(name="mp_waitingforplayers_cancel")
    cancel_wait.set_bool(True)

    player = userid_to_player(game_event["userid"])
    if player is not None:
        class_index = game_event["class"]
        player.state.player_class = PlayerClass(class_index)
        player.start()


@Event("player_death")
def on_player_death(game_event):
    """Called when a player dies."""
    player = userid_to_player(game_event["userid"])
    player.state.reset()


# =============================================================================
# >> VIRTUAL FUNCTIONS
# =============================================================================
@PreHook(EMIT_SOUND_FUNC)
def pre_emit_sound(args):
    """Called before a sound is emitted."""

    if args[4] in blocked_sounds:
        args[4] = "vo/null.wav"