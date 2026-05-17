# iSpeak v3.0

Offline Multilingual Edge AI Translator for Indian Languages built on Raspberry Pi 4.

iSpeak v3.0 is a fully offline AI-powered speech translation system capable of real-time multilingual communication using on-device AI inference without internet connectivity.

The system integrates:
- Offline Speech Recognition (STT)
- Neural Machine Translation (NMT)
- Offline Text-to-Speech (TTS)
- Embedded OLED UI
- GPIO hardware interaction
- ARM CPU optimized inference

Designed for:
- Rural communication
- Low-connectivity environments
- Privacy-sensitive deployments
- Accessibility systems
- Portable AI communication devices

# Demo

## Hardware Setup
<img width="1024" height="1536" alt="WhatsApp Image 2026-05-17 at 12 06 59" src="https://github.com/user-attachments/assets/2116d944-a3fe-4433-ad62-34cc2c8a7873" />
<img width="1600" height="900" alt="WhatsApp Image 2026-05-17 at 12 13 02" src="https://github.com/user-attachments/assets/e9f9e0fb-6657-44ec-ba0b-7365c148344e" />

## OLED Interface
<img width="3766" height="2118" alt="WhatsApp Image 2026-05-17 at 12 14 04" src="https://github.com/user-attachments/assets/7e339b38-62e5-4c8c-a14f-5d722044674c" />

## Translation Demo
<img width="518" height="338" alt="Screenshot 2026-05-17 at 12 04 25 PM" src="https://github.com/user-attachments/assets/a9f1fc0b-46ea-4ede-9d42-ac8a443a4778" />
<img width="497" height="283" alt="Picture1" src="https://github.com/user-attachments/assets/8ca18eb7-2c48-473f-85fb-50daf1d5c659" />

# Features

- Fully offline multilingual speech translation
- Sub-10 second end-to-end latency
- Indian language support
- Real-time speech-to-speech pipeline
- OLED embedded UI
- GPIO button controls
- Replay mode
- Confidence scoring
- Hallucination filtering
- ARM CPU optimized inference
- Native script translation
- Portable embedded deployment

# System Architecture

Speech Input
    ↓
Whisper STT
    ↓
IndicTrans2 Translation
    ↓
espeak-ng TTS
    ↓
Audio Output

# Supported Languages

| Language | Script |
|---|---|
| Hindi | Devanagari |
| Tamil | Tamil |
| Telugu | Telugu |
| Kannada | Kannada |
| Bengali | Bengali |
| Marathi | Devanagari |
| Gujarati | Gujarati |
| Malayalam | Malayalam |
| Punjabi | Gurmukhi |
| Urdu | Arabic |

# Hardware Stack

- Raspberry Pi 4 (8GB)
- 128x64 OLED Display
- USB Microphone
- Speaker Output
- GPIO Buttons

# Software Stack

## AI/ML
- PyTorch
- Transformers
- Faster-Whisper
- IndicTrans2

## Embedded
- RPi.GPIO
- adafruit_ssd1306
- sounddevice
- scipy
- numpy
- PIL

# Performance

| Stage | Time |
|---|---|
| Audio Recording | 3–5s |
| Whisper STT | 2–3s |
| Translation | 2–3s |
| TTS | ~1s |
| Total | <10s |

# Project Structure

```text
iSpeak-v3/
│
├── ispeak_v2.py
├── translator_engine.py
├── hardware.py
│
├── requirements.txt
├── README.md
│
├── assets/
│   ├── oled_ui.jpg
│   ├── hardware_setup.jpg
│   └── demo.gif
│
└── models/


# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/iSpeak-v3.git
cd iSpeak-v3
```

## Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run

```bash
python3.11 ispeak_v2.py
```

---

# Engineering Challenges Solved

- Running transformer inference on ARM CPUs
- Offline multilingual AI deployment
- Reducing latency from ~60s to under 10s
- Real-time audio pipeline orchestration
- Embedded OLED UI rendering
- Native Indian language handling
- Memory-aware model deployment

# Future Improvements

- Offline conversational AI
- llama.cpp integration
- Quantized LLM support
- Auto language detection
- Streaming translation
- Noise suppression
- Real-time subtitles

# Author

Vishal S

Embedded AI | Edge Computing | Multilingual NLP | Raspberry Pi Systems
