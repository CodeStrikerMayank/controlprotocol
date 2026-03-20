import os
import shutil
import time
import platform
import psutil
import hashlib
import json
import webbrowser
import subprocess
import sys
from rich.console import Console
from rich.style import Style
from rich.tree import Tree
from tabulate import tabulate
import pandas as pd

console = Console()

_orig_input = input


def _safe_input(prompt=""):
    try:
        return _orig_input(prompt)
    except (RuntimeError, EOFError):
        return ""


console.input = _safe_input


def open_target(target):
    target = target.strip()

    if target.startswith(("http://", "https://", "www.")):
        if target.startswith("www."):
            target = "https://" + target
        webbrowser.open(target)
        print("🌐 Website opened")
        return

    try:
        subprocess.Popen(target, shell=True)
        print("🖥️ Application opened")
        return
    except Exception:
        print("❌ Cannot open app or site")

    try:
        subprocess.Popen(target, shell=True)
        print("🖥️ Application opened")
        return
    except Exception:
        pass

    print("❌ Not a valid website or application")


console = Console()


def resource_path(rel_path):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, rel_path)


def normalize_path(user_input):
    """
    Normalize user input path:
    - Remove surrounding quotes (single or double)
    - Expand ~ to home directory
    - Strip whitespace
    - Convert to absolute path
    """
    if not user_input:
        return ""

    path = user_input.strip()
    if (path.startswith('"') and path.endswith('"')) or (
        path.startswith("'") and path.endswith("'")
    ):
        path = path[1:-1]

    path = path.strip()

    path = os.path.expanduser(path)

    path = os.path.abspath(path)

    return path


def read1():
    head = ["COMMANDS", "DESCRIPTION"]
    try:
        df = pd.read_csv(resource_path("dat.csv"), header=None, names=head)
        return tabulate(df, headers=head, tablefmt="grid")
    except FileNotFoundError:
        console.print("❌ dat.csv not found", style="bold red")
        return ""
    except Exception as e:
        console.print(f"❌ Error reading dat.csv: {e}", style="bold red")
        return ""


def organize_files(directory_path):
    try:
        if not os.path.exists(directory_path):
            console.print("❌ Path does not exist", style="bold red")
            return

        if not os.path.isdir(directory_path):
            console.print("❌ Path is not a directory", style="bold red")
            return

        moved_count = 0
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            if os.path.isdir(file_path):
                continue

            ext = filename.split(".")[-1].lower() if "." in filename else "others"
            target = os.path.join(directory_path, ext.upper() + "_Files")

            try:
                os.makedirs(target, exist_ok=True)
                shutil.move(file_path, os.path.join(target, filename))
                console.print(f"Moved: {filename}", style="green")
                moved_count += 1
            except PermissionError:
                console.print(f"❌ Permission denied: {filename}", style="bold red")
            except Exception as e:
                console.print(f"❌ Error moving {filename}: {str(e)}", style="bold red")

        console.print(f"✅ Total moved: {moved_count}", style="bold green")
    except Exception as e:
        console.print(f"❌ Error in organize_files: {str(e)}", style="bold red")


# ---------------- OLD FILE CLEANER ----------------
def delete_old_files(folder_path, days):
    try:
        if not os.path.exists(folder_path):
            console.print("❌ Path does not exist", style="bold red")
            return

        if not os.path.isdir(folder_path):
            console.print("❌ Path is not a directory", style="bold red")
            return

        if days < 0:
            console.print("❌ Days must be a positive number", style="bold red")
            return

        seconds = days * 86400
        now = time.time()
        old_files = []

        # 🔍 Scan files
        for file in os.listdir(folder_path):
            path = os.path.join(folder_path, file)
            if os.path.isfile(path):
                if now - os.path.getmtime(path) > seconds:
                    old_files.append(path)

        if not old_files:
            console.print("✅ No old files found", style="bold green")
            return

        # 📄 Show files
        console.print("\n🗂️ Files to be deleted:\n", style="bold yellow")
        for f in old_files:
            console.print(f"- {os.path.basename(f)}", style="yellow")

        # ❓ Confirmation
        confirm = console.input("\n❗ Confirm delete? (y/n): ").lower()

        if confirm != "y":
            console.print("❌ Deletion cancelled", style="bold red")
            return

        # 🧹 Delete files
        count = 0
        for f in old_files:
            try:
                os.remove(f)
                console.print(f"Deleted: {os.path.basename(f)}", style="yellow")
                count += 1
            except PermissionError:
                console.print(f"❌ Permission denied: {f}", style="bold red")

        console.print(f"\n✅ Total deleted: {count}", style="bold green")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")


# ---------------- SYSTEM INFO ----------------
def get_system_info():
    try:
        console.print("\n--- SYSTEM INFO ---", style="bright_green")
        console.print(
            f"OS: {platform.system()} {platform.release()}", style="bright_green"
        )
        console.print(
            f"CPU Cores: {psutil.cpu_count(logical=True)}", style="bright_green"
        )
        console.print(f"CPU Usage: {psutil.cpu_percent(1)}%", style="bright_green")

        mem = psutil.virtual_memory()
        console.print(
            f"RAM: {round(mem.total / (1024**3), 2)} GB", style="bright_green"
        )
        console.print(f"RAM Usage: {mem.percent}%", style="bright_green")

        disk = psutil.disk_usage("/")
        console.print(
            f"Disk Free: {round(disk.free / (1024**3), 2)} GB", style="bright_green"
        )
    except PermissionError:
        console.print("❌ Permission denied accessing system info", style="bold red")
    except Exception as e:
        console.print(f"❌ Error getting system info: {str(e)}", style="bold red")
    return ""


# ---------------- DUPLICATE FINDER ----------------
def file_hash(path):
    try:
        h = hashlib.md5()
        with open(path, "rb") as f:
            while chunk := f.read(4096):
                h.update(chunk)
        return h.hexdigest()
    except PermissionError:
        raise PermissionError(f"Permission denied reading: {path}")
    except Exception as e:
        raise Exception(f"Error hashing file: {str(e)}")


def find_duplicates(directory):
    try:
        if not os.path.exists(directory):
            console.print("❌ Path does not exist", style="bold red")
            return

        if not os.path.isdir(directory):
            console.print("❌ Path is not a directory", style="bold red")
            return

        seen = {}
        for root, _, files in os.walk(directory):
            for file in files:
                path = os.path.join(root, file)
                try:
                    h = file_hash(path)
                    if h in seen:
                        console.print(
                            f"Duplicate:\n{seen[h]}\n{path}\n", style="yellow"
                        )
                    else:
                        seen[h] = path
                except PermissionError:
                    console.print(f"⚠️  Permission denied: {path}", style="bold yellow")
                except Exception as e:
                    console.print(
                        f"⚠️  Error processing {path}: {str(e)}", style="bold yellow"
                    )
    except Exception as e:
        console.print(f"❌ Error in find_duplicates: {str(e)}", style="bold red")


# ---------------- DISK USAGE ANALYZER ----------------
def folder_size(path):
    total = 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except (OSError, PermissionError):
                    pass
    except Exception:
        pass
    return total


def build_tree(path, tree):
    try:
        items = os.listdir(path)
    except PermissionError:
        tree.add("[red]🔒 Access Denied[/red]")
        return
    except FileNotFoundError:
        tree.add("[red]❌ Not Found[/red]")
        return

    for item in items:
        full_path = os.path.join(path, item)

        if os.path.isdir(full_path):
            branch = tree.add(f"[green]📁 {item}[/green]")
            build_tree(full_path, branch)
        else:
            tree.add(f"[white]📄 {item}[/white]")


def show_tree(path):
    root = Tree(f"[bold cyan]📂 {path}[/bold cyan]")
    build_tree(path, root)
    console.print(root)


def disk_usage(directory):
    try:
        if not os.path.exists(directory):
            console.print("❌ Path does not exist", style="bold red")
            return

        if not os.path.isdir(directory):
            console.print("❌ Path is not a directory", style="bold red")
            return

        sizes = {}
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            try:
                if os.path.isdir(path):
                    sizes[path] = folder_size(path)
            except (OSError, PermissionError):
                console.print(f"⚠️  Could not access: {path}", style="bold yellow")

        if not sizes:
            console.print("❌ No folders found", style="bold red")
            return

        for folder, size in sorted(sizes.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]:
            console.print(f"{folder} → {round(size / (1024**3), 2)} GB", style="cyan")
    except Exception as e:
        console.print(f"❌ Error in disk_usage: {str(e)}", style="bold red")


# ---------------- FILE TRANSFER ----------------
def transfer_files(source_paths, destination):
    """
    Transfer files or folders from source to destination.
    source_paths: list of file/folder paths or single path
    destination: target directory path
    """
    try:
        # Convert single path to list
        if isinstance(source_paths, str):
            source_paths = [source_paths]

        # Validate destination
        if not destination:
            console.print("❌ Destination path cannot be empty", style="bold red")
            return

        # Create destination if it doesn't exist
        try:
            os.makedirs(destination, exist_ok=True)
        except PermissionError:
            console.print(
                f"❌ Permission denied: Cannot create {destination}", style="bold red"
            )
            return
        except Exception as e:
            console.print(f"❌ Error creating destination: {e}", style="bold red")
            return

        transferred_count = 0
        failed_count = 0

        console.print("\n📋 Transfer Summary:", style="bold cyan")
        console.print(f"   Destination: {destination}\n", style="cyan")

        for source in source_paths:
            source = source.strip()

            if not source:
                continue

            # Validate source
            if not os.path.exists(source):
                console.print(f"❌ Source not found: {source}", style="bold red")
                failed_count += 1
                continue

            try:
                item_name = os.path.basename(source)
                dest_path = os.path.join(destination, item_name)

                # Handle if destination already exists
                if os.path.exists(dest_path):
                    console.print(
                        f"⚠️  Already exists: {item_name}", style="bold yellow"
                    )
                    confirm = console.input(f"   Overwrite? (y/n): ").lower()
                    if confirm != "y":
                        console.print(f"⏭️  Skipped: {item_name}", style="yellow")
                        continue
                    # Remove existing destination
                    if os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    else:
                        os.remove(dest_path)

                # Transfer file or folder
                if os.path.isdir(source):
                    console.print(
                        f"📁 Transferring folder: {item_name}...", style="green"
                    )
                    shutil.copytree(source, dest_path)
                    console.print(f"✅ Folder transferred: {item_name}", style="green")
                else:
                    console.print(
                        f"📄 Transferring file: {item_name}...", style="green"
                    )
                    shutil.copy2(source, dest_path)
                    console.print(f"✅ File transferred: {item_name}", style="green")

                transferred_count += 1

            except PermissionError:
                console.print(f"❌ Permission denied: {source}", style="bold red")
                failed_count += 1
            except Exception as e:
                console.print(
                    f"❌ Error transferring {source}: {str(e)}", style="bold red"
                )
                failed_count += 1

        # Summary
        console.print(f"\n📊 Transfer Complete:", style="bold cyan")
        console.print(f"   ✅ Transferred: {transferred_count}", style="green")
        console.print(f"   ❌ Failed: {failed_count}", style="red")

    except Exception as e:
        console.print(f"❌ Error in transfer_files: {str(e)}", style="bold red")


# ---------------- MAIN INTERFACE ----------------
def main():
    while True:
        try:
            print(
                """
========= PYTHON SYSTEM TOOLKIT =========
1. Organize Files
2. Delete Old Files
3. System Information
4. Find Duplicate Files
5. Disk Usage Analyzer
6. Transfer Files
0. Exit
========================================
"""
            )
            # use console.input (safe wrapper) to avoid crashed exe when stdin is lost
            choice = console.input("Choose option: ").strip()

            if choice == "1":
                path = console.input("Enter folder path: ").strip()
                path = normalize_path(path)  # Normalize the path
                if path:
                    organize_files(path)
                else:
                    console.print("❌ Path cannot be empty", style="bold red")

            elif choice == "2":
                path = console.input("Enter folder path: ").strip()
                path = normalize_path(path)  # Normalize the path
                try:
                    days = int(console.input("Delete files older than days: ").strip())
                    if path:
                        delete_old_files(path, days)
                    else:
                        console.print("❌ Path cannot be empty", style="bold red")
                except ValueError:
                    console.print("❌ Days must be a valid number", style="bold red")

            elif choice == "3":
                get_system_info()

            elif choice == "4":
                path = console.input("Enter folder path: ").strip()
                path = normalize_path(path)  # Normalize the path
                if path:
                    find_duplicates(path)
                else:
                    console.print("❌ Path cannot be empty", style="bold red")

            elif choice == "5":
                path = console.input("Enter folder path: ").strip()
                path = normalize_path(path)  # Normalize the path
                if path:
                    disk_usage(path)
                else:
                    console.print("❌ Path cannot be empty", style="bold red")

            elif choice == "6":
                sources = console.input(
                    "Enter source file/folder paths (comma-separated): "
                ).strip()
                sources = [
                    normalize_path(s.strip()) for s in sources.split(",")
                ]  # Normalize each source path
                destination = console.input("Enter destination folder path: ").strip()
                destination = normalize_path(
                    destination
                )  # Normalize the destination path
                if sources and destination:
                    transfer_files(sources, destination)
                else:
                    console.print(
                        "❌ Source and destination cannot be empty", style="bold red"
                    )

            elif choice == "0":
                console.print("👋 Exiting Toolkit", style="bold cyan")
                break

            else:
                console.print("❌ Invalid choice", style="bold red")

        except KeyboardInterrupt:
            console.print("\n⚠️  Interrupted by user", style="bold yellow")
            break
        except Exception as e:
            console.print(f"❌ Unexpected error: {str(e)}", style="bold red")


def _type_writer(text, delay=0.04, style="bright_cyan", skip=False):
    if skip:
        console.print(text, style=style)
        return

    for ch in text:
        console.print(ch, end="", style=style, soft_wrap=True)
        time.sleep(delay)
    console.print()


def _animate_from_file(
    file_path="logic.txt", delay=0.04, style="bright_cyan", line_pause=0.25, skip=False
):
    # resolve file path so it works both when run normally and from PyInstaller --onefile
    fp = file_path if os.path.isabs(file_path) else resource_path(file_path)

    if not os.path.exists(fp):
        console.print("[red]❌ File not found[/red]")
        return

    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            _type_writer(line.rstrip(), delay=delay, style=style, skip=skip)
            if not skip:
                time.sleep(line_pause)


# ---------------- FILE VIEWER ----------------
def view_file(file_path=None, typewriter=False, speed=0.02, max_lines_preview=200):
    """
    Open and display a file. Supports .txt, .csv, .json (falls back to raw text).
    If file_path is None, prompts the user.
    """
    try:
        if not file_path:
            file_path = console.input("Enter file path: ").strip()

        if not file_path:
            console.print("❌ No path provided", style="bold red")
            return

        if not os.path.exists(file_path):
            console.print("❌ File not found", style="bold red")
            return

        if os.path.isdir(file_path):
            console.print("❌ Path is a directory", style="bold red")
            return

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # Ask if user wants typewriter animation
        if not typewriter:
            ans = console.input("Typewriter animation? (y/N): ").strip().lower()
            typewriter = ans == "y"

        def _print_text(text):
            if typewriter:
                _type_writer(text, delay=speed, skip=False)
            else:
                console.print(text)

        # CSV
        if ext == ".csv":
            try:
                df = pd.read_csv(file_path)
                console.print(f"[green]CSV loaded: {file_path}[/green]")
                console.print(
                    tabulate(
                        df.head(max_lines_preview), headers="keys", tablefmt="grid"
                    )
                )
                if len(df) > max_lines_preview:
                    more = (
                        console.input(f"Show full CSV? ({len(df)} rows) (y/N): ")
                        .strip()
                        .lower()
                    )
                    if more == "y":
                        console.print(tabulate(df, headers="keys", tablefmt="grid"))
                return
            except Exception as e:
                console.print(f"❌ Failed to read CSV: {e}", style="bold red")
                return

        # JSON
        if ext == ".json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pretty = json.dumps(data, indent=2, ensure_ascii=False)
                _print_text(pretty)
                return
            except Exception as e:
                console.print(f"❌ Failed to read JSON: {e}", style="bold red")
                return

        # Fallback: plain text (including .txt, .log, etc.)
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            if len(lines) <= max_lines_preview:
                _print_text("".join(lines))
            else:
                console.print(
                    f"[yellow]Previewing first {max_lines_preview} lines (file has {len(lines)} lines)[/yellow]"
                )
                _print_text("".join(lines[:max_lines_preview]))
                more = console.input("Show rest of file? (y/N): ").strip().lower()
                if more == "y":
                    _print_text("".join(lines[max_lines_preview:]))
        except Exception as e:
            console.print(f"❌ Error reading file: {e}", style="bold red")

    except KeyboardInterrupt:
        console.print("\n⚠️  Interrupted", style="bold yellow")
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="bold red")


# ---------------- INFO DISPLAY ----------------
def info(speed=0.04, style="bright_cyan", skip_animation=False):
    """
    Displays animated info from logic.txt
    """
    console.clear()
    console.print("[bold green]📜 TOOL INFORMATION[/bold green]\n", justify="center")

    _animate_from_file(
        file_path="logic.txt", delay=speed, style=style, skip=skip_animation
    )

    console.print("\n[dim]Press Enter to continue...[/dim]")
    console.input("")
