#!/usr/bin/env python3
"""iSpeak v2.0 - PHASE 3: UX Polish (Optimized for 1.3" OLED 128x64)"""

import RPi.GPIO as GPIO
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
from adafruit_ssd1306 import SSD1306_I2C
import time

class Hardware:
    def __init__(self, button1_pin=23, button2_pin=24):
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.button1_pin = button1_pin
        self.button2_pin = button2_pin
        GPIO.setup(self.button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # I2C and OLED Setup
        i2c = busio.I2C(SCL, SDA)
        self.oled = SSD1306_I2C(128, 64, i2c)
        self.oled.fill(0)
        self.oled.show()

        # Create image buffer
        self.image = Image.new("1", (128, 64))
        self.draw = ImageDraw.Draw(self.image)

        # Load fonts
        try:
            self.font_regular = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
            self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            self.font_regular = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_large = ImageFont.load_default()

        # PHASE 3: Animation state
        self.scroll_offset = 0
        self.animation_frame = 0

    def btn1_pressed(self):
        return GPIO.input(self.button1_pin) == GPIO.LOW

    def btn2_pressed(self):
        return GPIO.input(self.button2_pin) == GPIO.LOW

    def wait_release(self):
        while self.btn1_pressed() or self.btn2_pressed():
            time.sleep(0.05)

    def beep(self, freq, duration):
        """Simple beep (add buzzer code if needed)"""
        pass

    def show_logo(self):
        """PHASE 3: Animated startup logo (sized for 1.3" OLED)"""
        self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
        
        # Simple animation - 2 frames only
        for i in range(2):
            self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
            
            # Border
            if i >= 0:
                self.draw.rectangle((10, 10, 118, 54), outline=255, fill=0)
            
            # Text
            if i >= 1:
                self.draw.text((35, 22), "iSpeak", font=self.font_large, fill=255)
                self.draw.text((42, 38), "v2.0", font=self.font_small, fill=255)
            
            self.oled.image(self.image)
            self.oled.show()
            time.sleep(0.3)

    def display_selection(self, src_lang, tgt_lang, mode):
        """Display language selection (optimized for 1.3" OLED)"""
        self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
        
        # Title - smaller
        self.draw.text((5, 1), "iSpeak v2", font=self.font_small, fill=255)
        self.draw.line((0, 10, 128, 10), fill=255)
        
        # Source language (highlighted if mode=0)
        if mode == 0:
            self.draw.rectangle((1, 13, 127, 28), outline=255, fill=255)
            self.draw.text((3, 16), f"From: {src_lang[:12]}", font=self.font_small, fill=0)
        else:
            self.draw.text((3, 16), f"From: {src_lang[:12]}", font=self.font_small, fill=255)
        
        # Arrow - centered
        self.draw.text((60, 30), "v", font=self.font_small, fill=255)
        
        # Target language (highlighted if mode=1)
        if mode == 1:
            self.draw.rectangle((1, 35, 127, 50), outline=255, fill=255)
            self.draw.text((3, 38), f"To: {tgt_lang[:12]}", font=self.font_small, fill=0)
        else:
            self.draw.text((3, 38), f"To: {tgt_lang[:12]}", font=self.font_small, fill=255)
        
        # Instructions - bottom
        self.draw.line((0, 52, 128, 52), fill=255)
        if mode == 0:
            self.draw.text((2, 54), "B1:Chg B2:Next", font=self.font_small, fill=255)
        else:
            self.draw.text((2, 54), "B1:Chg B2:Go", font=self.font_small, fill=255)
        
        self.oled.image(self.image)
        self.oled.show()

    def display_message(self, line1, line2=""):
        """Simple two-line message (centered)"""
        self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
        
        # Center text better
        l1 = str(line1)[:18]
        l2 = str(line2)[:18]
        
        if line2:
            self.draw.text((3, 22), l1, font=self.font_small, fill=255)
            self.draw.text((3, 35), l2, font=self.font_small, fill=255)
        else:
            self.draw.text((3, 28), l1, font=self.font_small, fill=255)
        
        self.oled.image(self.image)
        self.oled.show()

    def display_progress(self, message, percent):
        """PHASE 3: Animated progress bar (compact)"""
        self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
        
        # Message - smaller, centered
        msg = str(message)[:18]
        self.draw.text((3, 15), msg, font=self.font_small, fill=255)
        
        # Progress bar background - smaller
        self.draw.rectangle((10, 30, 118, 40), outline=255, fill=0)
        
        # Progress bar fill
        bar_width = int((percent / 100) * 106)
        if bar_width > 0:
            self.draw.rectangle((11, 31, 11 + bar_width, 39), outline=255, fill=255)
        
        # Percentage text
        self.draw.text((55, 44), f"{percent}%", font=self.font_small, fill=255)
        
        self.oled.image(self.image)
        self.oled.show()

    def display_spinner(self, message, frame=0):
        """PHASE 3: Animated spinner (compact)"""
        self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
        
        # Message - truncated
        msg = str(message)[:18]
        self.draw.text((3, 20), msg, font=self.font_small, fill=255)
        
        # Spinner animation - smaller
        spinner_chars = ["|", "/", "-", "\\"]
        spinner = spinner_chars[frame % 4]
        self.draw.text((60, 35), spinner, font=self.font_regular, fill=255)
        
        self.oled.image(self.image)
        self.oled.show()

    def display_text_scrolling(self, title, text, confidence=None):
        """PHASE 3: Scrolling text (optimized layout)"""
        self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
        
        # Title with confidence - compact
        if confidence is not None:
            self.draw.text((2, 1), title[:12], font=self.font_small, fill=255)
            self.draw.text((95, 1), f"{confidence}%", font=self.font_small, fill=255)
            
            # Mini confidence bar
            bar_w = int((confidence / 100) * 90)
            self.draw.rectangle((2, 9, 92, 11), outline=255, fill=0)
            if bar_w > 0:
                self.draw.line((3, 10, 3 + bar_w, 10), fill=255)
        else:
            self.draw.text((2, 1), title[:18], font=self.font_small, fill=255)
        
        self.draw.line((0, 13, 128, 13), fill=255)
        
        # Word wrap - tighter
        words = str(text).split()
        lines = []
        line = ""
        for word in words:
            test = line + " " + word if line else word
            if len(test) < 21:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        
        # Display lines (up to 5 now)
        y = 16
        for l in lines[:5]:
            self.draw.text((2, y), l, font=self.font_small, fill=255)
            y += 9
        
        # Scroll indicator
        if len(lines) > 5:
            self.draw.text((120, 56), "v", font=self.font_small, fill=255)
        
        self.oled.image(self.image)
        self.oled.show()

    def display_text_indic(self, title, text):
        """Display Indic text (simplified for now)"""
        self.display_text_scrolling(title, text)

    def display_recording_animation(self, duration=5):
        """PHASE 3: Animated recording indicator"""
        start_time = time.time()
        frame = 0
        
        while time.time() - start_time < duration:
            self.draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
            
            # Recording text with blinking dot
            dots = "." * ((frame % 3) + 1)
            self.draw.text((20, 15), f"Recording{dots}", font=self.font_small, fill=255)
            
            # Waveform animation - smaller
            for i in range(0, 128, 8):
                height = abs((frame + i) % 15 - 7)
                self.draw.line((i, 35, i, 35 + height), fill=255)
            
            # Time indicator
            elapsed = int(time.time() - start_time)
            self.draw.text((50, 50), f"{elapsed}s", font=self.font_small, fill=255)
            
            self.oled.image(self.image)
            self.oled.show()
            
            frame += 1
            time.sleep(0.1)

    def cleanup(self):
        """Cleanup GPIO and OLED"""
        GPIO.cleanup()
        self.oled.fill(0)
        self.oled.show()
