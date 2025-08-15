import yt_dlp
import whisper
import tempfile
import os
import re
import ast
import subprocess
import asyncio
import base64
from openai import OpenAI
from moviepy.video.io.VideoFileClip import VideoFileClip
from typing import Callable, Optional, Dict, Any, List, Tuple
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VideoProcessor:
    def __init__(self, job_id: str, storage_dir: str = None):
        self.job_id = job_id
        
        # Use absolute path for storage directory
        if storage_dir is None:
            # Default to /app/storage/videos in Docker, or ./storage/videos locally
            if os.path.exists("/app"):
                # Running in Docker container
                self.storage_dir = Path("/app/storage/videos")
            else:
                # Running locally
                self.storage_dir = Path("./storage/videos")
        else:
            self.storage_dir = Path(storage_dir)
        
        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        print(f"Using storage directory: {self.storage_dir.absolute()}")
        
        # Create temp folder for this job
        self.temp_dir = Path(tempfile.mkdtemp())
        self.video_path = self.temp_dir / "input.mp4"
        self.output_path = self.storage_dir / f"{job_id}.mp4"
        
        # Load API keys from environment variables
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def _create_temp_cookies_file(self) -> Optional[str]:
        """Create temporary cookies file from environment variable or file"""
        # First try base64 encoded cookies (for deployment)
        cookies_b64 = os.getenv("YOUTUBE_COOKIES_B64")
        if cookies_b64:
            try:
                cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
                
                # Filter out malformed cookie entries
                filtered_lines = []
                for line in cookies_content.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        filtered_lines.append(line)
                        continue
                    
                    # Check if line has the correct format (7 tab-separated fields)
                    parts = line.split('\t')
                    if len(parts) == 7:
                        # Additional validation: check if the cookie value doesn't contain newlines
                        if '\n' not in parts[6]:
                            filtered_lines.append(line)
                        else:
                            print(f"Skipping cookie with newline in value: {parts[0]}")
                    else:
                        print(f"Skipping malformed cookie line: {line[:50]}...")
                
                # Write filtered cookies
                cookies_file = self.temp_dir / "cookies.txt"
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(filtered_lines))
                
                print(f"Using base64-encoded cookies from environment variable (filtered)")
                return str(cookies_file)
            except Exception as e:
                print(f"Failed to decode base64 cookies: {e}")
        
        # Fallback to file-based cookies (for local development)
        cookies_file = os.getenv("YOUTUBE_COOKIES_FILE")
        if cookies_file and os.path.exists(cookies_file):
            print(f"Using cookies from file: {cookies_file}")
            return cookies_file
        
        # Try to find cookies.txt in common locations
        common_paths = [
            "cookies.txt",
            "../cookies.txt",
            "backend/cookies.txt",
            "/app/cookies.txt"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"Using cookies from: {path}")
                return path
        
        print("No cookies found - YouTube downloads may fail for restricted videos")
        return None
    
    async def process_video(self, youtube_url: str, instructions: str = "", 
                          progress_callback: Optional[Callable[[int, str], None]] = None) -> Dict[str, Any]:
        """Process a YouTube video with progress updates"""
        
        def update_progress(progress: int, step: str):
            if progress_callback:
                progress_callback(progress, step)
        
        try:
            # Step 1: Download video (0-25%)
            update_progress(0, "Downloading video...")
            await self._download_youtube_video(youtube_url, str(self.video_path))
            update_progress(25, "Video downloaded successfully")
            
            # Step 2: Transcribe video (25-50%)
            update_progress(25, "Transcribing video with AI...")
            transcript = await self._transcribe_video(str(self.video_path))
            update_progress(50, "Transcription completed")
            
            # Step 3: Process with GPT and identify clips (50-75%)
            update_progress(50, "Analyzing content and identifying clips...")
            timestamps = await self._identify_clips(transcript, instructions)
            update_progress(75, "Clips identified")
            
            # Step 4: Render final video (75-100%)
            update_progress(75, "Rendering final video...")
            clips_info = await self._render_video(str(self.video_path), timestamps)
            update_progress(100, "Video processing completed")
            
            # Verify the output file was created
            print(f"Final output path: {self.output_path}")
            print(f"Output file exists: {self.output_path.exists()}")
            if self.output_path.exists():
                print(f"Output file size: {self.output_path.stat().st_size} bytes")
                # Store video data in job for Railway's ephemeral storage
                try:
                    with open(self.output_path, 'rb') as f:
                        video_data = f.read()
                    # Store as base64 for job storage
                    import base64
                    video_data_b64 = base64.b64encode(video_data).decode('utf-8')
                    # This will be stored in the job object by the main.py
                    print(f"Video data encoded and ready for storage")
                except Exception as e:
                    print(f"Warning: Could not encode video data: {e}")
            else:
                print("WARNING: Output file was not created!")
            
            # Clean up temp files
            self._cleanup_temp_files()
            
            return {
                "video_path": str(self.output_path),
                "clips": clips_info,
                "transcript": transcript,
                "video_data": video_data_b64 if self.output_path.exists() else None
            }
            
        except Exception as e:
            self._cleanup_temp_files()
            raise e
    
    async def _download_youtube_video(self, youtube_url: str, output_path: str):
        """Download YouTube video with cookie support and comprehensive 403 error handling"""
        def download():
            # Get cookies (either from file or base64 encoded)
            cookies_file = self._create_temp_cookies_file()
            
            # First, try to extract video info to validate the URL
            info_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            if cookies_file:
                info_opts['cookiefile'] = cookies_file
            
            try:
                print("Validating YouTube URL...", flush=True)
                with yt_dlp.YoutubeDL(info_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    print(f"Video title: {info.get('title', 'Unknown')}", flush=True)
                    print(f"Video duration: {info.get('duration', 'Unknown')} seconds", flush=True)
            except Exception as e:
                print(f"Warning: Could not extract video info: {e}", flush=True)
                # Continue anyway, might still be able to download
            
            # Multiple user agents to try
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
            ]
            
            # Multiple format strategies to try
            format_strategies = [
                'best[height<=720]/best',
                'worst[height<=480]/worst',
                'best[height<=480]/best',
                'worst[height<=360]/worst',
                'best[ext=mp4]/best',
                'best[ext=webm]/best',
                'best'
            ]
            
            # Base yt-dlp options
            base_ydl_opts = {
                'outtmpl': output_path,
                'merge_output_format': 'mp4',
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_warnings': False,
                'quiet': False,
                'verbose': True,
                'extract_flat': False,
                'force_generic_extractor': False,
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
                'keepvideo': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'prefer_ffmpeg': True,
                'ffmpeg_location': 'ffmpeg',
            }
            
            # Add cookies if available
            if cookies_file:
                base_ydl_opts['cookiefile'] = cookies_file
                print(f"Using cookies from: {cookies_file}")
                # Verify cookies file format
                try:
                    with open(cookies_file, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if not first_line.startswith('# Netscape HTTP Cookie File'):
                            print(f"Warning: Cookies file may not be in correct format. First line: {first_line[:50]}...")
                except Exception as e:
                    print(f"Warning: Could not verify cookies file format: {e}")
            else:
                print("No cookies file available - some videos may fail to download")
            
            download_successful = False
            
            # Strategy 1: Try with cookies first
            if cookies_file:
                print("Strategy 1: Trying with cookies...", flush=True)
                try:
                    ydl_opts = base_ydl_opts.copy()
                    ydl_opts['user_agent'] = user_agents[0]
                    ydl_opts['format'] = format_strategies[0]
                    ydl_opts['http_headers'] = {
                        'User-Agent': user_agents[0],
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        print("Download successful with cookies", flush=True)
                        download_successful = True
                        return
                except Exception as e:
                    print(f"Strategy 1 failed: {e}", flush=True)
            
            # Strategy 2: Try different user agents and formats without cookies
            print("Strategy 2: Trying different user agents and formats...", flush=True)
            for user_agent in user_agents[:3]:  # Try first 3 user agents
                for format_strategy in format_strategies[:4]:  # Try first 4 format strategies
                    try:
                        ydl_opts = base_ydl_opts.copy()
                        ydl_opts.pop('cookiefile', None)  # Remove cookies
                        ydl_opts['user_agent'] = user_agent
                        ydl_opts['format'] = format_strategy
                        ydl_opts['http_headers'] = {
                            'User-Agent': user_agent,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Cache-Control': 'max-age=0',
                        }
                        
                        print(f"Trying user agent: {user_agent[:50]}... with format: {format_strategy}", flush=True)
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([youtube_url])
                        
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            print(f"Download successful with user agent: {user_agent[:50]}... and format: {format_strategy}", flush=True)
                            download_successful = True
                            return
                    except Exception as e:
                        print(f"Failed with user agent {user_agent[:50]}... and format {format_strategy}: {e}", flush=True)
                        continue
            
            # Strategy 3: Try with different extraction methods
            print("Strategy 3: Trying different extraction methods...", flush=True)
            extraction_methods = [
                {'extractor_args': {'youtube': {'skip': ['dash', 'live']}}},
                {'extractor_args': {'youtube': {'player_client': ['android']}}},
                {'extractor_args': {'youtube': {'player_client': ['web']}}},
                {'extractor_args': {'youtube': {'player_client': ['tv_embedded']}}},
            ]
            
            for method in extraction_methods:
                try:
                    ydl_opts = base_ydl_opts.copy()
                    ydl_opts.pop('cookiefile', None)
                    ydl_opts['user_agent'] = user_agents[0]
                    ydl_opts['format'] = 'best[height<=480]/best'
                    ydl_opts.update(method)
                    
                    print(f"Trying extraction method: {method}", flush=True)
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        print(f"Download successful with extraction method: {method}", flush=True)
                        download_successful = True
                        return
                except Exception as e:
                    print(f"Extraction method failed: {e}", flush=True)
                    continue
            
            # Strategy 4: Try with minimal options (last resort)
            print("Strategy 4: Trying with minimal options...", flush=True)
            try:
                minimal_opts = {
                    'outtmpl': output_path,
                    'format': 'best',
                    'quiet': False,
                    'no_warnings': False,
                    'verbose': True,
                }
                
                with yt_dlp.YoutubeDL(minimal_opts) as ydl:
                    ydl.download([youtube_url])
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print("Download successful with minimal options", flush=True)
                    download_successful = True
                    return
            except Exception as e:
                print(f"Minimal options failed: {e}", flush=True)
            
            # If all strategies failed
            if not download_successful:
                raise Exception("All download strategies failed. This video may be restricted or unavailable.")
        
        # Run download in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download)
    
    async def _transcribe_video(self, video_path: str) -> List[Tuple[str, float, float]]:
        """Transcribe video using Whisper"""
        def transcribe():
            start_time = time.time()
            
            # Check if video file exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Check file size
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                raise ValueError(f"Video file is empty: {video_path}")
            
            print(f"Video file size: {file_size} bytes", flush=True)
            print(f"Video file path: {video_path}", flush=True)
            print(f"Video file absolute path: {os.path.abspath(video_path)}", flush=True)
            
            # Check if file is readable
            try:
                with open(video_path, 'rb') as f:
                    # Try to read first few bytes to verify file is accessible
                    f.read(1024)
                print("Video file is readable", flush=True)
            except Exception as e:
                raise IOError(f"Cannot read video file {video_path}: {e}")
            
            try:
                print("Starting Whisper transcription...", flush=True)
                model = whisper.load_model("base")
                print("Model loaded.", flush=True)
                result = model.transcribe(video_path, language="en")
                print("Whisper transcription complete.", flush=True)
                ...
            except Exception as e:
                print(f"Transcription failed: {e}", flush=True)
                raise
            
            transcript = []
            for segment in result['segments']:
                transcript.append((segment['text'], segment['start'], segment['end']))
            
            end_time = time.time()
            print("transcription took" + str(end_time - start_time) + "seconds")
            print(transcript)
            return transcript
        
        # Run transcription in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, transcribe)
    
    async def _identify_clips(self, transcript: List[Tuple[str, float, float]], instructions: str) -> List[Dict[str, float]]:
        """Use GPT to identify relevant clips"""
        def process_with_gpt():
            user_prompt = instructions if instructions else "Find the most engaging and important moments in this video"
            
            prompt = f"""
            Here is the transcript of the video: {transcript}
            
            Instructions: {user_prompt}
            
            Please identify the most relevant time intervals in the video based on the instructions.
            Return only the timestamps in this exact format: [{{'start': 12.4, 'end': 54.6}}, ...]
            """
            
            client = OpenAI(api_key=self.openai_key)
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a precise and efficient video clipping assistant.

Given a transcript of a video and a user request, your job is to extract the most relevant time intervals that match the intent of the request.

Provide just enough context for the user to understand what's happening, but avoid unnecessary filler. Be decisive—separate clips only when the topic, speaker, or scene clearly shifts. Minimize the number of clips while maintaining clarity.

Return only a list of timestamp dictionaries in this exact format:
[{'start': 12.4, 'end': 54.6}, {'start': 110.2, 'end': 132.0}]

Do not include any explanation or commentary—just the list of relevant timestamp ranges.
"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            print("GPT RESPONSE:", completion.choices[0].message.content, flush=True)
            
            # Extract timestamps
            match = re.search(r"\[\s*{.*?}\s*\]", completion.choices[0].message.content, re.DOTALL)
            if not match:
                raise ValueError("No valid timestamp list found in GPT response")
            
            return ast.literal_eval(match.group(0))
        
        # Run GPT processing in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, process_with_gpt)
    
    async def _render_video(self, video_path: str, timestamps: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Render the final video with identified clips using ffmpeg for fast stitching"""
        def render():
            clips_info = []
            temp_clips = []
            concat_list_path = self.temp_dir / "concat_list.txt"
            video_duration = None

            # Get video duration using ffprobe
            try:
                import json
                result = subprocess.run([
                    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video_path)
                ], capture_output=True, text=True)
                video_duration = float(json.loads(result.stdout)["format"]["duration"])
            except Exception:
                video_duration = None

            for i, timestamp in enumerate(timestamps):
                start_time = max(0, timestamp['start'])
                end_time = min(timestamp['end'], video_duration) if video_duration else timestamp['end']
                if end_time <= start_time:
                    continue  # skip invalid clips
                out_clip = self.temp_dir / f"clip_{i+1}.mp4"
                temp_clips.append(out_clip)
                # ffmpeg command to extract subclip
                cmd = [
                    "ffmpeg", "-y", "-i", str(video_path),
                    "-ss", str(start_time), "-to", str(end_time),
                    "-avoid_negative_ts", "make_zero", str(out_clip)
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                clips_info.append({
                    "id": str(i + 1),
                    "title": f"Clip {i + 1}",
                    "duration": f"{end_time - start_time:.1f}s",
                    "timeframe": f"{start_time:.1f}s - {end_time:.1f}s",
                    "start": start_time,
                    "end": end_time
                })

            # Write concat list file
            with open(concat_list_path, "w") as f:
                for clip_path in temp_clips:
                    f.write(f"file '{clip_path}'\n")

            # ffmpeg concat command
            concat_cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_path),
                "-c", "copy", str(self.output_path)
            ]
            print(f"Running ffmpeg concat command: {' '.join(concat_cmd)}")
            result = subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"ffmpeg concat result: {result.returncode}")
            print(f"Output file after concat: {self.output_path.exists()}")
            if self.output_path.exists():
                print(f"Output file size after concat: {self.output_path.stat().st_size} bytes")

            # Optionally, cleanup temp clips (but not self.output_path)
            for clip_path in temp_clips:
                if clip_path.exists():
                    try:
                        os.remove(clip_path)
                    except Exception:
                        pass
            if concat_list_path.exists():
                try:
                    os.remove(concat_list_path)
                except Exception:
                    pass

            return clips_info

        # Run rendering in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, render)
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temp files: {e}")
    
    def get_video_info(self) -> Dict[str, Any]:
        """Get information about the processed video"""
        if not self.output_path.exists():
            return {}
        
        try:
            with VideoFileClip(str(self.output_path)) as clip:
                return {
                    "duration": clip.duration,
                    "fps": clip.fps,
                    "size": (clip.w, clip.h),
                    "file_size": self.output_path.stat().st_size
                }
        except Exception:
            return {} 
 