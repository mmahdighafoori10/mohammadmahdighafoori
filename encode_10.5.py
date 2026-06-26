import os
import sys
import subprocess
import glob
from pathlib import Path
from time import time, sleep
import winsound
import platform
from plyer import notification
from datetime import datetime
import threading
import signal
import io
import codecs

# اضافه کردن تنظیمات کدگذاری برای ویندوز
if platform.system() == "Windows":
    # تنظیم کدگذاری کنسول ویندوز
    os.system("chcp 65001 > NUL")
    # استفاده از utf-8 برای stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# -------------------------------
# نصب خودکار پکیج‌های مورد نیاز
# -------------------------------
def check_and_install_packages():
    required_packages = {
        "rich": "rich",
        "tqdm": "tqdm",
        "plyer": "plyer",
        "keyboard": "keyboard",
        "psutil": "psutil"
    }
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"Package '{package}' not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except Exception as e:
                print(f"Installation of {package} failed: {e}")
                sys.exit(1)

check_and_install_packages()

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    ProgressColumn
)
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
import keyboard
import psutil

console = Console(highlight=False)

# متغیر سراسری برای وضعیت توقف
PAUSED = False
CURRENT_PROCESS = None

# -------------------------------
# صداهای سوپر ماریو
# -------------------------------
def play_mario_sound(sound_type):
    """پخش صدای سوپر ماریو"""
    try:
        if platform.system() == "Windows":
            if sound_type == "startup":
                mario_theme = [
                    (659, 150), (659, 150), (0, 150), (659, 150), (0, 150), (523, 150), (659, 150), (0, 150),
                    (784, 300), (0, 300), (392, 300), (0, 300)
                ]
                for freq, duration in mario_theme:
                    if freq > 0:
                        winsound.Beep(freq, duration)
                    else:
                        sleep(duration / 1000)
            elif sound_type == "welcome":
                welcome_notes = [(440, 100), (554, 100), (659, 100), (880, 200)]
                for freq, duration in welcome_notes:
                    winsound.Beep(freq, duration)
            elif sound_type == "menu_navigate":
                winsound.Beep(800, 50)
            elif sound_type == "scanning":
                scan_notes = [(400, 50), (600, 50), (800, 50)]
                for freq, duration in scan_notes:
                    winsound.Beep(freq, duration)
            elif sound_type == "coin":
                winsound.Beep(988, 100)
            elif sound_type == "level_complete":
                notes = [(660, 150), (660, 150), (660, 150), (510, 150), (660, 150), (770, 200), (380, 200)]
                for n, d in notes:
                    winsound.Beep(n, d)
            elif sound_type == "game_over":
                notes = [(660, 300), (330, 300), (165, 500)]
                for n, d in notes:
                    winsound.Beep(n, d)
            elif sound_type == "powerup":
                powerup_notes = [(1046, 80), (1175, 80), (1319, 80), (1397, 80), (1568, 200)]
                for freq, duration in powerup_notes:
                    winsound.Beep(freq, duration)
            elif sound_type == "pipe":
                winsound.Beep(200, 100)
                winsound.Beep(300, 100)
            elif sound_type == "pause":
                winsound.Beep(660, 200)
                winsound.Beep(440, 200)
            elif sound_type == "resume":
                winsound.Beep(440, 200)
                winsound.Beep(660, 200)
                winsound.Beep(880, 200)
            elif sound_type == "file_select":
                select_notes = [(659, 60), (784, 60), (880, 80)]
                for freq, duration in select_notes:
                    winsound.Beep(freq, duration)
            elif sound_type == "processing_start":
                start_notes = [(523, 100), (659, 100), (784, 100), (1047, 200)]
                for freq, duration in start_notes:
                    winsound.Beep(freq, duration)
            elif sound_type == "notification_alert":
                alert_notes = [(880, 100), (1047, 100), (1319, 150), (1047, 100), (880, 100)]
                for freq, duration in alert_notes:
                    winsound.Beep(freq, duration)
            elif sound_type == "final_celebration":
                celebration_notes = [
                    (523, 100), (659, 100), (784, 100), (1047, 100), (784, 100), (659, 100),
                    (523, 100), (659, 100), (784, 100), (1047, 200), (1175, 200), (1319, 300),
                    (1047, 100), (784, 100), (659, 100), (523, 200)
                ]
                for freq, duration in celebration_notes:
                    winsound.Beep(freq, duration)
            elif sound_type == "detection":
                detection_notes = [(523, 80), (659, 80), (784, 120)]
                for freq, duration in detection_notes:
                    winsound.Beep(freq, duration)
    except:
        pass

# -------------------------------
# توابع تزیینی برای UI
# -------------------------------
def print_separator(char="=", length=80, color="dim"):
    """چاپ خط جداکننده زیبا"""
    console.print(f"[{color}]{char * length}[/{color}]")

def print_fancy_separator():
    """خط جداکننده فانتزی"""
    console.print("[cyan]" + "─" * 20 + "🎬" + "─" * 20 + "🎥" + "─" * 20 + "🎭" + "─" * 18 + "[/cyan]")

def print_loading_animation():
    """انیمیشن لودینگ ساده"""
    console.print("[yellow]Loading[/yellow]", end="")
    for _ in range(3):
        sleep(0.3)
        console.print(".", end="")
    console.print(" [green]✓[/green]")

# -------------------------------
# نمایش عنوان و ورودی زیبا
# -------------------------------
def show_welcome():
    """نمایش صفحه خوشامدگویی"""
    clear_console()

    play_mario_sound("startup")

    title_art = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                          🎬 VIDEO COMPRESSOR 🎬                              ║
    ║                      ULTRA HIGH-SPEED Edition v9.0                          ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """

    console.print(Align.center(title_art), style="bold cyan")

    welcome_panel = Panel.fit(
        "[bold yellow]✨ ULTRA HIGH-SPEED FEATURES ✨[/bold yellow]\n\n"
        "[green]⚡[/green] GPU NVENC (p4 preset, qp 23) - MAXIMUM SPEED\n"
        "[green]🎵[/green] Audio copy (NO re-encode) - 3-5x FASTER\n"
        "[green]👑[/green] ONE-CLICK ALL FILES CONVERSION\n"
        "[green]🎞️[/green] Enhanced WEBM/MOV/MKV/MTS conversions\n" 
        "[green]⏸️[/green] Real-time pause/resume with F10\n"
        "[green]🧠[/green] Smart resume detection\n"
        "[green]🪄[/green] Magic preview showing before/after sizes\n"
        "[green]📊[/green] Detailed compression reports\n"
        "[green]📁[/green] Automatic old file management\n\n"
        "[bold cyan]Press Enter to start ULTRA-FAST compression...[/bold cyan]",
        title="[bold blue]🚀 ULTRA HIGH-SPEED VIDEO COMPRESSION 🚀[/bold blue]",
        border_style="cyan",
        padding=(1, 2)
    )

    console.print(welcome_panel)
    play_mario_sound("welcome")
    input()
    clear_console()

def clear_console():
    """پاک کردن صفحه کنسول"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# -------------------------------
# نمایش راهنمای کلیدهای میانبر
# -------------------------------
def show_shortcuts_guide():
    """نمایش راهنمای کلیدهای میانبر"""
    play_mario_sound("menu_navigate")

    table = Table(title="⌨️ KEYBOARD SHORTCUTS GUIDE", show_header=True, header_style="bold cyan")
    table.add_column("🎮 Key", style="bold yellow", width=10)
    table.add_column("🎯 Function", style="green", width=30)
    table.add_column("⏰ When to Use", style="blue")

    table.add_row("F9", "🔍 Open Current Folder", "Anytime - Opens working folder in Explorer")
    table.add_row("F10", "⏸️ Pause/Resume Processing", "During encoding - Real pause and resume")
    table.add_row("Enter", "✅ Confirm/Continue", "At prompts - Confirms selections")

    console.print(Panel(table, border_style="blue", padding=(1, 2)))
    print_fancy_separator()

# -------------------------------
# مدیریت توقف موقت با psutil
# -------------------------------
def toggle_pause():
    """توقف موقت یا ادامه پردازش فعلی با استفاده از psutil"""
    global PAUSED, CURRENT_PROCESS

    if CURRENT_PROCESS is None or CURRENT_PROCESS.poll() is not None:
        console.print("\n[yellow]⚠️ No active process to pause/resume[/yellow]")
        return

    try:
        process = psutil.Process(CURRENT_PROCESS.pid)
        
        if PAUSED:
            process.resume()
            PAUSED = False
            console.print("\n[green]▶️ Processing resumed - FFmpeg is now running at full speed![/green]")
            play_mario_sound("resume")
        else:
            process.suspend()
            PAUSED = True
            console.print("\n[yellow]⏸️ Processing paused - FFmpeg suspended. Press F10 to resume![/yellow]")
            play_mario_sound("pause")
            
    except psutil.NoSuchProcess:
        console.print("\n[yellow]⚠️ Process no longer exists[/yellow]")
    except psutil.AccessDenied:
        console.print("\n[yellow]⚠️ Access denied. Try running as administrator for full pause functionality[/yellow]")
    except Exception as e:
        console.print(f"\n[yellow]⚠️ Pause error: {e}[/yellow]")
        PAUSED = not PAUSED
        if PAUSED:
            console.print("\n[yellow]⏸️ Marked as paused (visual indicator)[/yellow]")
        else:
            console.print("\n[green]▶️ Marked as resumed (visual indicator)[/green]")

# -------------------------------
# تنظیم کلیدهای میانبر
# -------------------------------
def setup_shortcuts(folder_path):
    """تنظیم کلیدهای میانبر"""

    def open_folder_shortcut():
        """عملکرد باز کردن پوشه با کلید میانبر"""
        console.print("\n[yellow]🔍 Opening current folder...[/yellow]")
        open_folder(folder_path)
        play_mario_sound("pipe")

    def pause_shortcut():
        """عملکرد توقف موقت/ادامه با کلید میانبر"""
        toggle_pause()

    try:
        keyboard.add_hotkey('f9', open_folder_shortcut)
        keyboard.add_hotkey('f10', pause_shortcut)
        show_shortcuts_guide()
    except Exception as e:
        console.print(f"[yellow]⚠️ Could not set up keyboard shortcuts: {e}[/yellow]")
        console.print("[dim]💡 Note: Keyboard shortcuts may require running as administrator in some systems[/dim]")

# -------------------------------
# بررسی FFmpeg
# -------------------------------
def check_ffmpeg():
    console.print("[yellow]🔍 Checking FFmpeg installation...[/yellow]")
    print_loading_animation()

    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
        console.print("[green]✅ FFmpeg found and ready![/green]")
        play_mario_sound("powerup")
        return True
    except Exception:
        console.print("\n[bold red]❌ FFmpeg not found![/bold red]")
        console.print("Please install FFmpeg manually using one of the following methods:")
        console.print(" • Windows: Download from https://www.gyan.dev/ffmpeg/builds/")
        console.print(" • Mac:     brew install ffmpeg")
        console.print(" • Linux:   sudo apt install ffmpeg")
        play_mario_sound("game_over")
        input("\nPress Enter to exit...")
        sys.exit(1)

check_ffmpeg()

# -------------------------------
# توابع کمکی
# -------------------------------
def get_file_info(file_path):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0

def get_video_files():
    """Find all video files in current directory"""
    console.print("\n[yellow]🔍 Scanning for video files...[/yellow]")
    play_mario_sound("scanning")

    video_extensions = [
        '*.mp4', '*.mov', '*.avi', '*.mkv', '*.wmv', '*.flv',
        '*.webm', '*.m4v', '*.3gp', '*.mpg', '*.mpeg', '*.m2v',
        '*.ts', '*.mts', '*.m2ts', '*.vob', '*.asf', '*.rm',
        '*.rmvb', '*.divx', '*.xvid', '*.f4v', '*.ogv'
    ]

    video_files = []
    for ext in video_extensions:
        video_files.extend(glob.glob(ext))
        video_files.extend(glob.glob(ext.upper()))

    # حذف فایل‌های فشرده شده قبلی
    filtered_files = [f for f in list(set(video_files)) 
                     if "_compress" not in f.lower() 
                     and "_compressed" not in f.lower()
                     and "_hq" not in f.lower()]

    if filtered_files:
        console.print(f"[green]✅ Found {len(filtered_files)} video files ready for compression![/green]")
        play_mario_sound("coin")

    return filtered_files

def get_video_duration(file):
    """Get video duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception:
        return None

def estimate_compressed_size(input_file):
    """Estimate compressed file size"""
    try:
        original_size = os.path.getsize(input_file)
        compression_ratio = 0.35
        return (original_size * compression_ratio) / (1024 * 1024)
    except Exception:
        return 0

def convert_video(input_file, progress, video_index):
    """Convert video with ULTRA HIGH-SPEED optimized settings"""
    global CURRENT_PROCESS, PAUSED

    try:
        file_path = Path(input_file)
        safe_name = str(file_path.name)
        output_file = f"{file_path.stem}_compress.mp4"

        if os.path.exists(output_file):
            console.print(f"[yellow]⚠️ {output_file} exists - skipping[/yellow]")
            play_mario_sound("pipe")
            return False, None

        original_size = get_file_info(input_file)
        estimated_size = estimate_compressed_size(input_file)
        console.print(f"[bold blue]📊 Estimated: {original_size:.1f} MB → ~{estimated_size:.1f} MB[/bold blue]")

        # تشخیص نوع فایل
        file_ext = file_path.suffix.lower()
        is_webm = file_ext == '.webm'
        is_mts = file_ext in ['.mts', '.m2ts']
        is_mkv = file_ext == '.mkv'
        is_mov = file_ext == '.mov'

        # تنظیمات ULTRA HIGH-SPEED
        if is_mts or is_webm or is_mkv or is_mov:
            # برای فرمت‌های خاص: تبدیل با کیفیت خوب و سرعت بالا
            console.print(f"[dim]🎥 {file_ext.upper()} detected: Using FAST conversion settings...[/dim]")
            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-c:v', 'libx264',
                '-crf', '23',           # کیفیت خوب
                '-preset', 'medium',    # سرعت متوسط (بهتر از slow)
                '-c:a', 'aac',          # تبدیل صدا
                '-b:a', '128k',
                '-movflags', '+faststart',
                output_file
            ]
        else:
            # برای MP4 و سایر فرمت‌ها: استفاده از GPU با حداکثر سرعت
            console.print("[dim]🚀 Using GPU (NVENC) with ULTRA HIGH-SPEED settings (p4, qp 23)...[/dim]")
            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-c:v', 'h264_nvenc',
                '-preset', 'p4',        # ⚡ حداکثر سرعت
                '-rc', 'constqp',       # ⚡ کنترل کیفیت ثابت
                '-qp', '23',            # ⚡ کیفیت خوب
                '-c:a', 'copy',         # ⚡ کپی صدا (بدون re-encode)
                '-movflags', '+faststart',
                output_file
            ]

        task = progress.add_task(f"🎥 [{video_index:02d}] {safe_name}", total=100)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            errors='replace'
        )

        CURRENT_PROCESS = process
        PAUSED = False

        duration = get_video_duration(input_file)
        start_time = time()
        paused_time = 0
        last_pause_time = 0
        reached_fifty_percent = False
        nvenc_error = False

        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break

            # بررسی خطای NVENC
            if "No NVENC capable devices found" in line or "Failed to create CUDA context" in line:
                nvenc_error = True

            # مدیریت توقف موقت
            if PAUSED:
                if last_pause_time == 0:
                    last_pause_time = time()
                sleep(0.1)
                continue
            else:
                if last_pause_time > 0:
                    paused_time += time() - last_pause_time
                    last_pause_time = 0

            if line and "time=" in line:
                try:
                    time_str = line.split("time=")[1].split()[0]
                    h, m, s = map(float, time_str.split(':'))
                    current_sec = h * 3600 + m * 60 + s
                    if duration and duration > 0:
                        percent = (current_sec / duration) * 100
                        percent = min(percent, 100)

                        elapsed_time = time() - start_time - paused_time
                        if elapsed_time > 0:
                            render_speed = current_sec / elapsed_time
                            speed_text = f" | {percent:.1f}% | ⚡{render_speed:.1f}x"
                            if PAUSED:
                                speed_text += " [PAUSED]"
                        else:
                            speed_text = ""

                        progress.update(task, completed=percent,
                                    description=f"🎥 [{video_index:02d}] {safe_name}{speed_text}")

                        if percent >= 50 and not reached_fifty_percent:
                            play_mario_sound("coin")
                            reached_fifty_percent = True
                except Exception:
                    pass

        CURRENT_PROCESS = None
        PAUSED = False

        # Fallback به CPU اگر GPU شکست خورد
        if process.returncode != 0 and nvenc_error and not (is_webm or is_mts or is_mkv or is_mov):
            console.print("[yellow]⚠️ GPU failed. Using CPU (libx264) with FAST settings...[/yellow]")
            
            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-c:v', 'libx264',
                '-crf', '23',           # کیفیت خوب
                '-preset', 'fast',      # ⚡ سرعت بالا
                '-c:a', 'copy',         # ⚡ کپی صدا
                '-movflags', '+faststart',
                output_file
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                errors='replace'
            )
            
            CURRENT_PROCESS = process
            PAUSED = False
            
            start_time = time()
            paused_time = 0
            last_pause_time = 0
            reached_fifty_percent = False
            
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                    
                if PAUSED:
                    if last_pause_time == 0:
                        last_pause_time = time()
                    sleep(0.1)
                    continue
                else:
                    if last_pause_time > 0:
                        paused_time += time() - last_pause_time
                        last_pause_time = 0
                        
                if line and "time=" in line:
                    try:
                        time_str = line.split("time=")[1].split()[0]
                        h, m, s = map(float, time_str.split(':'))
                        current_sec = h * 3600 + m * 60 + s
                        if duration and duration > 0:
                            percent = (current_sec / duration) * 100
                            percent = min(percent, 100)
                            
                            elapsed_time = time() - start_time - paused_time
                            if elapsed_time > 0:
                                render_speed = current_sec / elapsed_time
                                speed_text = f" | {percent:.1f}% | CPU:⚡{render_speed:.1f}x"
                                if PAUSED:
                                    speed_text += " [PAUSED]"
                            else:
                                speed_text = " (CPU)"
                                
                            progress.update(task, completed=percent,
                                        description=f"🎥 [{video_index:02d}] {safe_name}{speed_text}")
                            
                            if percent >= 50 and not reached_fifty_percent:
                                play_mario_sound("coin")
                                reached_fifty_percent = True
                    except Exception:
                        pass
                        
            CURRENT_PROCESS = None
            PAUSED = False

        if process.returncode == 0:
            progress.update(task, completed=100)
            play_mario_sound("level_complete")

            final_size = get_file_info(output_file)
            original_size = get_file_info(input_file)

            if original_size > 0:
                reduction_percent = ((original_size - final_size) / original_size) * 100
                console.print(f"[green]✅ Created: {output_file}[/green]")
                console.print(f"[bold blue]📊 Size: {original_size:.1f} MB → {final_size:.1f} MB ({reduction_percent:.1f}% reduction)[/bold blue]")
            else:
                console.print(f"[green]✅ Created: {output_file}[/green]")
                console.print(f"[bold blue]📊 Final size: {final_size:.1f} MB[/bold blue]")

            return True, output_file
        else:
            console.print(f"[red]❌ Failed: {input_file}[/red]")
            play_mario_sound("game_over")
            return False, None
            
    except Exception as e:
        console.print(f"[red]❌ Error in convert_video: {e}[/red]")
        play_mario_sound("game_over")
        return False, None

def move_to_old_folder(file):
    """Move old file to ./old_files/"""
    try:
        old_dir = Path("old_files")
        old_dir.mkdir(exist_ok=True)

        dest = old_dir / Path(file).name
        counter = 1
        while dest.exists():
            dest = old_dir / f"{Path(file).stem}_copy{counter}{Path(file).suffix}"
            counter += 1

        os.rename(file, dest)
        console.print(f"[blue]📁 Moved: {file} → old_files/[/blue]")
        play_mario_sound("pipe")
    except Exception as e:
        console.print(f"[red]❌ Can't move {file}: {e}[/red]")
        play_mario_sound("game_over")

def play_notification_sound():
    """پخش صدای نوتیفیکیشن ماریو"""
    play_mario_sound("notification_alert")

def show_notification(title, message):
    """نمایش نوتیفیکیشن ویندوز"""
    console.print("[bold yellow]📱 Sending desktop notification...[/bold yellow]")
    play_notification_sound()

    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Video Compressor Pro",
            timeout=15,
            toast=True
        )

        sleep(1)

        notification.notify(
            title="🎉 Compression Complete!",
            message=f"✅ {message}\n🎵 All videos processed successfully!",
            app_name="Video Compressor Pro",
            timeout=20,
            toast=True
        )

        console.print("[green]📱 Desktop notifications sent successfully![/green]")

    except Exception as e:
        console.print(f"[yellow]⚠️ Could not send notification: {e}[/yellow]")
        try:
            if platform.system() == "Windows":
                os.system(f'msg * "Video Compression Complete! {message}"')
        except:
            pass

def open_folder(path):
    """باز کردن پوشه در فایل منیجر"""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        console.print(f"[yellow]⚠️ Could not open folder: {e}[/yellow]")

def generate_report(final_video_files, converted_files, start_time, current_folder):
    """Generate a text report of the compression process"""
    try:
        report_path = os.path.join(current_folder, "compression_report.txt")

        total_original = 0
        total_compressed = 0
        file_details = []

        for original, compressed in zip(final_video_files, converted_files):
            try:
                orig_size = get_file_info(original)
                comp_size = get_file_info(compressed)
                reduction = ((orig_size - comp_size) / orig_size) * 100 if orig_size > 0 else 0

                total_original += orig_size
                total_compressed += comp_size

                file_details.append({
                    'original_name': Path(original).name,
                    'original_size': orig_size,
                    'compressed_name': Path(compressed).name,
                    'compressed_size': comp_size,
                    'reduction': reduction
                })
            except Exception as e:
                console.print(f"[yellow]⚠️ Warning while processing file info: {e}[/yellow]")
                continue

        duration = time() - start_time
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)

        if total_original > 0:
            total_reduction = ((total_original - total_compressed) / total_original) * 100
        else:
            total_reduction = 0

        with open(report_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write("=== VIDEO COMPRESSION REPORT ===\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Folder: {current_folder}\n")
            f.write(f"Total processing time: {int(hours)}h {int(minutes)}m {int(seconds)}s\n")
            f.write(f"Compression method: ULTRA HIGH-SPEED (NVENC p4/libx264 fast, QP/CRF 23)\n")
            f.write(f"Audio: Copy (no re-encode) / AAC 128k\n\n")

            f.write("=== FILE DETAILS ===\n")
            for i, detail in enumerate(file_details, 1):
                try:
                    f.write(f"{i}. {detail['original_name']}\n")
                    f.write(f"   Original: {detail['original_size']:.1f} MB\n")
                    f.write(f"   Compressed: {detail['compressed_size']:.1f} MB\n")
                    f.write(f"   Reduction: {detail['reduction']:.1f}%\n")
                    f.write(f"   Output: {detail['compressed_name']}\n\n")
                except Exception as e:
                    f.write(f"{i}. [Error writing filename: {e}]\n\n")
                    continue

            f.write("\n=== SUMMARY ===\n")
            f.write(f"Total original size: {total_original:.1f} MB\n")
            f.write(f"Total compressed size: {total_compressed:.1f} MB\n")
            f.write(f"Total reduction: {total_reduction:.1f}%\n")
            f.write(f"Number of files processed: {len(converted_files)}\n")
            f.write(f"Average compression ratio: {total_reduction:.1f}%\n")

        console.print(f"\n[green]✅ Report generated: {report_path}[/green]")
        play_mario_sound("coin")
        return report_path
    except Exception as e:
        console.print(f"[red]❌ Failed to generate report: {e}[/red]")
        return None

# -------------------------------
# انتخاب فایل‌ها برای پردازش
# -------------------------------
def parse_file_selection(input_str, max_files):
    """Parse user input for file selection"""
    selected = set()

    try:
        parts = input_str.replace(' ', '').split(',')

        for part in parts:
            if '-' in part and part.count('-') == 1:
                start, end = map(int, part.split('-'))
                if 1 <= start <= max_files and 1 <= end <= max_files:
                    selected.update(range(min(start, end), max(start, end) + 1))
                else:
                    console.print(f"[red]❌ Range {part} is out of bounds (1-{max_files})[/red]")
                    return None
            else:
                num = int(part)
                if 1 <= num <= max_files:
                    selected.add(num)
                else:
                    console.print(f"[red]❌ Number {num} is out of bounds (1-{max_files})[/red]")
                    return None

        return sorted(list(selected))
    except ValueError:
        console.print("[red]❌ Invalid input format. Use numbers, ranges (1-5), or comma-separated (1,3,5)[/red]")
        return None

def select_by_file_type(mp4_files, webm_files, mts_files, mov_files, mkv_files, other_files, all_files):
    """انتخاب بر اساس نوع فایل"""
    play_mario_sound("menu_navigate")

    options = []
    option_files = []

    mp4_count = len(mp4_files)
    webm_count = len(webm_files)
    mts_count = len(mts_files)
    mov_count = len(mov_files)
    mkv_count = len(mkv_files)
    other_count = len(other_files)

    options.append("👑 Process ALL files")
    option_files.append(all_files)

    if mp4_count > 0:
        options.append("Compress MP4 files")
        option_files.append(mp4_files)

    if mts_count > 0:
        options.append("Convert & Compress MTS camera files")
        option_files.append(mts_files)

    if webm_count > 0:
        options.append("Convert & Compress WEBM files")
        option_files.append(webm_files)

    if mov_count > 0:
        options.append("Convert & Compress MOV files")
        option_files.append(mov_files)
        
    if mkv_count > 0:
        options.append("Convert & Compress MKV files")
        option_files.append(mkv_files)

    if other_count > 0:
        options.append("Convert & Compress other files")
        option_files.append(other_files)

    if not options:
        return []

    console.print("\n[bold cyan]🔢 Select by File Type:[/bold cyan]")
    for i, option in enumerate(options, 1):
        if option.startswith("👑"):
            console.print(f"   {i}. [bold yellow]{option}[/bold yellow] ({len(all_files)} files)")
        elif option.startswith("Compress MP4"):
            console.print(f"   {i}. {option} ({mp4_count} files)")
        elif option.startswith("Convert & Compress MTS"):
            console.print(f"   {i}. {option} ({mts_count} files)")
        elif option.startswith("Convert & Compress WEBM"):
            console.print(f"   {i}. {option} ({webm_count} files)")
        elif option.startswith("Convert & Compress MOV"):
            console.print(f"   {i}. {option} ({mov_count} files)")
        elif option.startswith("Convert & Compress MKV"):
            console.print(f"   {i}. {option} ({mkv_count} files)")
        elif option.startswith("Convert & Compress other"):
            console.print(f"   {i}. {option} ({other_count} files)")

    while True:
        try:
            choice = int(input(f"\nEnter option number (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                play_mario_sound("powerup")
                return option_files[choice - 1]
            else:
                console.print("[red]❌ Invalid choice. Please try again.[/red]")
                play_mario_sound("game_over")
        except ValueError:
            console.print("[red]❌ Please enter a number.[/red]")
            play_mario_sound("game_over")

def show_quick_start_menu(video_files):
    """نمایش منوی شروع سریع"""
    
    quick_panel = Panel.fit(
        f"[bold yellow]🚀 QUICK START: PROCESS ALL {len(video_files)} FILES?[/bold yellow]\n\n"
        "[green]✅ Process everything with one click![/green]\n"
        "[dim]This will compress all files with ULTRA HIGH-SPEED settings[/dim]",
        title="[bold cyan]⚡ ONE-CLICK PROCESSING[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(quick_panel)
    
    choice = input("\n🚀 Process all files? [Y/n]: ").lower().strip()
    if choice in ['y', 'yes', '']:
        play_mario_sound("powerup")
        return video_files
    else:
        console.print("[yellow]Going to advanced selection...[/yellow]")
        return None

def select_files_to_process(video_files):
    """انتخاب فایل‌ها با تشخیص هوشمند"""
    try:
        quick_result = show_quick_start_menu(video_files)
        if quick_result:
            return quick_result
        
        mp4_files = [f for f in video_files if f.lower().endswith('.mp4')]
        webm_files = [f for f in video_files if f.lower().endswith('.webm')]
        mts_files = [f for f in video_files if f.lower().endswith(('.mts', '.m2ts'))]
        mov_files = [f for f in video_files if f.lower().endswith('.mov')]
        mkv_files = [f for f in video_files if f.lower().endswith('.mkv')]
        other_files = [f for f in video_files if not f.lower().endswith(('.mp4', '.webm', '.mts', '.m2ts', '.mov', '.mkv'))]

        sorted_files = sorted(video_files)

        print_fancy_separator()

        console.print("[yellow]🔍 Checking for already compressed files...[/yellow]")
        already_compressed = []
        new_files = []
        
        for f in sorted_files:
            file_path = Path(f)
            expected_compressed = f"{file_path.stem}_compress.mp4"
            if os.path.exists(expected_compressed):
                already_compressed.append(f)
            else:
                new_files.append(f)

        if already_compressed:
            play_mario_sound("detection")

        files_table = Table(title="📁 VIDEO FILES DISCOVERY", show_header=True, header_style="bold cyan")
        files_table.add_column("🎬 No.", style="bold yellow", width=6)
        files_table.add_column("📄 Filename", style="green")
        files_table.add_column("🎭 Type", style="cyan", width=10)
        files_table.add_column("📊 Size (MB)", style="yellow", justify="right", width=12)
        files_table.add_column("🪄 Est. (MB)", style="blue", justify="right", width=12)
        files_table.add_column("✅ Status", style="white", width=15)

        for i, f in enumerate(sorted_files, 1):
            try:
                size_mb = get_file_info(f)
                estimated_size = estimate_compressed_size(f)
                file_path = Path(f)
                expected_compressed = f"{file_path.stem}_compress.mp4"

                file_ext = file_path.suffix.lower()
                if file_ext == '.mp4':
                    file_type = "🟢 MP4"
                elif file_ext in ['.mts', '.m2ts']:
                    file_type = "🔴 MTS"
                elif file_ext == '.webm':
                    file_type = "🟣 WEBM"
                elif file_ext == '.mov':
                    file_type = "🔶 MOV"
                elif file_ext == '.mkv':
                    file_type = "🟦 MKV"
                else:
                    file_type = "🔵 Other"

                if os.path.exists(expected_compressed):
                    compressed_size = get_file_info(expected_compressed)
                    status = f"🟰 Done ({compressed_size:.1f}MB)"
                    files_table.add_row(
                        f"[dim]{i:02d}[/dim]",
                        f"[dim]{f}[/dim]",
                        f"[dim]{file_type}[/dim]",
                        f"[dim]{size_mb:.1f}[/dim]",
                        f"[dim]{estimated_size:.1f}[/dim]",
                        f"[green]{status}[/green]"
                    )
                else:
                    status = "⏳ Pending"
                    files_table.add_row(
                        f"{i:02d}",
                        f,
                        file_type,
                        f"{size_mb:.1f}",
                        f"{estimated_size:.1f}",
                        f"[yellow]{status}[/yellow]"
                    )
                    
            except Exception as e:
                files_table.add_row(f"{i:02d}", f, "❌ Error", "N/A", "N/A", "[red]❌ Error[/red]")
                continue

        console.print(files_table)

        if already_compressed:
            summary_panel = Panel.fit(
                f"[bold yellow]📊 PROCESSING STATUS:[/bold yellow]\n\n"
                f"[green]✅ Already compressed: {len(already_compressed)} files[/green]\n"
                f"[yellow]⏳ Pending compression: {len(new_files)} files[/yellow]\n\n"
                f"[bold cyan]💡 SMART RESUME TIP:[/bold cyan] [dim]Dimmed files are already processed.[/dim]",
                title="[bold blue]🧠 SMART RESUME DETECTION[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            )
            console.print(summary_panel)
            play_mario_sound("coin")

        print_fancy_separator()

        if new_files and already_compressed:
            selection_panel = Panel.fit(
                "[bold yellow]🎯 SMART SELECTION OPTIONS:[/bold yellow]\n"
                "• Type [bold]all[/bold] to process all files (recommended)\n"
                "• Type [bold]new[/bold] to process only pending files\n"
                "• Type [bold]done[/bold] to re-process completed files\n"
                "• Enter file numbers: [dim]1,3,5[/dim] or [dim]1-5[/dim] or [dim]2,4-7,9[/dim]\n"
                "• Type [bold]a[/bold] for advanced options (by file type)\n"
                "• Type [bold]1[/bold] for first file | [bold]last[/bold] for last file",
                title="[bold cyan]🧠 INTELLIGENT SELECTION MENU[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
        else:
            selection_panel = Panel.fit(
                "[bold yellow]🎯 CUSTOM SELECTION:[/bold yellow]\n"
                "• Type [bold]all[/bold] for all files (recommended)\n"
                "• Enter file numbers: [dim]1,3,5[/dim] or [dim]1-5[/dim]\n"
                "• Type [bold]a[/bold] for advanced options\n"
                "• Type [bold]1[/bold] for first file | [bold]last[/bold] for last file",
                title="[bold cyan]🎮 SELECTION MENU[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
        
        console.print(selection_panel)

        while True:
            try:
                choice = input(f"\n🎯 Select files (1-{len(sorted_files)} or 'all'): ").strip().lower()

                if choice in ['all']:
                    console.print(f"[green]✅ Selected all {len(sorted_files)} files[/green]")
                    if already_compressed:
                        console.print(f"[yellow]⚠️ Includes {len(already_compressed)} completed files[/yellow]")
                    play_mario_sound("file_select")
                    return sorted_files

                elif choice == 'new' and new_files:
                    console.print(f"[green]✅ Selected {len(new_files)} pending files[/green]")
                    play_mario_sound("file_select")
                    return new_files

                elif choice == 'done' and already_compressed:
                    console.print(f"[yellow]⚠️ Selected {len(already_compressed)} completed files[/yellow]")
                    confirm = input("⚠️ This will create duplicates. Continue? [y/N]: ").lower().strip()
                    if confirm in ['y', 'yes']:
                        play_mario_sound("file_select")
                        return already_compressed
                    else:
                        console.print("[yellow]Cancelled. Try again.[/yellow]")
                        continue

                elif choice == 'last':
                    console.print(f"[green]✅ Selected last file: {sorted_files[-1]}[/green]")
                    play_mario_sound("file_select")
                    return [sorted_files[-1]]

                elif choice == 'a':
                    return select_by_file_type(mp4_files, webm_files, mts_files, mov_files, mkv_files, other_files, video_files)

                elif choice.isdigit() and choice == '1':
                    console.print(f"[green]✅ Selected first file: {sorted_files[0]}[/green]")
                    play_mario_sound("file_select")
                    return [sorted_files[0]]

                else:
                    selected_indices = parse_file_selection(choice, len(sorted_files))

                    if selected_indices is not None:
                        selected_files = [sorted_files[i-1] for i in selected_indices]

                        print_fancy_separator()

                        selected_table = Table(title="✅ SELECTED FILES", show_header=True, header_style="bold green")
                        selected_table.add_column("🎬 No.", style="bold yellow", width=6)
                        selected_table.add_column("📄 Filename", style="green")
                        selected_table.add_column("📊 Size (MB)", style="yellow", justify="right")
                        selected_table.add_column("🪄 After (MB)", style="blue", justify="right", width=12)
                        selected_table.add_column("✅ Status", style="white", width=15)

                        pending_count = 0
                        already_done_count = 0

                        for i, f in enumerate(selected_files, 1):
                            size_mb = get_file_info(f)
                            estimated_size = estimate_compressed_size(f)
                            file_path = Path(f)
                            expected_compressed = f"{file_path.stem}_compress.mp4"
                            
                            if os.path.exists(expected_compressed):
                                compressed_size = get_file_info(expected_compressed)
                                status = f"🟰 Done"
                                already_done_count += 1
                                selected_table.add_row(
                                    f"[dim]{i}[/dim]", 
                                    f"[dim]{f}[/dim]", 
                                    f"[dim]{size_mb:.1f}[/dim]", 
                                    f"[dim green]{compressed_size:.1f}[/dim green]",
                                    f"[green]{status}[/green]"
                                )
                            else:
                                status = "⏳ Pending"
                                pending_count += 1
                                selected_table.add_row(
                                    f"{i}", 
                                    f, 
                                    f"{size_mb:.1f}", 
                                    f"[blue]~{estimated_size:.1f}[/blue]",
                                    f"[yellow]{status}[/yellow]"
                                )

                        console.print(selected_table)
                        
                        if already_done_count > 0 and pending_count > 0:
                            console.print(f"\n[yellow]⚠️ Mixed: {already_done_count} done, {pending_count} pending[/yellow]")
                        elif already_done_count > 0:
                            console.print(f"\n[green]✅ All {already_done_count} already compressed[/green]")
                        else:
                            total_original = sum(get_file_info(f) for f in selected_files if not os.path.exists(f"{Path(f).stem}_compress.mp4"))
                            total_estimated = sum(estimate_compressed_size(f) for f in selected_files if not os.path.exists(f"{Path(f).stem}_compress.mp4"))
                            if total_original > 0:
                                reduction_percent = ((total_original - total_estimated) / total_original) * 100
                                console.print(f"\n[cyan]🪄 Preview: {total_original:.1f} MB → ~{total_estimated:.1f} MB (~{reduction_percent:.1f}% reduction)[/cyan]")
                        
                        play_mario_sound("file_select")
                        print_separator("─", 80, "dim")

                        confirm = input(f"\n✨ Process these {len(selected_files)} files? [Y/n]: ").lower().strip()
                        if confirm in ['', 'y', 'yes']:
                            play_mario_sound("powerup")
                            return selected_files
                        else:
                            console.print("[yellow]Cancelled. Try again.[/yellow]")
                            continue
            except KeyboardInterrupt:
                console.print("\n[yellow]❌ Selection cancelled![/yellow]")
                play_mario_sound("game_over")
                return []
            except Exception as e:
                console.print(f"[red]❌ Error: {e}. Try again.[/red]")
                play_mario_sound("game_over")
                continue
    except Exception as e:
        console.print(f"[red]❌ Error in file selection: {e}[/red]")
        play_mario_sound("game_over")
        return []

# -------------------------------
# تابع اصلی
# -------------------------------
def main():
    try:
        show_welcome()

        current_folder = os.getcwd()
        start_time = time()

        header_panel = Panel.fit(
            "[cyan]🎬 VIDEO COMPRESSOR ULTRA HIGH-SPEED - v9.0 🎬[/cyan]\n"
            "[dim]🚀 Features: Maximum speed, One-click processing, All formats, Smart resume[/dim]",
            title="[bold blue]⚡ ULTRA HIGH-SPEED VIDEO PROCESSING ⚡[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(header_panel)
        print_fancy_separator()

        setup_shortcuts(current_folder)

        video_files = get_video_files()

        if not video_files:
            console.print(Panel("[red]❌ No video files found![/red]",
                               title="[bold red]🚨 ERROR 🚨[/bold red]", border_style="red"))
            play_mario_sound("game_over")
            input("\nPress Enter to exit...")
            return

        final_video_files = select_files_to_process(video_files)

        if not final_video_files:
            console.print("[yellow]⚠️ No files selected![/yellow]")
            play_mario_sound("game_over")
            input("\nPress Enter to exit...")
            return

        print_fancy_separator()

        try:
            total_original = sum(get_file_info(f) for f in final_video_files)
            total_estimated = sum(estimate_compressed_size(f) for f in final_video_files)
            estimated_reduction = ((total_original - total_estimated) / total_original) * 100 if total_original > 0 else 0

            summary_panel = Panel.fit(
                f"[bold yellow]⚙️ Ready to process {len(final_video_files)} files[/bold yellow]\n"
                f"[bold blue]📊 Total: {total_original:.1f} MB → ~{total_estimated:.1f} MB (~{estimated_reduction:.1f}% reduction)[/bold blue]\n"
                f"[bold green]💡 F10 = Real pause/resume | F9 = Open folder[/bold green]",
                title="[bold cyan]📋 PROCESSING SUMMARY[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(summary_panel)
        except Exception as e:
            console.print(f"[yellow]⚠️ Error calculating totals: {e}[/yellow]")
            console.print(f"\n[bold yellow]⚙️ Ready to process {len(final_video_files)} files[/bold yellow]")

        print_separator("─", 80, "dim")

        confirm = input("\n🚀 Start processing? [Y/n]: ").lower().strip()
        if confirm not in ['y', 'yes', '']:
            console.print("[yellow]❌ Cancelled![/yellow]")
            play_mario_sound("game_over")
            input("\nPress Enter to exit...")
            return

        play_mario_sound("processing_start")

        converted_files = []
        original_files = []

        print_fancy_separator()

        location_panel = Panel.fit(
            f"[bold cyan]📂 WORKING FOLDER:[/bold cyan] [yellow]{current_folder}[/yellow]",
            title="[bold blue]🎯 PROCESSING LOCATION[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(location_panel)
        print_fancy_separator()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            expand=True
        ) as progress:

            overall_task = progress.add_task("[cyan]🎬 Overall Progress[/cyan]", total=len(final_video_files))

            for i, video_file in enumerate(sorted(final_video_files), 1):
                try:
                    console.print(f"\n[bold magenta]📽️ Processing {i:02d}/{len(final_video_files)}: {video_file}[/bold magenta]")

                    success, output_file = convert_video(video_file, progress, i)

                    if success:
                        converted_files.append(output_file)
                        original_files.append(video_file)

                    percent_done = (i / len(final_video_files)) * 100
                    progress.update(overall_task, completed=i,
                                    description=f"[cyan]🎬 Overall Progress[/cyan] | {percent_done:.1f}% | {i}/{len(final_video_files)} files")
                except Exception as e:
                    console.print(f"[red]❌ Error processing {video_file}: {e}[/red]")
                    play_mario_sound("game_over")
                    continue

        print_fancy_separator()

        if original_files:
            console.print("\n[bold yellow]📦 Moving original files to 'old_files'...[/bold yellow]")
            for file in original_files:
                move_to_old_folder(file)

            print_separator("─", 80, "green")

            console.print("\n[bold green]🎉 PROCESSING COMPLETED! 🎉[/bold green]")
            console.print("[bold green]🎵 Playing celebration music...[/bold green]")
            play_mario_sound("final_celebration")

            print_separator("─", 80, "green")

            try:
                show_notification("🎉 Compression Complete!", f"Successfully compressed {len(converted_files)} files")
            except Exception as e:
                console.print(f"[yellow]⚠️ Could not show notification: {e}[/yellow]")

            print_separator("─", 80, "green")

            console.print(f"\n[green]✅ {len(converted_files)} files compressed successfully[/green]")
            console.print(f"[blue]📁 {len(original_files)} files moved to 'old_files/'[/blue]")

            report_path = generate_report(final_video_files, converted_files, start_time, current_folder)

            print_fancy_separator()

            try:
                total_original = sum(get_file_info(f) for f in original_files)
                total_compressed = sum(get_file_info(f) for f in converted_files)

                duration = time() - start_time
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)

                if total_original > 0:
                    total_reduction = ((total_original - total_compressed) / total_original) * 100
                    summary_msg = f"Original: {total_original:.1f} MB\nCompressed: {total_compressed:.1f} MB\nReduction: {total_reduction:.1f}%\nTime: {int(hours)}h {int(minutes)}m {int(seconds)}s"
                else:
                    summary_msg = f"Original: {total_original:.1f} MB\nCompressed: {total_compressed:.1f} MB\nTime: {int(hours)}h {int(minutes)}m {int(seconds)}s"

                final_panel = Panel.fit(
                    summary_msg,
                    title="[bold cyan]📊 FINAL SUMMARY[/bold cyan]",
                    border_style="green",
                    padding=(1, 2)
                )
                console.print(final_panel)
            except Exception as e:
                console.print(f"[yellow]⚠️ Could not calculate summary: {e}[/yellow]")
                duration = time() - start_time
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                console.print(f"Files: {len(converted_files)} | Time: {int(hours)}h {int(minutes)}m {int(seconds)}s")

            try:
                open_folder(current_folder)
            except Exception as e:
                console.print(f"[yellow]⚠️ Could not open folder: {e}[/yellow]")

            print_fancy_separator()

            delete_panel = Panel.fit(
                "[bold red]⚠️ DELETE original files from 'old_files/'?[/bold red]\n"
                "[yellow]⚠️ This cannot be undone![/yellow]",
                title="[bold red]🗑️ DELETE ORIGINAL FILES[/bold red]",
                border_style="red",
                padding=(1, 2)
            )
            console.print(delete_panel)

            choice = input("🗑️ Delete permanently? [y/N]: ").lower().strip()

            if choice in ['y', 'yes']:
                play_mario_sound("powerup")
                deleted_count = 0
                old_dir = Path("old_files")
                if old_dir.exists():
                    for file in old_dir.iterdir():
                        if file.is_file():
                            try:
                                file.unlink()
                                console.print(f"[red]🗑️ Deleted: {file.name}[/red]")
                                deleted_count += 1
                                play_mario_sound("coin")
                            except Exception as e:
                                console.print(f"[red]❌ Failed to delete {file.name}: {e}[/red]")
                                play_mario_sound("game_over")

                    console.print(f"\n[green]✅ {deleted_count} files deleted[/green]")
                else:
                    console.print("[yellow]📁 'old_files' not found.[/yellow]")
            else:
                console.print("[yellow]📁 Files kept in 'old_files/'[/yellow]")

        print_fancy_separator()

        completion_panel = Panel.fit(
            "[bold cyan]🎉 ALL DONE! 🎉[/bold cyan]\n\n"
            "[bold green]✅ Check '_compress.mp4' files[/bold green]\n"
            "[bold blue]📊 Check 'compression_report.txt'[/bold blue]\n"
            "[bold yellow]📁 Originals in 'old_files/'[/bold yellow]\n\n"
            "[dim]💡 Thank you for using Video Compressor![/dim]",
            title="[bold green]🏆 MISSION ACCOMPLISHED 🏆[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(completion_panel)

    except Exception as error:
        console.print(f"\n[bold red]⚠️ Error: {error}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        play_mario_sound("game_over")
    finally:
        print_separator("=", 80, "cyan")
        input("\n🎮 Press Enter to exit...")

if __name__ == "__main__":
    main()