# Skin Scanner with AI Analysis & Text-to-Speech

This application combines a trained skin condition detection model with local AI analysis (Ollama) and text-to-speech (System TTS) to provide comprehensive skincare insights.

## Features

- 🎥 Real-time skin condition detection (Acne, Clear, Dark Circles)
- 🤖 Local AI analysis using Ollama LLM with user context
- 🔊 Text-to-speech feedback using System TTS
- 💾 Automatic image saving with high confidence predictions
- ⌨️ Manual analysis mode for on-demand assessment
- 🖥️ On-screen interface with live status updates and AI results
- 📝 Interactive context input directly in the camera window

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install opencv-python torch torchvision requests
```

### 2. Setup Ollama (Local LLM)

Ollama provides a local language model for AI analysis without external API calls.

**Installation:**
- Download and install from [ollama.ai](https://ollama.ai)

**Pulling a Model:**
```bash
ollama pull llama2
# or for a smaller model:
ollama pull mistral
```

**Verify Installation:**
```bash
ollama list  # Should show your downloaded models
```

**Note:** No need to run `ollama serve` - the application will call Ollama directly when needed.

The application defaults to `llama2`. You can change the model in `webcam-test.py`:
```python
ai = OllamaAI(model_name="mistral")  # Available: llama2, mistral, neural-chat, etc.
```

### 3. Setup Text-to-Speech (System TTS)

The application uses your system's built-in text-to-speech capabilities:

**Windows:** Uses PowerShell System.Speech.Synthesis (built-in)
**macOS:** Uses `say` command (built-in)  
**Linux:** Uses `espeak` (install with: `sudo apt install espeak`)

No additional setup required - the application will automatically detect and use your system's TTS.

### 4. Required Files

Ensure you have in the `SKUBBA-DEV/` directory:
- `skin_model_weights.pth` - Pre-trained skin condition model
- `haarcascade_frontalface_default.xml` - Face cascade classifier
- All Python files (model.py, webcam-test.py, etc.)

## Running the Application

```bash
python webcam-test.py
```

## Usage

1. **Start the Scanner**
   - The camera window will appear immediately
   - Status messages show AI and TTS availability
   - Press any key to start scanning

2. **Detection & Analysis**
   - Real-time skin condition detection with confidence scores
   - When a high-confidence condition is detected:
     - On-screen prompt appears for context input
     - Type your context and press Enter (or press Enter to skip)
     - AI analysis appears on-screen with recommendations
     - Text-to-speech speaks the analysis

3. **Keyboard Controls**
   - **'a'** - Manual analysis of current prediction (anytime)
   - **'q'** - Quit the application
   - **Enter** - Submit context input
   - **Escape** - Skip context input
   - **Backspace** - Delete characters in context input

4. **On-Screen Information**
   - Current prediction and confidence score
   - AI analysis results (when available)
   - Context input prompts
   - Control instructions (when idle)

## Troubleshooting

### Ollama Issues
```
Ollama is not installed
```
**Solution:** Install from [ollama.ai](https://ollama.ai)

```
Ollama model 'llama2' not found
```
**Solution:** Run `ollama pull llama2` to download the model

### TTS Issues
```
TTS is not available
```
**Solution:** 
- **Windows:** System TTS should work automatically
- **macOS:** System TTS should work automatically  
- **Linux:** Install espeak: `sudo apt install espeak`

### Audio Not Playing
- **Windows:** Ensure PowerShell has access to audio devices
- **Linux:** Install `espeak` (`sudo apt install espeak`)
- **Mac:** `say` command should be available by default

### Camera Not Found
```
Camera not available
```
**Solution:** 
- Check if another application is using the camera
- Ensure camera is properly connected
- Try restarting the application

## File Structure

```
SKUBBA-DEV/
├── webcam-test.py          # Main application
├── model.py                 # Skin condition model
├── ollama_helper.py         # Ollama integration
├── tts_helper.py            # System TTS integration
├── db_helper.py             # Database utilities
├── database.py              # Database handling
├── face_scanner.py          # Face detection utilities
├── skin_model_weights.pth   # Pre-trained model weights
├── haarcascade_frontalface_default.xml  # Face cascade
├── acne_products.json       # Product database
└── images/                  # Saved scan images (auto-created)
```

## Customization

### Change LLM Model
Edit `webcam-test.py`:
```python
ai = OllamaAI(model_name="mistral")  # Available: llama2, mistral, neural-chat, etc.
```

### Change Voice
Edit `webcam-test.py`:
```python
tts = PiperTTS()  # Uses system default voice
```
**Note:** Voice selection depends on your operating system TTS settings.

### Adjust Confidence Threshold
Edit `webcam-test.py`:
```python
if confidence < 0.8:  # Changed from 0.7
    label = "Unsure"
```

### Change Save Interval
Edit `webcam-test.py`:
```python
interval = 10  # Changed from 5 seconds
```

## Future Enhancements

- [ ] Database storage integration
- [ ] Historical tracking and trends
- [ ] Multi-language support
- [ ] Integration with skincare product recommendations
- [ ] Web interface for remote access
- [ ] Mobile app companion
