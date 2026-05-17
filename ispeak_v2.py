#!/usr/bin/env python3
"""iSpeak v2.0 - PHASE 3 FINAL: Perfect Font Sizing for 1.3" OLED"""

from hardware_v2 import Hardware
from translator_engine_v2 import TranslationEngine
import time
import threading

LANGUAGES = [
    ("eng_Latn", "English"),
    ("hin_Deva", "Hindi"),
    ("tam_Taml", "Tamil"),
    ("tel_Telu", "Telugu"),
    ("ben_Beng", "Bengali"),
    ("mar_Deva", "Marathi"),
    ("guj_Gujr", "Gujarati"),
    ("kan_Knda", "Kannada"),
    ("mal_Mlym", "Malayalam"),
    ("pan_Guru", "Punjabi"),
    ("urd_Arab", "Urdu"),
]

def main():
    print("\n" + "="*70)
    print("🚀 iSpeak v2.0 - PHASE 3 FINAL")
    print("="*70 + "\n")
    
    # Initialize hardware
    try:
        print("Initializing Hardware...")
        hw = Hardware(button1_pin=23, button2_pin=24)
        hw.show_logo()
        time.sleep(1.5)
    except Exception as e:
        print(f"❌ Hardware initialization failed: {e}")
        return
    
    # Initialize engine
    try:
        loading = True
        def animate_loading():
            frame = 0
            while loading:
                hw.display_spinner("Loading AI...", frame)
                frame += 1
                time.sleep(0.15)
        
        anim_thread = threading.Thread(target=animate_loading, daemon=True)
        anim_thread.start()
        
        print("Loading AI Engine...")
        engine = TranslationEngine()
        
        loading = False
        time.sleep(0.3)
        
        hw.display_message("Ready!", "Press B2")
        hw.beep(1200, 0.2)
        time.sleep(1.5)
        
    except Exception as e:
        hw.display_message("AI Error", "Check logs")
        print(f"❌ Engine Error: {e}")
        time.sleep(5)
        hw.cleanup()
        return

    src_idx = 0
    tgt_idx = 1
    mode = 0

    last_result_native = None
    last_result_english = None
    last_tgt_code = None

    hw.beep(1000, 0.1)

    try:
        while True:
            src_code, src_name = LANGUAGES[src_idx]
            tgt_code, tgt_name = LANGUAGES[tgt_idx]
            
            # Mode 2: REPLAY SCREEN - PERFECT SIZING
            if mode == 2:
                hw.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
                
                # Top: Confidence (small font, 1 line)
                confidence = engine.get_last_confidence()
                hw.draw.text((2, 0), "Done", font=hw.font_small, fill=255)
                hw.draw.text((100, 0), f"{confidence}%", font=hw.font_small, fill=255)
                
                # Confidence bar (thin)
                bar_w = int((confidence / 100) * 94)
                hw.draw.rectangle((2, 8, 96, 10), outline=255, fill=0)
                if bar_w > 0:
                    hw.draw.line((3, 9, 3 + bar_w, 9), fill=255)
                
                hw.draw.line((0, 12, 128, 12), fill=255)
                
                # Translation text (3 lines, small font)
                if last_result_english:
                    words = str(last_result_english).split()
                    lines = []
                    line = ""
                    for word in words:
                        test = line + " " + word if line else word
                        if len(test) < 22:  # Fit more chars
                            line = test
                        else:
                            lines.append(line)
                            line = word
                    if line:
                        lines.append(line)
                    
                    y = 14
                    for l in lines[:3]:  # Only 3 lines
                        hw.draw.text((2, y), l, font=hw.font_small, fill=255)
                        y += 9
                
                hw.draw.line((0, 42, 128, 42), fill=255)
                
                # Performance (1 line, small)
                timings = engine.get_performance_summary()
                hw.draw.text((2, 44), f"Time:{timings['total']:.0f}s", font=hw.font_small, fill=255)
                hw.draw.text((60, 44), f"STT:{timings['stt']:.0f}s", font=hw.font_small, fill=255)
                
                hw.draw.line((0, 54, 128, 54), fill=255)
                
                # Buttons (1 line, small)
                hw.draw.text((2, 56), "B1:Play B2:New", font=hw.font_small, fill=255)
                
                hw.oled.image(hw.image)
                hw.oled.show()
                
                # Button checks
                if hw.btn1_pressed() and hw.btn2_pressed():
                    hw.beep(600, 0.3)
                    hw.display_message("Exiting...", "")
                    print("\n👋 Exit")
                    time.sleep(1)
                    
                    history = engine.get_history()
                    if history:
                        print(f"\n📚 History ({len(history)} translations):")
                        for i, entry in enumerate(history, 1):
                            print(f"  {i}. [{entry['confidence']}%] {entry['source'][:30]} → {entry['english'][:30]}")
                    break
                
                if hw.btn1_pressed():
                    hw.beep(800, 0.1)
                    print(f"🔁 Replaying...")
                    hw.display_message("Replaying...", "")
                    if last_result_native:
                        engine.speak(last_result_native, last_tgt_code)
                    hw.wait_release()
                    time.sleep(0.5)
                    continue
                
                if hw.btn2_pressed():
                    hw.beep(1000, 0.1)
                    print("📝 New translation")
                    hw.display_message("Resetting...", "")
                    time.sleep(0.5)
                    mode = 0
                    last_result_native = None
                    last_result_english = None
                    last_tgt_code = None
                    hw.wait_release()
                    continue
                
                time.sleep(0.05)
                continue
            
            # Mode 0/1: Language selection
            hw.display_selection(src_name, tgt_name, mode)

            if hw.btn1_pressed() and hw.btn2_pressed():
                hw.beep(600, 0.3)
                hw.display_message("Exiting...", "")
                print("\n👋 Exit")
                time.sleep(1)
                
                history = engine.get_history()
                if history:
                    print(f"\n📚 History ({len(history)} translations):")
                    for i, entry in enumerate(history, 1):
                        print(f"  {i}. [{entry['confidence']}%] {entry['source'][:30]} → {entry['english'][:30]}")
                break

            if hw.btn1_pressed():
                hw.beep(800, 0.05)
                if mode == 0:
                    src_idx = (src_idx + 1) % len(LANGUAGES)
                    print(f"Source: {LANGUAGES[src_idx][1]}")
                else:
                    tgt_idx = (tgt_idx + 1) % len(LANGUAGES)
                    print(f"Target: {LANGUAGES[tgt_idx][1]}")
                hw.wait_release()
                time.sleep(0.1)

            if hw.btn2_pressed():
                hw.beep(1000, 0.1)
                if mode == 0:
                    mode = 1
                    print("Select target")
                    hw.wait_release()
                    time.sleep(0.1)
                else:
                    # START TRANSLATION
                    print(f"\n🎯 {src_name} → {tgt_name}")
                    hw.display_message("Recording...", "Speak now")
                    
                    try:
                        audio = engine.record_audio(duration=5)
                        
                        if len(audio) < 8000:
                            hw.display_message("Error", "Too short")
                            hw.beep(400, 0.3)
                            print("   ❌ Audio too short")
                            time.sleep(2)
                            mode = 0
                            hw.wait_release()
                            continue
                        
                        # Transcription with animation
                        transcribing = True
                        def animate_transcribe():
                            f = 0
                            while transcribing:
                                hw.display_spinner(f"STT {src_name[:8]}", f)
                                f += 1
                                time.sleep(0.15)
                        
                        anim_thread = threading.Thread(target=animate_transcribe, daemon=True)
                        anim_thread.start()
                        
                        text = engine.transcribe(audio, src_code)
                        transcribing = False
                        time.sleep(0.2)
                        
                        confidence = engine.get_last_confidence()
                        
                        if not text:
                            hw.display_message("Error", "No speech")
                            hw.beep(400, 0.3)
                            print("   ❌ No speech")
                            time.sleep(2)
                            mode = 0
                            hw.wait_release()
                            continue
                        
                        # Low confidence warning
                        if confidence < 60:
                            print(f"   ⚠️  LOW CONFIDENCE: {confidence}%")
                            hw.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
                            hw.draw.text((10, 20), "Low Quality!", font=hw.font_small, fill=255)
                            hw.draw.text((5, 32), f"Conf: {confidence}%", font=hw.font_small, fill=255)
                            hw.oled.image(hw.image)
                            hw.oled.show()
                            hw.beep(600, 0.2)
                            time.sleep(2)
                        
                        # Show transcription
                        hw.display_text_scrolling("You said:", text, confidence)
                        time.sleep(2)
                        
                        # Translation with animation
                        translating = True
                        def animate_translate():
                            f = 0
                            while translating:
                                hw.display_spinner("Translating...", f)
                                f += 1
                                time.sleep(0.15)
                        
                        anim_thread = threading.Thread(target=animate_translate, daemon=True)
                        anim_thread.start()
                        
                        result_native, result_english = engine.translate_pivot(text, src_code, tgt_code)
                        translating = False
                        time.sleep(0.2)
                        
                        if not result_native or not result_english:
                            hw.display_message("Error", "Trans fail")
                            hw.beep(400, 0.3)
                            print("   ❌ Translation failed")
                            time.sleep(2)
                            mode = 0
                            hw.wait_release()
                            continue
                        
                        # Show translation
                        hw.display_text_scrolling("Translation:", result_english)
                        time.sleep(2)
                        
                        # Speaking
                        hw.display_message("Speaking...", tgt_name[:12])
                        engine.speak(result_native, tgt_code)
                        
                        last_result_native = result_native
                        last_result_english = result_english
                        last_tgt_code = tgt_code
                        
                        # Success summary
                        timings = engine.get_performance_summary()
                        
                        hw.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
                        hw.draw.text((35, 10), "Success!", font=hw.font_small, fill=255)
                        hw.draw.line((0, 20, 128, 20), fill=255)
                        hw.draw.text((2, 24), f"Total: {timings['total']:.1f}s", font=hw.font_small, fill=255)
                        hw.draw.text((2, 34), f"STT: {timings['stt']:.1f}s", font=hw.font_small, fill=255)
                        hw.draw.text((2, 44), f"MT: {timings['translate']:.1f}s", font=hw.font_small, fill=255)
                        hw.oled.image(hw.image)
                        hw.oled.show()
                        time.sleep(1.5)
                        
                        print(f"⏱️  Total:{timings['total']:.1f}s (STT:{timings['stt']:.1f}s | MT:{timings['translate']:.1f}s | TTS:{timings['tts']:.1f}s)")
                        print(f"🎯 Confidence: {confidence}%")
                        
                        mode = 2
                        hw.beep(1200, 0.15)
                        print(f"✅ Done! '{result_english}' | {confidence}%")
                        
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        hw.display_message("Error", "Check logs")
                        hw.beep(400, 0.5)
                        time.sleep(2)
                        mode = 0
                
                hw.wait_release()

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupt")
    except Exception as e:
        print(f"\n❌ Fatal: {e}")
        hw.display_message("Fatal Error", "")
        time.sleep(3)
    finally:
        print("Cleaning up...")
        try:
            hw.cleanup()
        except:
            pass
        print("✅ Goodbye!")

if __name__ == "__main__":
    main()
