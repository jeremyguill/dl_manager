import subprocess
import os
import re
import json
import sys

def check_and_install_yt_dlp():
    """Checks if yt-dlp is installed and installs it if not."""
    try:
        subprocess.run(['yt-dlp', '--version'], check=True, capture_output=True)
        print("yt-dlp is already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("yt-dlp not found. Attempting to install...")
        try:
            # Ensure pip is available
            subprocess.run([sys.executable, '-m', 'pip', '--version'], check=True, capture_output=True)
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], check=True)
            print("yt-dlp installed successfully.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to install yt-dlp using pip: {e}")
            print("Please install yt-dlp manually (e.g., pip install yt-dlp) or ensure pip is in your PATH.")
            sys.exit(1)

def download_video(url):
    """Downloads video in 720p MP4 format with audio."""
    print(f"Downloading video from: {url}")
    try:
        subprocess.run(['yt-dlp', '-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]', '--recode-video', 'mp4', '-o', '%(title)s.mp4', url], check=True)
        print("Video download complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")

def download_audio(url):
    """Downloads audio only in MP3 format."""
    print(f"Downloading audio from: {url}")
    try:
        subprocess.run(['yt-dlp', '-x', '--audio-format', 'mp3', '-o', '%(title)s.mp3', url], check=True)
        print("Audio download complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading audio: {e}")

def download_and_parse_transcript(url):
    """Downloads transcript, parses it, and saves as a TXT file."""
    print(f"Downloading transcript from: {url}")
    try:
        # Get video title for filename
        info_json = subprocess.run(['yt-dlp', '--print-json', '--skip-download', url], capture_output=True, text=True, check=True).stdout
        info = json.loads(info_json)
        title = info.get('title', 'transcript')
        # Sanitize title for filename
        title = re.sub(r'[<>:"/\\|?*]', '', title) # Remove invalid characters for filenames

        srt_filename = f"{title}.en.srt"
        txt_filename = f"{title}_transcript.txt"

        # Download SRT transcript
        subprocess.run(['yt-dlp', '--write-auto-subs', '--sub-langs', 'en', '--skip-download', '-o', f'{title}.%(ext)s', url], check=True)

        if not os.path.exists(srt_filename):
            print(f"SRT file not found: {srt_filename}. Trying to locate any .srt file...")
            # Fallback to finding any .srt file if the exact name isn't found
            found_srt = False
            for f in os.listdir('.'):
                if f.endswith('.srt') and title in f:
                    srt_filename = f
                    found_srt = True
                    break
            if not found_srt:
                print("Could not locate SRT file. Aborting transcript parsing.")
                return

        print(f"Parsing transcript from: {srt_filename}")
        with open(srt_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        parsed_transcript = []
        timestamp_pattern = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$')
        sequence_pattern = re.compile(r'^\d+$')

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if sequence_pattern.match(line):
                continue
            if timestamp_pattern.match(line):
                continue

            cleaned_line = re.sub(r'<[^>]*>', '', line)
            if cleaned_line:
                parsed_transcript.append(cleaned_line)

        full_text = ' '.join(parsed_transcript)
        output_chars = []
        capitalize_next = True
        for char in full_text:
            if capitalize_next and char.isalpha():
                output_chars.append(char.upper())
                capitalize_next = False
            else:
                output_chars.append(char)

            if char in ('.', '!', '?'):
                capitalize_next = True
            elif char.isspace() and capitalize_next:
                continue
            elif not char.isalpha() and not char.isspace() and capitalize_next:
                continue
            else:
                capitalize_next = False

        output_text = ''.join(output_chars)
        output_text = re.sub(r'\s+', ' ', output_text).strip()
        output_text = re.sub(r'([.!?])([A-Za-z0-9])', r'\1 \2', output_text)
        output_text = re.sub(r'\s+([.,!?;:])', r'\1', output_text)
        if output_text:
            output_text = output_text[0].upper() + output_text[1:]

        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        print(f"Transcript saved to: {txt_filename}")
        os.remove(srt_filename) # Clean up the downloaded SRT file

    except subprocess.CalledProcessError as e:
        print(f"Error downloading or processing transcript: {e}")
        print(f"Command: {e.cmd}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    check_and_install_yt_dlp()

    urls = []
    try:
        with open('urls.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: urls.txt not found. Please create a urls.txt file with one URL per line.")
        return

    if not urls:
        print("No URLs found in urls.txt. Please add URLs to the file.")
        return

    while True:
        print("\n--- Video Downloader Menu ---")
        print("1. Download video (720p MP4 with audio)")
        print("2. Download audio only (MP3)")
        print("3. Download and parse transcript (TXT)")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            for url in urls:
                download_video(url)
        elif choice == '2':
            for url in urls:
                download_audio(url)
        elif choice == '3':
            for url in urls:
                download_and_parse_transcript(url)
        elif choice == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
