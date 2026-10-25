from collections.abc import Callable
from functools import partial

from neko2020.application.ports import (
    IConfigProvider,
    ICursorProvider,
    IRenderer,
)
from neko2020.application.settings import AppSettings
from neko2020.domain.state_machine import NekoStateMachine
from neko2020.domain.value_objects import Point, Rect


type SessionFactory = Callable[
    [AppSettings], tuple[NekoStateMachine, IRenderer]
]
type Scheduler = Callable[[int, Callable[[], None]], None]


class AnimationService:
    def __init__(
        self,
        config: IConfigProvider,
        cursor: ICursorProvider,
        session_factory: SessionFactory,
        scheduler: Scheduler,
        monitors: list[Rect],
    ):
        self._config = config
        self._cursor = cursor
        self._session_factory = session_factory
        self._scheduler = scheduler
        self._monitors = monitors
        self._settings: AppSettings | None = None
        self._state_machine: NekoStateMachine | None = None
        self._renderer: IRenderer | None = None
        self._stopped = True
        # Bumped on every start/stop so a tick scheduled by an earlier
        # session can tell it is stale and end its chain.
        self._generation = 0

    def _delay_ms(self) -> int:
        return 1000 // self._settings.fps

    def _monitor_for(self, cursor: Point) -> Rect:
        for m in self._monitors:
            if m.left <= cursor.x < m.right and m.top <= cursor.y < m.bottom:
                return m
        return self._monitors[0]

    def start(self) -> None:
        if not self._stopped:
            return
        self._stopped = False
        self._generation += 1
        self._config.reload()
        self._settings = AppSettings.from_config(self._config)
        self._state_machine, self._renderer = self._session_factory(
            self._settings
        )
        self._tick(self._generation)

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._generation += 1
        # keep the application running while idle
        self._scheduler(self._delay_ms(), self._idle_pump)

    def restart(self) -> None:
        self.stop()
        self.start()

    def _tick(self, generation: int) -> None:
        if generation != self._generation:
            return
        cursor_pos = self._cursor.get_cursor_position()
        result = self._state_machine.tick(
            cursor_pos,
            self._renderer.get_position(),
            self._renderer.get_size(),
            self._monitor_for(cursor_pos),
        )
        self._renderer.render(result.state, result.phase, result.x, result.y)
        self._scheduler(self._delay_ms(), partial(self._tick, generation))

    def _idle_pump(self) -> None:
        if not self._stopped:
            return
        self._scheduler(self._delay_ms(), self._idle_pump)
