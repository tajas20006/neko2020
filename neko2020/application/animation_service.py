import threading
from typing import Callable

from neko2020.application.ports import (
    IConfigProvider,
    ICursorProvider,
    IRenderer,
)
from neko2020.domain.state_machine import NekoStateMachine
from neko2020.domain.value_objects import Point, Rect


SessionFactory = Callable[[], tuple[NekoStateMachine, IRenderer]]
Scheduler = Callable[[int, Callable[[], None]], None]


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
        self._state_machine: NekoStateMachine | None = None
        self._renderer: IRenderer | None = None
        self._stopped = True
        self._stopped_event = threading.Event()
        self._stopped_event.set()

    def _delay_ms(self) -> int:
        return 1000 // self._config.get_int("fps")

    def _monitor_for(self, cursor: Point) -> Rect:
        for m in self._monitors:
            if m.left <= cursor.x < m.right and m.top <= cursor.y < m.bottom:
                return m
        return self._monitors[0]

    def start(self) -> None:
        if not self._stopped:
            return
        self._stopped = False
        self._stopped_event.clear()
        self._config.reload()
        self._state_machine, self._renderer = self._session_factory()
        self._tick()

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        # keep the application running while idle
        self._scheduler(self._delay_ms(), self._idle_pump)

    def restart(self) -> None:
        self.stop()
        self._stopped_event.wait()
        self.start()

    def _tick(self) -> None:
        if self._stopped:
            self._stopped_event.set()
            return
        cursor_pos = self._cursor.get_cursor_position()
        result = self._state_machine.tick(
            cursor_pos,
            self._renderer.get_position(),
            self._renderer.get_size(),
            self._monitor_for(cursor_pos),
        )
        self._renderer.render(result.frame_index, result.x, result.y)
        self._scheduler(self._delay_ms(), self._tick)

    def _idle_pump(self) -> None:
        if not self._stopped:
            return
        self._scheduler(self._delay_ms(), self._idle_pump)
