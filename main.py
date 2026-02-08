from rich.console import Console
from rich.align import Align
from rich.panel import Panel
from rapidfuzz import fuzz
import control
import animation as ad
import os
from datetime import datetime

console = Console()
kit = 75


# ---------------- SAFE INPUT ---------------- #
def safe_input(prompt: str) -> str:
    try:
        return console.input(prompt)
    except (RuntimeError, EOFError):
        console.print("[red]❌ Input stream lost. Exiting.[/red]")
        raise SystemExit


# ---------------- HEADER ---------------- #
def header():
    console.clear()
    now = datetime.now()
    console.print(
        Align.center(
            Panel(
                f"[bold cyan]🛠 CONTROL TOOL[/bold cyan]\n"
                f"[dim]Threshold : {kit} | {now.strftime('%d %b %Y • %H:%M')}[/dim]",
                border_style="bright_cyan",
                width=60,
            )
        )
    )


def status(msg, ok=True):
    color = "green" if ok else "red"
    icon = "✔" if ok else "❌"
    console.print(f"[{color}]{icon} {msg}[/{color}]")


# ---------------- COMMAND FUNCTIONS ---------------- #
def cmd_sort():
    path = safe_input("[green]>>> File path :[/green]")
    path = control.normalize_path(path)
    if path and os.path.exists(path):
        control.organize_files(directory_path=path)
    else:
        status("Invalid path", False)


def cmd_viewfile():
    path = safe_input("[green]>>> File path (Enter for default): [/green]")
    path = control.normalize_path(path)
    control.view_file(file_path=path if path else None)


def cmd_delete():
    path = safe_input("[green]>>> File path :[/green]")
    path = control.normalize_path(path)
    if not path or not os.path.exists(path):
        status("Invalid path", False)
        return
    try:
        days = int(safe_input("[green]Delete files older than days: [/green]"))
        control.delete_old_files(folder_path=path, days=days)
    except ValueError:
        status("Invalid number", False)


def cmd_threshold():
    global kit
    kit = int(safe_input("[green]>>> New Threshold :[/green]"))
    status("Threshold updated")


def cmd_open():
    target = safe_input("[green]>>> Open app/site :[/green]")
    control.open_target(target)


def cmd_sysinfo():
    console.print(control.get_system_info(), style="bright_green")


def cmd_duplicates():
    path = safe_input("[green]>>> File path :[/green]")
    path = control.normalize_path(path)
    if path and os.path.exists(path):
        control.find_duplicates(directory=path)
    else:
        status("Invalid path", False)


def cmd_diskinfo():
    path = safe_input("[green]>>> File path :[/green]")
    path = control.normalize_path(path)
    if path:
        control.disk_usage(path)
    else:
        status("Invalid path", False)


def cmd_tree():
    path = safe_input("[green]>>> Folder or drive path :[/green]")
    path = control.normalize_path(path)
    if path and os.path.exists(path):
        control.show_tree(path=path)
    else:
        status("Invalid path", False)


def cmd_help():
    console.print(control.read1(), style="bright_green")


def cmd_interface():
    interface()
    os.system("cls")
    header()


def cmd_coderinfo():
    os.system("cls")
    control.info()


def cmd_exit():
    ad.terminate()
    raise SystemExit


def cmd_transfer():
    console.print("[bold cyan]📦 FILE TRANSFER TOOL[/bold cyan]\n", style="bold")

    # Get source paths
    console.print(
        "[yellow]Enter source file/folder paths (one per line, empty line to finish):[/yellow]"
    )
    sources = []
    counter = 1
    while True:
        path = safe_input(f"[green]Source {counter}: [/green]")
        path = control.normalize_path(path)
        if not path:
            break
        sources.append(path)
        counter += 1

    if not sources:
        status("No source paths provided", False)
        return

    # Get destination
    dest = safe_input("[green]Destination path: [/green]")
    dest = control.normalize_path(dest)
    if not dest:
        status("No destination provided", False)
        return

    # Confirm transfer
    console.print(
        f"\n[cyan]Transferring {len(sources)} item(s) to: {dest}[/cyan]"
    )
    confirm = safe_input("[yellow]Proceed? (y/n): [/yellow]").lower()

    if confirm == "y":
        control.transfer_files(sources, dest)
    else:
        status("Transfer cancelled", False)


# ---------------- COMMAND MAP ---------------- #
COMMAND_MAP = {
    "sort data": cmd_sort,
    "file clr": cmd_delete,
    "chthress": cmd_threshold,
    "open": cmd_open,
    "sysinfo": cmd_sysinfo,
    "dittocpy": cmd_duplicates,
    "diskinfo": cmd_diskinfo,
    "tree": cmd_tree,
    "view file": cmd_viewfile,
    "transfer": cmd_transfer,
    "help": cmd_help,
    "loadinterface": cmd_interface,
    "coderinfo": cmd_coderinfo,
    "exit": cmd_exit,
}


def match_command(user_input):
    best_cmd, best_score = None, 0
    for cmd in COMMAND_MAP:
        score = fuzz.WRatio(user_input, cmd)
        if score > best_score:
            best_cmd, best_score = cmd, score
    return best_cmd if best_score >= kit else None


# ---------------- MENU INTERFACE ---------------- #
def interface():
    global kit
    while True:
        console.print(
            Align.center(
                Panel(
                    "[bold green]1.[/bold green] Sort Data\n"
                    "[bold green]2.[/bold green] Delete Old Files\n"
                    "[bold green]3.[/bold green] Change Threshold\n"
                    "[bold green]4.[/bold green] Open App / Website\n"
                    "[bold green]5.[/bold green] System Info\n"
                    "[bold green]6.[/bold green] Find Duplicates\n"
                    "[bold green]7.[/bold green] Disk Info\n"
                    "[bold green]8.[/bold green] Directory Tree\n"
                    "[bold green]9.[/bold green] View File\n"
                    "[bold green]10.[/bold green] Transfer Files\n"
                    "[bold green]11.[/bold green] Help Menu\n"
                    "[bold red]0.[/bold red] Exit",
                    title="[bold cyan]Control_Interface[/bold cyan]",
                    border_style="bright_green",
                    width=50,
                )
            )
        )

        choice = safe_input("[green]>>> Select option: [/green]").strip()

        try:
            if choice == "1":
                cmd_sort()
            elif choice == "2":
                cmd_delete()
            elif choice == "3":
                cmd_threshold()
            elif choice == "4":
                cmd_open()
            elif choice == "5":
                cmd_sysinfo()
            elif choice == "6":
                cmd_duplicates()
            elif choice == "7":
                cmd_diskinfo()
            elif choice == "8":
                cmd_tree()
            elif choice == "9":
                cmd_viewfile()
            elif choice == "10":
                cmd_transfer()
            elif choice == "11":
                cmd_help()
            elif choice == "0":
                break
            else:
                status("Invalid option", False)
        except ValueError:
            status("Invalid input", False)


# ---------------- CLI LOOP ---------------- #
def cli():
    header()
    while True:
        try:
            user_input = (
                safe_input(
                    f"[bold green]CLI[/bold green] [cyan](kit={kit})[/cyan] >>> "
                )
                .strip()
                .lower()
            )

            if user_input == "cls":
                os.system("cls")
                header()
                continue

            if user_input in ("quit", "exit", "terminate", "stop"):
                cmd_exit()

            command = match_command(user_input)
            if command:
                COMMAND_MAP[command]()
                status("Operation completed")
            else:
                status("Unknown command", False)
                console.print(
                    "[dim]Try: sort data | open | tree | diskinfo | help[/dim]"
                )

        except SystemExit:
            break
        except ValueError:
            status("Invalid input", False)


# ---------------- START ---------------- #
os.system("cls")
ad.loading()
os.system("cls")
cli()
