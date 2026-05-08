import time
from typing import Callable

from neko2020.application.ports import (
    IConfigProvider,
    ICursorProvider,
    IRenderer,
)
from neko2020.domain.state_machine import NekoStateMachine


SessionFactory = Callable[[], tuple[NekoStateMachine, IRenderer]]
Scheduler = Callable[[int, Callable[[], None]], None]


class AnimationService:
    def __init__(
        self,
        config: IConfigProvider,
        cursor: ICursorProvider,
        session_factory: SessionFactory,
        scheduler: Scheduler,
    ):
        self._config = config
        self._cursor = cursor
        self._session_factory = session_factory
        self._scheduler = scheduler
        self._state_machine: NekoStateMachine | None = None
        self._renderer: IRenderer | None = None
        self._stopped = True

    def _delay_ms(self) -> int:
        return 1000 // self._config.get_int("fps")

    def start(self) -> None:
        if not self._stopped:
            return
        self._stopped = False
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
        delay = self._delay_ms()
        self.stop()
        # let the old tick chain settle before starting fresh
        time.sleep(2 * delay / 1000)
        self.start()

    def _tick(self) -> None:
        if self._stopped:
            return
        cursor_pos = self._cursor.get_cursor_position()
        result = self._state_machine.tick(
            cursor_pos,
            self._renderer.get_position(),
            self._renderer.get_size(),
            self._renderer.get_bounds(),
        )
        self._renderer.render(result.frame_index, result.x, result.y)
        self._scheduler(self._delay_ms(), self._tick)

    def _idle_pump(self) -> None:
        if not self._stopped:
            return
        self._scheduler(self._delay_ms(), self._idle_pump)
