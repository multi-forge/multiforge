#!/usr/bin/env python3
"""
ForgeOS Onboarding Kiosk Display Generator v1.3
Fixes text overlaps, auto-detects framebuffer resolution, and polishes typography.
Generates a 2-QR code setup kiosk screen:
1. Wi-Fi AP Auto-Connect (WIFI:S:ForgeOS-Setup-btve10;T:WPA;P:forgeos123;;)
2. Captive Portal Web URL (http://192.168.4.1)
"""
import os
import sys
import subprocess
from pathlib import Path

def get_fb_resolution():
    try:
        with open('/sys/class/graphics/fb0/virtual_size', 'r') as f:
            w, h = map(int, f.read().strip().split(','))
            if w > 0 and h > 0:
                return w, h
    except Exception:
        pass
    return 1920, 1080

def generate_display_image():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[FORGE-DISPLAY WARNING] Pillow PIL not installed.")
        return False

    W, H = get_fb_resolution()
    print(f"[FORGE-DISPLAY] Detected Framebuffer Resolution: {W}x{H}")

    run_cmd = lambda cmd: subprocess.run(cmd, shell=True, capture_output=True)
    
    wifi_qr_data = "WIFI:S:ForgeOS-Setup-btve10;T:WPA;P:forgeos123;;"
    url_qr_data = "http://192.168.4.1"

    # Generate QR PNG files
    run_cmd(f'qrencode -s 8 -o /tmp/qr_wifi.png "{wifi_qr_data}"')
    run_cmd(f'qrencode -s 8 -o /tmp/qr_url.png "{url_qr_data}"')

    if not Path('/tmp/qr_wifi.png').exists() or not Path('/tmp/qr_url.png').exists():
        print("[FORGE-DISPLAY ERROR] Failed to generate QR PNG files.")
        return False

    canvas = Image.new('RGB', (W, H), color='#0d1117')
    draw = ImageDraw.Draw(canvas)

    # Dynamic font scaling based on resolution
    scale = min(W / 1920.0, H / 1080.0)
    def s(val): return max(10, int(val * scale))

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s(44))
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s(26))
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s(20))
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s(22))
    except Exception:
        font_title = font_sub = font_body = font_bold = ImageFont.load_default()

    # Draw Header
    draw.text((W // 2, s(60)), "ForgeOS — Kiosk de Configuração Inicial", fill="#f0f6fc", font=font_title, anchor="mm")
    draw.text((W // 2, s(110)), "Dispositivo: BTV E10 Express (Amlogic S905X2) | Distro: ForgeOS v1.2", fill="#8b949e", font=font_body, anchor="mm")

    # Load & resize QR Images cleanly (300x300 for 1080p scale)
    qr_dim = s(300)
    img_wifi = Image.open('/tmp/qr_wifi.png').convert('RGB').resize((qr_dim, qr_dim), Image.Resampling.LANCZOS)
    img_url = Image.open('/tmp/qr_url.png').convert('RGB').resize((qr_dim, qr_dim), Image.Resampling.LANCZOS)

    # Card dimensions
    card_w = s(520)
    card_h = s(620)
    card_y = s(160)

    # Card 1: Wi-Fi Auto-Connect QR
    c1_x = (W // 2) - card_w - s(30)
    draw.rectangle([c1_x, card_y, c1_x + card_w, card_y + card_h], fill="#161b22", outline="#30363d", width=2)
    draw.text((c1_x + (card_w // 2), card_y + s(35)), "1. Conectar à Rede Wi-Fi", fill="#58a6ff", font=font_sub, anchor="mm")
    
    # Paste QR Code with exact offsets so text NEVER overlaps
    qr1_x = c1_x + ((card_w - qr_dim) // 2)
    qr1_y = card_y + s(75)
    canvas.paste(img_wifi, (qr1_x, qr1_y))

    # Text below QR 1
    t1_y = qr1_y + qr_dim + s(30)
    draw.text((c1_x + (card_w // 2), t1_y), "Rede: ForgeOS-Setup-btve10", fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((c1_x + (card_w // 2), t1_y + s(35)), "Senha: forgeos123", fill="#8b949e", font=font_body, anchor="mm")
    draw.text((c1_x + (card_w // 2), t1_y + s(80)), "Escaneie para Conectar Automaticamente", fill="#3fb950", font=font_body, anchor="mm")

    # Card 2: Captive Portal URL QR
    c2_x = (W // 2) + s(30)
    draw.rectangle([c2_x, card_y, c2_x + card_w, card_y + card_h], fill="#161b22", outline="#30363d", width=2)
    draw.text((c2_x + (card_w // 2), card_y + s(35)), "2. Abrir Portal de Setup", fill="#58a6ff", font=font_sub, anchor="mm")

    qr2_x = c2_x + ((card_w - qr_dim) // 2)
    qr2_y = card_y + s(75)
    canvas.paste(img_url, (qr2_x, qr2_y))

    t2_y = qr2_y + qr_dim + s(30)
    draw.text((c2_x + (card_w // 2), t2_y), "URL: http://192.168.4.1", fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((c2_x + (card_w // 2), t2_y + s(35)), "Portal de Configuração Web", fill="#8b949e", font=font_body, anchor="mm")
    draw.text((c2_x + (card_w // 2), t2_y + s(80)), "Escaneie para Abrir no Navegador", fill="#3fb950", font=font_body, anchor="mm")

    # Footer
    draw.text((W // 2, H - s(50)), "Aguardando configuração inicial via smartphone...", fill="#6e7681", font=font_body, anchor="mm")

    output_path = '/tmp/forge_setup_display.png'
    canvas.save(output_path)
    print(f"[FORGE-DISPLAY SUCCESS] Saved resolution-adapted setup screen ({W}x{H}) to {output_path}")
    return True

def render_to_framebuffer():
    if generate_display_image():
        print("[FORGE-DISPLAY] Outputting display image to framebuffer...")
        subprocess.run('fbi -d /dev/fb0 -T 1 --noverbose -a /tmp/forge_setup_display.png 2>/dev/null', shell=True)

if __name__ == '__main__':
    render_to_framebuffer()
