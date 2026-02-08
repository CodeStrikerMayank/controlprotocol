from rich.console import Console
from rich.live import Live
from rich.panel import Panel
import time
from rich.align import Align

console = Console()
import sys

def terminate():
    with Live(console=console, refresh_per_second=1) as live:
        frames = [
            "😎 Hold on... wrapping things up",
            "🔻 Terminating program",
            "🔻 Terminating program .",
            "🔻 Terminating program ..",
            "🔻 Terminating program ..."
        ]
        for frame in frames:
            live.update(
                Align.center(
                    Panel(
                        frame,
                        style="bright_green",
                        border_style="black"
                    )
                )
            )
            time.sleep(1.8)
    sys.exit()

def loading():
    with Live(console=console, refresh_per_second=1) as live:
        messages = [
            "Please wait…",
            "Initializing interface",
            "Loading modules",
            "Finalizing setup",
            "Ready"
        ]

        bar = "▮"
        for i in range(5):
            live.update(
                Align.center(
                    Panel(
                        f"{messages[i]}\n[{bar}]",
                        style="bright_green",
                        border_style="black"
                    )
                )
            )
            time.sleep(1)
            bar += "▮"
def dots_wave(duration=6):
    frames = [
        "● ○ ○",
        "○ ● ○",
        "○ ○ ●",
        "○ ● ○",
    ]

    with Live(console=console, refresh_per_second=4) as live:
        for _ in range(duration * 4):
            frame = frames[_ % len(frames)]
            live.update(
                Align.center(
                    Panel(
                        f"[bright_green]{frame}[/]",
                        border_style="green"
                    )
                )
            )
            time.sleep(0.25)
