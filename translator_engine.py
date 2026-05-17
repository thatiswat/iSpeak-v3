#!/usr/bin/env python3
"""iSpeak v2.0 - PHASE 3 FINAL: Optimized Indian Voice Parameters"""

import torch
from faster_whisper import WhisperModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
import sounddevice as sd
import scipy.signal
import numpy as np
import subprocess
import time
import warnings
warnings.filterwarnings("ignore")

class TranslationEngine:
    def __init__(self):
        print("\n" + "="*70)
        print("🚀 iSpeak v2.0 - PHASE 3 FINAL (Optimized Voices)")
        print("="*70 + "\n")

        torch.set_grad_enabled(False)
        torch.set_num_threads(4)
        
        print("1/3 Loading Whisper BASE...")
        try:
            self.whisper = WhisperModel("base", device="cpu", compute_type="int8", cpu_threads=4)
            print("    ✅ Ready\n")
        except Exception as e:
            print(f"    ❌ Whisper Error: {e}")
            raise RuntimeError("Failed to load Whisper.")

        print("2/3 Loading IndicTrans2...")
        try:
            self.model_indic_en = AutoModelForSeq2SeqLM.from_pretrained(
                "ai4bharat/indictrans2-indic-en-dist-200M",
                trust_remote_code=True, cache_dir="./models/cache"
            )
            self.tokenizer_indic_en = AutoTokenizer.from_pretrained(
                "ai4bharat/indictrans2-indic-en-dist-200M",
                trust_remote_code=True, cache_dir="./models/cache"
            )
            self.model_indic_en.eval()

            self.model_en_indic = AutoModelForSeq2SeqLM.from_pretrained(
                "ai4bharat/indictrans2-en-indic-dist-200M",
                trust_remote_code=True, cache_dir="./models/cache"
            )
            self.tokenizer_en_indic = AutoTokenizer.from_pretrained(
                "ai4bharat/indictrans2-en-indic-dist-200M",
                trust_remote_code=True, cache_dir="./models/cache"
            )
            self.model_en_indic.eval()
            print("    ✅ Ready\n")
        except Exception as e:
            print(f"    ❌ Translation Error: {e}")
            raise RuntimeError("Failed to load IndicTrans2.")

        print("3/3 Loading IndicProcessor...")
        try:
            self.ip = IndicProcessor(inference=True)
            print("    ✅ Ready\n")
        except Exception as e:
            print(f"    ❌ Processor Error: {e}")
            raise RuntimeError("Failed to load IndicProcessor.")

        self.langs = {
            "eng_Latn": ("en", "English"),
            "hin_Deva": ("hi", "हिंदी"),
            "tam_Taml": ("ta", "தமிழ்"),
            "tel_Telu": ("te", "తెలుగు"),
            "kan_Knda": ("kn", "ಕನ್ನಡ"),
            "ben_Beng": ("bn", "বাংলা"),
            "mar_Deva": ("mr", "मराठी"),
            "guj_Gujr": ("gu", "ગુજરાતી"),
            "mal_Mlym": ("ml", "മലയാളം"),
            "pan_Guru": ("pa", "ਪੰਜਾਬੀ"),
            "urd_Arab": ("ur", "اردو"),
        }
        
        self.speaking = False
        self.history = []
        
        self.last_timings = {
            "record": 0,
            "stt": 0,
            "translate": 0,
            "tts": 0,
            "total": 0
        }
        
        self.last_confidence = 0
        
        print("="*70)
        print("✅ PHASE 3 READY: Optimized Indian Voices")
        print("="*70 + "\n")

    def record_audio(self, duration=5):
        """Record audio with timing"""
        print("🎤 Recording...")
        start_time = time.time()
        
        try:
            samplerate = 44100
            block_size = 2048
            silence_thresh = 0.012
            silence_blocks = 14

            stream = sd.InputStream(samplerate=samplerate, channels=1, dtype="float32", device=1)
            stream.start()

            audio = []
            silent_count = 0
            record_start = time.time()

            while True:
                try:
                    block_data, _ = stream.read(block_size)
                    block_data = block_data.flatten()
                    audio.extend(block_data)

                    if np.max(np.abs(block_data)) < silence_thresh:
                        silent_count += 1
                    else:
                        silent_count = 0

                    if silent_count > silence_blocks or time.time() - record_start >= duration:
                        break
                except Exception as e:
                    print(f"   ⚠️  Audio read error: {e}")
                    break

            stream.stop()
            stream.close()

            if len(audio) == 0:
                print("   ❌ No audio captured")
                return np.array([])

            audio = np.array(audio)
            recorded_len = len(audio) / samplerate
            
            self.last_timings["record"] = time.time() - start_time
            
            print(f"   ✅ Recorded {recorded_len:.1f}s ({self.last_timings['record']:.1f}s)")

            max_amp = np.max(np.abs(audio))
            if max_amp > 0.01:
                audio = audio * (0.95 / max_amp)

            audio_16k = scipy.signal.resample(audio, int(len(audio) * 16000 / samplerate))
            return audio_16k.astype(np.float32)
            
        except Exception as e:
            print(f"   ❌ Recording failed: {e}")
            return np.array([])

    def transcribe(self, audio, lang="hin_Deva"):
        """Transcribe with confidence scoring"""
        lang_code, lang_name = self.langs.get(lang, ("hi", "हिंदी"))
        
        print(f"📝 Transcribing ({lang_name})...")
        start_time = time.time()

        if len(audio) < 8000:
            print("   ❌ Audio too short")
            self.last_confidence = 0
            return ""

        try:
            prompts = {
                "en": "I you we they what when where how this is was",
                "hi": "मैं तुम हम वह क्या कब कहाँ कैसे यह है था हूँ",
                "ta": "நான் நீ நாம் அவர் என்ன எப்போது எங்கே எப்படி இது",
                "te": "నేను నువ్వు మనం అతడు ఏమిటి ఎప్పుడు ఎక్కడ ఎలా ఇది",
                "kn": "ನಾನು ನೀನು ನಾವು ಅವನು ಏನು ಯಾವಾಗ ಎಲ್ಲಿ ಹೇಗೆ ಇದು",
                "bn": "আমি তুমি আমরা তিনি কী কখন কোথায় কীভাবে এটা",
                "mr": "मी तू आम्ही तो काय कधी कुठे कसे हे",
                "gu": "હું તું આપણે તે શું ક્યારે ક્યાં કેવી રીતે આ",
                "ml": "ഞാൻ നീ നാം അവൻ എന്ത് എപ്പോൾ എവിടെ എങ്ങനെ ഇത്",
                "pa": "ਮੈਂ ਤੂੰ ਅਸੀਂ ਉਹ ਕੀ ਕਦੋਂ ਕਿੱਥੇ ਕਿਵੇਂ ਇਹ",
                "ur": "میں تم ہم وہ کیا کب کہاں کیسے یہ"
            }
            
            initial_prompt = prompts.get(lang_code, "")
            
            segments, info = self.whisper.transcribe(
                audio, 
                language=lang_code,
                initial_prompt=initial_prompt,
                beam_size=1,
                temperature=0.0,
                condition_on_previous_text=False
            )
            
            segments_list = list(segments)
            text = " ".join([s.text.strip() for s in segments_list]).strip()
            
            if segments_list:
                avg_logprob = sum(s.avg_logprob for s in segments_list) / len(segments_list)
                self.last_confidence = int(max(0, min(100, (1 + avg_logprob) * 100)))
            else:
                self.last_confidence = 0
            
            self.last_timings["stt"] = time.time() - start_time

            if text:
                words = text.split()
                if len(words) > 8:
                    unique_words = len(set(words))
                    if unique_words < len(words) * 0.5:
                        print(f"   ⚠️  Hallucination detected")
                        self.last_confidence = 0
                        return ""

            has_native = any(ord(c) > 128 for c in text if c.isalnum())

            print(f"   ⏱️  {self.last_timings['stt']:.1f}s | Confidence: {self.last_confidence}% | Native: {has_native}")
            print(f"   📝 '{text[:70]}...'")
            
            return text if len(text) > 2 else ""
            
        except Exception as e:
            print(f"   ❌ Transcription error: {e}")
            self.last_confidence = 0
            return ""

    def translate_pivot(self, text, src_lang, tgt_lang):
        """Translate with quality checking"""
        if not text:
            return "", ""

        src_name = self.langs.get(src_lang, ("?", "?"))[1]
        tgt_name = self.langs.get(tgt_lang, ("?", "?"))[1]
        
        start_time = time.time()

        try:
            if src_lang == tgt_lang:
                print(f"🔄 {src_name} → {tgt_name} (passthrough)")
                self.last_timings["translate"] = 0
                return text, text

            if src_lang == "eng_Latn" and tgt_lang == "eng_Latn":
                print(f"🔄 English → English (passthrough)")
                self.last_timings["translate"] = 0
                return text, text

            if src_lang == "eng_Latn":
                print(f"🔄 English → {tgt_name}...")
                
                batch = self.ip.preprocess_batch([text], src_lang="eng_Latn", tgt_lang=tgt_lang)
                inputs = self.tokenizer_en_indic(
                    batch, truncation=True, padding="longest", 
                    max_length=256, return_tensors="pt"
                )
                
                with torch.no_grad():
                    outputs = self.model_en_indic.generate(
                        **inputs, max_length=256, num_beams=1,
                        early_stopping=True, do_sample=False
                    )
                
                decoded = self.tokenizer_en_indic.batch_decode(outputs, skip_special_tokens=True)
                final_text = self.ip.postprocess_batch(decoded, lang=tgt_lang)[0].strip()
                
                self.last_timings["translate"] = time.time() - start_time
                
                print(f"   ✅ '{final_text[:70]}' ({self.last_timings['translate']:.1f}s)")
                
                self._add_to_history(text, final_text, text, src_lang, tgt_lang)
                
                return final_text, text

            if tgt_lang == "eng_Latn":
                print(f"🔄 {src_name} → English...")
                
                batch = self.ip.preprocess_batch([text], src_lang=src_lang, tgt_lang="eng_Latn")
                inputs = self.tokenizer_indic_en(
                    batch, truncation=True, padding="longest", 
                    max_length=256, return_tensors="pt"
                )
                
                with torch.no_grad():
                    outputs = self.model_indic_en.generate(
                        **inputs, max_length=256, num_beams=1,
                        early_stopping=True, do_sample=False
                    )
                
                decoded = self.tokenizer_indic_en.batch_decode(outputs, skip_special_tokens=True)
                english_text = self.ip.postprocess_batch(decoded, lang="eng_Latn")[0].strip()
                
                self.last_timings["translate"] = time.time() - start_time
                
                print(f"   ✅ '{english_text[:70]}' ({self.last_timings['translate']:.1f}s)")
                
                self._add_to_history(text, english_text, english_text, src_lang, tgt_lang)
                
                return english_text, english_text

            print(f"🔄 {src_name} → English...")
            
            batch = self.ip.preprocess_batch([text], src_lang=src_lang, tgt_lang="eng_Latn")
            inputs = self.tokenizer_indic_en(
                batch, truncation=True, padding="longest", 
                max_length=256, return_tensors="pt"
            )
            
            with torch.no_grad():
                outputs = self.model_indic_en.generate(
                    **inputs, max_length=256, num_beams=1,
                    early_stopping=True, do_sample=False
                )
            
            decoded = self.tokenizer_indic_en.batch_decode(outputs, skip_special_tokens=True)
            english_text = self.ip.postprocess_batch(decoded, lang="eng_Latn")[0].strip()
            
            if not english_text or len(english_text) < 2:
                print(f"   ❌ Translation to English failed")
                self.last_timings["translate"] = time.time() - start_time
                return "", ""
                
            print(f"   ✅ '{english_text[:70]}'")

            print(f"🔄 English → {tgt_name}...")
            
            batch = self.ip.preprocess_batch([english_text], src_lang="eng_Latn", tgt_lang=tgt_lang)
            inputs = self.tokenizer_en_indic(
                batch, truncation=True, padding="longest", 
                max_length=256, return_tensors="pt"
            )
            
            with torch.no_grad():
                outputs = self.model_en_indic.generate(
                    **inputs, max_length=256, num_beams=1,
                    early_stopping=True, do_sample=False
                )
            
            decoded = self.tokenizer_en_indic.batch_decode(outputs, skip_special_tokens=True)
            final_text = self.ip.postprocess_batch(decoded, lang=tgt_lang)[0].strip()
            
            self.last_timings["translate"] = time.time() - start_time
            
            if not final_text or len(final_text) < 2:
                print(f"   ❌ Translation to {tgt_name} failed")
                return english_text, english_text
                
            print(f"   ✅ '{final_text[:70]}'")
            print(f"   ⏱️  Total translation: {self.last_timings['translate']:.1f}s")
            
            self._add_to_history(text, final_text, english_text, src_lang, tgt_lang)
            
            return final_text, english_text
            
        except Exception as e:
            print(f"   ❌ Translation error: {e}")
            self.last_timings["translate"] = time.time() - start_time
            return "", ""

    def speak(self, text, lang):
        """TTS with optimized Indian voice parameters"""
        if self.speaking or not text:
            return

        self.speaking = True
        print("🔊 Speaking...")
        start_time = time.time()

        # OPTIMIZED: Indian language voice parameters
        voice_config = {
            "hin_Deva": {
                "voice": "hi+m3",
                "speed": "145",
                "amplitude": "200",
                "pitch": "45",
                "gap": "10"
            },
            "tam_Taml": {
                "voice": "ta+m3",
                "speed": "140",
                "amplitude": "200",
                "pitch": "48",
                "gap": "10"
            },
            "tel_Telu": {
                "voice": "te+m3",
                "speed": "145",
                "amplitude": "200",
                "pitch": "46",
                "gap": "10"
            },
            "kan_Knda": {
                "voice": "kn+m3",
                "speed": "145",
                "amplitude": "200",
                "pitch": "47",
                "gap": "10"
            },
            "ben_Beng": {
                "voice": "bn+m3",
                "speed": "140",
                "amplitude": "200",
                "pitch": "50",
                "gap": "10"
            },
            "mar_Deva": {
                "voice": "mr+m3",
                "speed": "145",
                "amplitude": "200",
                "pitch": "45",
                "gap": "10"
            },
            "guj_Gujr": {
                "voice": "gu+m3",
                "speed": "140",
                "amplitude": "200",
                "pitch": "48",
                "gap": "10"
            },
            "mal_Mlym": {
                "voice": "ml+m3",
                "speed": "145",
                "amplitude": "200",
                "pitch": "46",
                "gap": "10"
            },
            "pan_Guru": {
                "voice": "pa+m3",
                "speed": "150",
                "amplitude": "200",
                "pitch": "44",
                "gap": "10"
            },
            "urd_Arab": {
                "voice": "ur+m3",
                "speed": "140",
                "amplitude": "200",
                "pitch": "47",
                "gap": "10"
            },
            "eng_Latn": {
                "voice": "en-gb+m3",
                "speed": "145",
                "amplitude": "200",
                "pitch": "46",
                "gap": "10"
            }
        }
        
        config = voice_config.get(lang, voice_config["eng_Latn"])

        try:
            result = subprocess.run([
                "espeak-ng",
                "-v", config["voice"],
                "-s", config["speed"],
                "-a", config["amplitude"],
                "-p", config["pitch"],
                "-g", config["gap"],
                str(text)
            ],
            timeout=15,
            check=False,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
            )
            
            self.last_timings["tts"] = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ Done ({self.last_timings['tts']:.1f}s)")
            else:
                print(f"   ⚠️  TTS warning (code {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print("   ❌ TTS timeout")
        except Exception as e:
            print(f"   ❌ TTS Error: {e}")

        self.speaking = False

    def _add_to_history(self, source, target, english, src_lang, tgt_lang):
        """Add translation to history (last 5)"""
        entry = {
            "source": source,
            "target": target,
            "english": english,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "confidence": self.last_confidence,
            "timestamp": time.time()
        }
        
        self.history.append(entry)
        
        if len(self.history) > 5:
            self.history.pop(0)

    def get_performance_summary(self):
        """Get performance breakdown"""
        total = sum([
            self.last_timings["record"],
            self.last_timings["stt"],
            self.last_timings["translate"],
            self.last_timings["tts"]
        ])
        self.last_timings["total"] = total
        
        return self.last_timings

    def get_history(self):
        """Get conversation history"""
        return self.history

    def get_last_confidence(self):
        """Get last STT confidence"""
        return self.last_confidence
