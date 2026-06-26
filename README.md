Ultra-Fast System-Adaptive Video Encoder
# 🎬 Ultra High-Speed Video Compressor

**Ultra High-Speed Video Compressor** is a Python-based desktop video compression and conversion tool powered by **FFmpeg**. It is designed for fast, simple, and efficient batch video compression with GPU acceleration, smart file detection, real-time progress tracking, pause/resume controls, compression reports, desktop notifications, and automatic file management.

---

## 🚀 README Description

**Ultra High-Speed Video Compressor** is a Python command-line desktop tool built to compress and convert video files quickly and efficiently using FFmpeg.

It features a rich interactive terminal interface, smart video scanning, NVIDIA GPU acceleration, automatic CPU fallback, one-click batch processing, real-time progress monitoring, and detailed compression reports.

This tool is especially useful for content creators, video editors, social media managers, and anyone who needs to reduce video file sizes while maintaining good visual quality.

---

## ✨ Key Features

* ⚡ **Ultra-fast video compression** powered by FFmpeg

* 🚀 **GPU acceleration with NVIDIA NVENC** for supported video formats

* 🧠 **Automatic CPU fallback** using libx264 when GPU encoding is unavailable

* 🎞️ **Wide video format support**, including:

  * MP4
  * MOV
  * MKV
  * WEBM
  * MTS / M2TS
  * AVI
  * WMV
  * FLV
  * MPEG
  * TS
  * VOB
  * and more

* 👑 **One-click batch processing** for all video files in the current folder

* 🧩 **Smart resume detection** to skip already compressed files

* 🎯 **Advanced file selection options**, including:

  * Process all files
  * Process only new files
  * Select files by number
  * Select file ranges
  * Select files by format/type

* ⏸️ **Real-time pause and resume** using `F10`

* 📂 **Quickly open the working folder** using `F9`

* 🎨 **Beautiful terminal interface** powered by Rich

* 📊 **Live progress bar** with elapsed time, remaining time, percentage, and render speed

* 🪄 **Compression size preview** before processing

* 🏷️ **Automatic output naming** using `_compress.mp4`

* 📁 **Automatic old-file management** by moving original files to an `old_files` folder

* 🗑️ **Optional permanent deletion** of original files after compression

* 📝 **Detailed compression report** generated as `compression_report.txt`

* 🔔 **Desktop notifications** after the process is completed

* 🎵 **Mario-style sound effects** for startup, alerts, progress, and completion

* 📦 **Automatic dependency installer** for required Python packages

* 🌐 **UTF-8 console support for Windows** to improve text display compatibility

---

## ⚙️ How It Works

The script scans the current directory for supported video files and allows the user to choose which files should be processed.

Users can either compress all videos with one click or use the advanced selection menu to choose specific files, file ranges, pending files, or files by format.

For most video files, the tool first attempts to use **NVIDIA NVENC** for maximum encoding speed. If GPU encoding is not available, it automatically switches to **CPU-based libx264 encoding**.

After successful compression, the compressed videos remain in the main folder, while the original files are moved to an `old_files` folder for safer file management.

---

## 🛠️ Requirements

* 🐍 Python 3
* 🎬 FFmpeg installed and available in the system PATH
* 🚀 Optional NVIDIA GPU for NVENC acceleration

The following Python packages are installed automatically if missing:

* rich
* tqdm
* plyer
* keyboard
* psutil

---

## 📤 Output

For each processed video, the tool creates a compressed MP4 file:

```text
filename_compress.mp4
```

It also generates a detailed compression report:

```text
compression_report.txt
```

The report includes:

* 📅 Processing date
* 📂 Folder path
* 📦 Original file sizes
* 🎞️ Compressed file sizes
* 📉 Compression percentage
* ⏱️ Total processing time
* 🔢 Number of processed files
* 📊 Overall compression summary

---

## 🎯 Best Use Cases

This tool is ideal for quickly compressing large video files for:

* 📺 YouTube uploads
* 📱 Instagram content
* 💬 Telegram sharing
* 🗃️ Video archiving
* 👥 Client previews
* 💾 Reducing storage usage
* 🔄 Batch video conversion
* 🎬 Content production workflows

---

## 💡 Note

For the best experience, run the script inside the folder that contains your video files.

On some systems, keyboard shortcuts such as `F9` and `F10` may require administrator permission to work properly.

FFmpeg must be installed and accessible from the system PATH before running the tool.
