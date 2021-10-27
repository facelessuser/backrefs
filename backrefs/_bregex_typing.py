"""Typing objects for the Regex library."""
from typing import Mapping, Union, Generic, Tuple, Optional, Set, List, Iterator, Callable, Any, AnyStr


class Pattern(Generic[AnyStr]):
    """
    Pattern type for the Regex library.

    Only specify what we need to.
    """

    pattern: AnyStr
    flags: int
    groupindex: Mapping[str, int]
    groups: Tuple[Optional[AnyStr], ...]
    named_lists: Mapping[str, Set[Union[str, bytes]]]
    scanner: Any

    def search(self, string: AnyStr, *args: Any, **kwargs: Any) -> 'Optional[Match[AnyStr]]':
        """Search."""

    def match(self, string: AnyStr, *args: Any, **kwargs: Any) -> 'Optional[Match[AnyStr]]':
        """Match."""

    def fullmatch(self, string: AnyStr, *args: Any, **kwargs: Any) -> 'Optional[Match[AnyStr]]':
        """Full match."""

    def split(self, string: AnyStr, *args: Any, **kwargs: Any) -> List[AnyStr]:
        """Split."""

    def splititer(self, string: AnyStr, *args: Any, **kwargs: Any) -> Iterator[AnyStr]:
        """Split as iterator."""

    def findall(self, string: AnyStr, *args: Any, **kwargs: Any) -> Union[List[AnyStr], List[Tuple[AnyStr, ...]]]:
        """Find all."""

    def finditer(self, string: AnyStr, *args: Any, **kwargs: Any) -> Iterator['Match[AnyStr]']:
        """Find as iterator."""

    def sub(self, repl: Union[AnyStr, Callable[..., AnyStr]], string: AnyStr, *args: Any, **kwargs: Any) -> AnyStr:
        """Substitute."""

    def subf(self, repl: Union[AnyStr, Callable[..., AnyStr]], string: AnyStr, *args: Any, **kwargs: Any) -> AnyStr:
        """Substitute with format string."""

    def subn(
        self, repl: Union[AnyStr, Callable[..., AnyStr]], string: AnyStr, *args: Any, **kwargs: Any
    ) -> Tuple[AnyStr, int]:
        """Substitute and return replacement count."""

    def subfn(
        self, repl: Union[AnyStr, Callable[..., AnyStr]], string: AnyStr, *args: Any, **kwargs: Any
    ) -> Tuple[AnyStr, int]:
        """Substitute with format string and return replacement count."""


class Match(Generic[AnyStr]):
    """
    Match type for the Regex library.

    Only specify what we need to.
    """

    re: Pattern[AnyStr]
    string: Optional[AnyStr]
    pos: int
    endpos: int
    regs: Tuple[Tuple[int, int], ...]
    lastindex: int
    fuzzy_counts: Tuple[int, ...]
    fuzzy_changes: Tuple[List[int], ...]
    lastgroup: Optional[str]
    partial: bool

    def group(self, *index: Union[str, int]) -> Union[Optional[AnyStr], Tuple[Optional[AnyStr], ...]]:
        """Get group."""

    def groups(self, default: Optional[Any] = None) -> Union[AnyStr, Optional[Any]]:
        """Get groups."""

    def groupdict(self, default: Optional[Any] = None) -> Mapping[str, Optional[Any]]:
        """Get group dictionary."""

    def captures(self, *index: Union[str, int]) -> Union[List[AnyStr], Tuple[List[AnyStr], ...]]:
        """Get captures."""

    def capturesdict(self) -> Mapping[str, List[AnyStr]]:
        """Get captures dictionary."""

    def start(self, *index: Union[str, int]) -> Union[int, Tuple[int, ...]]:
        """Get start position by group."""

    def end(self, *index: Union[str, int]) -> Union[int, Tuple[int, ...]]:
        """Get end position by group."""

    def detach_string(self) -> None:
        """Detach string."""

    def span(self, *index: Union[str, int]) -> Union[Tuple[int, int], Tuple[Tuple[int, int], ...]]:
        """Return span of groups."""

    def spans(self, *index: Union[str, int]) -> Union[List[Tuple[int, int]], Tuple[List[Tuple[int, int]], ...]]:
        """Return span of groups."""

    def expand(self, template: AnyStr) -> AnyStr:
        """Expand replacement template."""

    def expandf(self, template: AnyStr) -> AnyStr:
        """Expand format replacement template."""
