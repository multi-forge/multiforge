#!/usr/bin/env python3
"""
ForgeOS Agent & First Boot Provisioning Daemon
Implements Obsidian Blueprint Architecture goals for BTV E10 (Amlogic S905X2).
"""
import os
import sys
import time
import subprocess
import glob
from pathlib import Path

BOOT_FORGE_DIR = Path('/boot/forge')
NETWORK_YAML = BOOT_FORGE_DIR / 'network.yaml'
MINA_YAML = BOOT_FORGE_DIR / 'mina.yaml'

def get_hdmi_status():
    drm_paths = glob.glob('/sys/class/drm/*HDMI*/status')
    for path in drm_paths:
        try:
            with open(path, 'r') as f:
                status = f.read().strip()
                if status:
                    return status
        except Exception:
            pass
    return 'disconnected'

def run_cmd(cmd, check=False):
    print(f"[FORGE-AGENT] Executing: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

def start_captive_portal():
    print('[FORGE-AGENT] Starting Hotspot AP & Captive Portal Mode...')
    
    # 1. Generate hostapd config
    hostapd_conf = """interface=wlan0
driver=nl80211
ssid=ForgeOS-Setup-btve10
hw_mode=g
channel=6
auth_algs=1
wpa=2
wpa_passphrase=forgeos123
wpa_key_mgmt=WPA-PSK
"""
    with open('/tmp/hostapd.conf', 'w') as f:
        f.write(hostapd_conf)

    # 2. Generate dnsmasq config
    dnsmasq_conf = """interface=wlan0
dhcp-range=192.168.4.10,192.168.4.250,12h
address=/#/192.168.4.1
"""
    with open('/tmp/dnsmasq.conf', 'w') as f:
        f.write(dnsmasq_conf)

    # 3. Apply iptables NAT redirect for HTTP 80
    run_cmd(['iptables', '-t', 'nat', '-A', 'PREROUTING', '-i', 'wlan0', '-p', 'tcp', '--dport', '80', '-j', 'DNAT', '--to-destination', '192.168.4.1:80'])
    run_cmd(['iptables', '-A', 'FORWARD', '-i', 'wlan0', '-p', 'tcp', '--dport', '80', '-j', 'ACCEPT'])

    # Check HDMI status
    hdmi = get_hdmi_status()
    print(f'[FORGE-AGENT] HDMI Status: {hdmi}')
    if hdmi == 'disconnected':
        print('[FORGE-AGENT] Headless Mode (No HDMI). Rendering CLI QR pairing code on TTY1...')
        subprocess.run('qrencode -t UTF8 "http://192.168.4.1" > /dev/tty1', shell=True)
        subprocess.run('echo "\nSSID: ForgeOS-Setup-btve10 | Pass: forgeos123 | Setup: http://192.168.4.1" > /dev/tty1', shell=True)

    # Launch Captive Portal HTTP Server
    print('[FORGE-AGENT] Starting Captive Portal Web Server on port 80...')
    subprocess.run(['python3', '/opt/forgeos/captive-portal/server.py', '80'])

def apply_provisioning():
    print('[FORGE-AGENT] Checking provisioning files in /boot/forge/...')
    if NETWORK_YAML.exists() and MINA_YAML.exists():
        print('[FORGE-AGENT] Provisioning files found. Applying configurations...')
        # Parse network config
        ssid, passphrase = '', ''
        with open(NETWORK_YAML, 'r') as f:
            for line in f:
                if 'ssid:' in line:
                    ssid = line.split(':', 1)[1].strip().strip("'")
                elif 'passphrase:' in line:
                    passphrase = line.split(':', 1)[1].strip().strip("'")

        if ssid:
            print(f'[FORGE-AGENT] Connecting to Wi-Fi SSID: {ssid}...')
            run_cmd(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', passphrase])

        # Parse Mina config
        window_mode = '-g right'
        with open(MINA_YAML, 'r') as f:
            for line in f:
                if 'window_mode:' in line:
                    window_mode = line.split(':', 1)[1].strip().strip("'")

        print(f'[FORGE-AGENT] Launching Mina Assistant with window mode: {window_mode}...')
        mina_cmd = ['python3', '/root/Mina-a-Assistente-Virtual/main_cli.py'] + window_mode.split()
        subprocess.run(mina_cmd)
    else:
        print('[FORGE-AGENT] Provisioning files NOT found. Falling back to Captive Portal...')
        start_captive_portal()

if __name__ == '__main__':
    apply_provisioning()
