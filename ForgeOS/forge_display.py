#!/usr/bin/env python3
"""
ForgeOS Ultra-HD 4K Setup Kiosk Display Generator v1.4
Renders a 4K (3840x2160) master canvas with LiberationSans TTF typography
and high-density Lanczos anti-aliasing for pin-sharp display on TV Box monitors.
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

def get_ttf_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
    ]
    from PIL import ImageFont
    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def generate_display_image():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("[FORGE-DISPLAY WARNING] Pillow PIL not installed.")
        return False

    FB_W, FB_H = get_fb_resolution()
    print(f"[FORGE-DISPLAY] Active Framebuffer Resolution: {FB_W}x{FB_H}")

    # Master 4K Ultra HD Canvas (3840x2160) for maximum vector crispness
    W, H = 3840, 2160

    run_cmd = lambda cmd: subprocess.run(cmd, shell=True, capture_output=True)
    wifi_qr_data = "WIFI:S:ForgeOS-Setup-btve10;T:WPA;P:forgeos123;;"
    url_qr_data = "http://192.168.4.1"

    # Generate high-density QR PNGs
    run_cmd(f'qrencode -s 20 -o /tmp/qr_wifi.png "{wifi_qr_data}"')
    run_cmd(f'qrencode -s 20 -o /tmp/qr_url.png "{url_qr_data}"')

    if not Path('/tmp/qr_wifi.png').exists() or not Path('/tmp/qr_url.png').exists():
        print("[FORGE-DISPLAY ERROR] Failed to generate QR PNG files.")
        return False

    canvas = Image.new('RGB', (W, H), color='#0d1117')
    draw = ImageDraw.Draw(canvas)

    # 4K Fonts
    font_header = get_ttf_font(96, bold=True)
    font_sub = get_ttf_font(52, bold=False)
    font_card_title = get_ttf_font(58, bold=True)
    font_label_bold = get_ttf_font(46, bold=True)
    font_label_regular = get_ttf_font(40, bold=False)
    font_badge = get_ttf_font(44, bold=True)

    # Header
    draw.text((W // 2, 130), "ForgeOS — Kiosk de Configuração Inicial", fill="#f0f6fc", font=font_header, anchor="mm")
    draw.text((W // 2, 230), "Dispositivo: BTV E10 Express (Amlogic S905X2) | Distro: ForgeOS v1.2 Pro", fill="#8b949e", font=font_sub, anchor="mm")

    # Load & Resize 4K QR Images (600x600px each)
    qr_size = 620
    img_wifi = Image.open('/tmp/qr_wifi.png').convert('RGB').resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    img_url = Image.open('/tmp/qr_url.png').convert('RGB').resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Cards Geometry (2 large cards centered)
    card_w, card_h = 1080, 1320
    card_y = 350

    # Card 1: Wi-Fi AP QR
    c1_x = (W // 2) - card_w - 70
    draw.rounded_rectangle([c1_x, card_y, c1_x + card_w, card_y + card_h], radius=24, fill="#161b22", outline="#30363d", width=4)
    draw.text((c1_x + (card_w // 2), card_y + 80), "1. Conectar à Rede Wi-Fi", fill="#58a6ff", font=font_card_title, anchor="mm")

    qr1_x = c1_x + ((card_w - qr_size) // 2)
    qr1_y = card_y + 170
    canvas.paste(img_wifi, (qr1_x, qr1_y))

    t1_y = qr1_y + qr_size + 60
    draw.text((c1_x + (card_w // 2), t1_y), "Rede: ForgeOS-Setup-btve10", fill="#f0f6fc", font=font_label_bold, anchor="mm")
    draw.text((c1_x + (card_w // 2), t1_y + 70), "Senha: forgeos123", fill="#8b949e", font=font_label_regular, anchor="mm")
    draw.text((c1_x + (card_w // 2), t1_y + 160), "Escaneie para Conectar Automaticamente", fill="#3fb950", font=font_badge, anchor="mm")

    # Card 2: Captive Portal URL QR
    c2_x = (W // 2) + 70
    draw.rounded_rectangle([c2_x, card_y, c2_x + card_w, card_y + card_h], radius=24, fill="#161b22", outline="#30363d", width=4)
    draw.text((c2_x + (card_w // 2), card_y + 80), "2. Abrir Portal de Setup", fill="#58a6ff", font=font_card_title, anchor="mm")

    qr2_x = c2_x + ((card_w - qr_size) // 2)
    qr2_y = card_y + 170
    canvas.paste(img_url, (qr2_x, qr2_y))

    t2_y = qr2_y + qr_size + 60
    draw.text((c2_x + (card_w // 2), t2_y), "URL: http://192.168.4.1", fill="#f0f6fc", font=font_label_bold, anchor="mm")
    draw.text((c2_x + (card_w // 2), t2_y + 70), "Portal de Configuração Web", fill="#8b949e", font=font_label_regular, anchor="mm")
    draw.text((c2_x + (card_w // 2), t2_y + 160), "Escaneie para Abrir no Navegador", fill="#3fb950", font=font_badge, anchor="mm")

    # Footer
    draw.text((W // 2, H - 100), "Aguardando configuração inicial via smartphone ou PC...", fill="#6e7681", font=font_sub, anchor="mm")

    # Downsample from 4K to active Framebuffer resolution (FB_W x FB_H) with Lanczos anti-aliasing
    final_img = canvas.resize((FB_W, FB_H), Image.Resampling.LANCZOS)

    output_path = '/tmp/forge_setup_display.png'
    final_img.save(output_path, quality=100)
    print(f"[FORGE-DISPLAY SUCCESS] Rendered 4K supersampled image downscaled to {FB_W}x{FB_H} -> {output_path}")
    return True

def render_to_framebuffer():
    if generate_display_image():
        print("[FORGE-DISPLAY] Outputting crisp 4K anti-aliased image to framebuffer...")
        subprocess.run('fbi -d /dev/fb0 -T 1 --noverbose -a /tmp/forge_setup_display.png 2>/dev/null', shell=True)

if __name__ == '__main__':
    render_to_framebuffer()
