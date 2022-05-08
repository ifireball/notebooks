"""Protocols for bouncing ball displays."""
from typing import Protocol, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class BallScreen(Protocol):
    """Defines a screen for displaying bouncing balls."""

    @property
    @abstractmethod
    def screen_width(self) -> int:
        """Return the screen width."""

    @property
    @abstractmethod
    def screen_height(self) -> int:
        """Return the screen height."""

    @property
    @abstractmethod
    def should_stop(self) -> bool:
        """Return true if screen activity should be stopped.

        (E.g. because app is exiting)
        """

    @abstractmethod
    def draw_ball(self, center_x: int, center_y: int, size: int) -> None:
        """Draw a ball at the given coordiantes."""

    @abstractmethod
    def clear(self) -> None:
        """Clear the screen for the next frame."""


class AnimationFunc(Protocol):
    """Represent a function that runs the main animation loop."""

    @abstractmethod
    def __call__(self, screen: BallScreen) -> None:
        """Call to run the main animation loop."""
