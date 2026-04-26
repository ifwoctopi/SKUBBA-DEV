import subprocess
import os
import platform

class PiperTTS:
    """Simple TTS using system TTS or pyttsx3 fallback"""

    def __init__(self, voice="default"):
        """
        Initialize TTS

        Args:
            voice: str - voice to use (system dependent)
        """
        self.voice = voice
        self.system = platform.system()

    def is_available(self):
        """Check if TTS is available"""
        try:
            if self.system == "Windows":
                # Check if PowerShell TTS is available
                result = subprocess.run(
                    ["powershell", "-Command", "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak('test')"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            elif self.system == "Darwin":  # macOS
                result = subprocess.run(["say", "test"], capture_output=True, timeout=60)
                return result.returncode == 0
            else:  # Linux
                result = subprocess.run(["espeak", "test"], capture_output=True, timeout=60)
                return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def speak(self, text):
        """
        Convert text to speech

        Args:
            text: str - text to speak

        Returns:
            bool - True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                # Use Windows built-in TTS
                cmd = [
                    "powershell",
                    "-Command",
                    f"Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak('{text.replace(chr(39), chr(39)+chr(39))}')"
                ]
                subprocess.run(cmd, timeout=60)
                return True

            elif self.system == "Darwin":  # macOS
                subprocess.run(["say", text], timeout=60)
                return True

            else:  # Linux
                # Try espeak first, then festival
                try:
                    subprocess.run(["espeak", text], timeout=60)
                    return True
                except FileNotFoundError:
                    try:
                        subprocess.run(["festival", "--tts"], input=text.encode(), timeout=60)
                        return True
                    except FileNotFoundError:
                        print("No TTS system found. Install espeak: sudo apt install espeak")
                        return False

        except subprocess.TimeoutExpired:
            print("TTS timeout")
            return False
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            return False
