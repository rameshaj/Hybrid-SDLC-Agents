# Hardware Configuration and Environment Versions

Date captured: 2026-03-14

## Hardware Configuration
- RAM: 8 GB (user provided)
- CPU: Dual-core processor (user provided)
- OS family: macOS

## OS Version (detected)
- ProductName: macOS
- ProductVersion: 15.7.3
- BuildVersion: 24G419

## Python Versions (detected)
- `python3 --version`: Python 3.9.6
- `python --version`: Python 3.11.7

## Llama CLI Version (detected)
- `which llama-completion`: `/usr/local/bin/llama-completion`
- `which llama-cli`: `/usr/local/bin/llama-cli`
- `llama-completion --version`: `version: 7650 (68b4d516c)`; built with AppleClang 16.0.0.16000026 for Darwin x86_64
- `llama-cli --version`: `version: 7650 (68b4d516c)`; built with AppleClang 16.0.0.16000026 for Darwin x86_64

## Notes
- Direct hardware probing via `sysctl` was blocked in the current sandbox environment, so RAM/CPU are recorded from user-provided configuration.
