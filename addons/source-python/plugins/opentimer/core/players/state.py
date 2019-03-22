from enum import Enum
import mathlib
from engines.server import server
from ..timer import timer
from ..hud import hud


class State:
    def __init__(self, player):
        self.player_reference = player
        self.player_class = Player_Class.NONE

        self.origin = mathlib.NULL_VECTOR
        self.center = mathlib.NULL_VECTOR
        self.extents = mathlib.NULL_VECTOR
        self.bounds = [mathlib.NULL_VECTOR, mathlib.NULL_VECTOR]
        self.velocity = mathlib.NULL_VECTOR

        self.previous_origin = self.origin
        self.previous_center = self.center
        self.previous_extents = self.extents
        self.previous_bounds = self.bounds
        self.previous_velocity = self.velocity

        self.timer_mode = Timer_Mode.NONE
        self.map_state = Run_State.NONE
        self.course_state = Run_State.NONE
        self.bonus_state = Run_State.NONE

        # (Segment, start_time, end_time)
        self.checkpoints = []
        self.courses = []
        self.course_index = 0
        self.bonus = [None, None, None]
        self.bonus_index = 0
        self.map = [None, None, None]
        self.overlaps = []

    def reset(self):
        self.checkpoints = []
        self.courses = []
        self.bonus = [None, None, None]
        self.map = [None, None, None]
        self.bonus_index = 0
        self.course_index = 0
        self.overlaps = []

        self.origin = mathlib.NULL_VECTOR
        self.center = mathlib.NULL_VECTOR
        self.extents = mathlib.NULL_VECTOR
        self.bounds = [mathlib.NULL_VECTOR, mathlib.NULL_VECTOR]
        self.velocity = mathlib.NULL_VECTOR

        self.previous_origin = self.origin
        self.previous_center = self.center
        self.previous_bounds = self.bounds
        self.previous_extents = self.extents
        self.previous_velocity = self.velocity

    def running(self):
        if self.timer_mode != Timer_Mode.NONE:
            return True
        return False

    def update(self, origin, vecMinsMaxs, velocity):
        # are we running?
        if self.running:
            if type(origin) != mathlib.Vector:
                print(
                    f"ERR: Trying to update Player State but origin is not Type(mathlib.Vector)!"
                )
                return

            if type(vecMinsMaxs) != mathlib.Vector:
                print(
                    f"ERR: Trying to update Player State but vecMinsMaxs is not Type(mathlib.Vector)!"
                )
                return

            self.previous_origin = self.origin
            self.origin = origin

            self.previous_extents = self.extents
            self.extents = vecMinsMaxs
            self.extents[2] /= 2

            self.previous_bounds = self.bounds
            self.bounds[0] = origin + vecMinsMaxs
            self.bounds[1] = origin - vecMinsMaxs
            self.bounds[1][2] += vecMinsMaxs[2]

            self.previous_center = self.center
            self.center = self.origin
            self.center[2] += vecMinsMaxs[2] / 2

            self.previous_velocity = self.velocity
            self.velocity = velocity

            # first update
            if self.previous_origin == mathlib.NULL_VECTOR:
                return

            to_check = []
            if self.timer_mode == Timer_Mode.MAP:
                to_check.append(timer.current_map)
                to_check.extend(timer.current_map.courses)
            elif self.timer_mode == Timer_Mode.COURSE:
                to_check.append(timer.current_map.courses[self.course_index])
            if self.timer_mode == Timer_Mode.BONUS:
                to_check.append(timer.current_map.bonuses[self.bonus_index])

            for segment in to_check:
                # check start_zone
                if segment.start_zone.is_overlapping(self.center, self.extents):
                    segment.on_enter_start(self.player_reference)
                else:
                    segment.on_leave_start(self.player_reference)

                # check end zone
                if segment.end_zone.is_overlapping(self.center, self.extents):
                    segment.on_enter_end(self.player_reference)

                # check checkpoints
                for cp in segment.checkpoints:
                    if cp.is_overlapping(self.center, self.extents):
                        segment.on_enter_checkpoint(self.player_reference, cp)

        # update hud every half a second
        if server.tick % 33 == 0:
            hud.draw_timer(self.player_reference)


class Run_State(Enum):
    NONE = 0
    START = (1,)
    RUN = (2,)
    END = 3


class Timer_Mode(Enum):
    NONE = 0
    MAP = 1
    COURSE = 2
    BONUS = 3


class Player_Class(Enum):
    NONE = (0,)
    SCOUT = (1,)
    SOLDIER = (2,)
    PYRO = (3,)
    DEMOMAN = (4,)
    HEAVY = (5,)
    ENGINEER = (6,)
    MEDIC = (7,)
    SNIPER = (8,)
    SPY = 9
