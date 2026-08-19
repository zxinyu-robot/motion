#!/usr/bin/env python3
"""本地翻译：选中即译，PDF / 文本通用。"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request


def _run(cmd: list[str]) -> str | None:
    try:
        out = subprocess.check_output(
            cmd,
            text=True,
            stderr=subprocess.DEVNULL,
            env=os.environ.copy(),
        )
        text = out.strip()
        return text or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def read_primary() -> str | None:
    return _run(["xclip", "-o", "-selection", "primary"])


def read_clipboard() -> str | None:
    for cmd in (
        ["xclip", "-o", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--output"],
        ["wl-paste"],
    ):
        text = _run(cmd)
        if text:
            return text
    return None


def auto_copy_selection() -> None:
    """xdotool 可用时模拟 Ctrl+C，把 PDF 选中内容写入剪贴板。"""
    if shutil.which("xdotool") is None:
        return
    _run(["xdotool", "key", "ctrl+c"])
    time.sleep(0.12)


def resolve_source(explicit: str | None = None, smart: bool = False) -> str:
    if explicit and explicit.strip():
        return explicit.strip()

    env_text = os.environ.get("TRANSLATE_TEXT", "").strip()
    if env_text:
        return env_text

    if smart:
        for reader in (read_primary, read_clipboard):
            text = reader()
            if text:
                return text
        auto_copy_selection()
        text = read_clipboard()
        if text:
            return text
        raise RuntimeError("未检测到选中文字。请先在 PDF/文本中拖选一段英文。")

    text = read_clipboard()
    if text:
        return text
    raise RuntimeError("剪贴板为空。请先选中文字，或安装 xclip：sudo apt install xclip")


def translate(text: str, target: str = "zh-CN") -> str:
    text = text.strip()
    if not text:
        raise ValueError("没有可翻译的文本")
    if len(text) > 4500:
        text = text[:4500]

    url = (
        "https://translate.googleapis.com/translate_a/single?"
        + urllib.parse.urlencode(
            {
                "client": "gtx",
                "sl": "auto",
                "tl": target,
                "dt": "t",
                "q": text,
            }
        )
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    parts = [chunk[0] for chunk in payload[0] if chunk and chunk[0]]
    result = "".join(parts).strip()
    if not result:
        raise RuntimeError("翻译结果为空")
    return result


def show_result(original: str, translated: str) -> None:
    preview = original.replace("\n", " ")
    if len(preview) > 160:
        preview = preview[:160] + "…"

    body = f"原文：{preview}\n\n译文：{translated}"
    print(body)

    try:
        subprocess.run(
            [
                "zenity",
                "--info",
                "--title=翻译",
                "--width=760",
                "--height=420",
                f"--text={body}",
            ],
            check=False,
            env=os.environ.copy(),
        )
    except FileNotFoundError:
        subprocess.run(
            ["notify-send", "翻译", translated[:240]],
            check=False,
            env=os.environ.copy(),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate selected or copied text")
    parser.add_argument("text", nargs="*", help="optional inline text")
    parser.add_argument("--smart", action="store_true", help="auto-detect selection")
    args = parser.parse_args()

    try:
        inline = " ".join(args.text).strip() if args.text else ""
        source = resolve_source(inline or None, smart=args.smart or not inline)
        translated = translate(source)
        show_result(source, translated)
        return 0
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        print(f"翻译失败: {msg}", file=sys.stderr)
        try:
            subprocess.run(
                ["zenity", "--error", "--title=翻译失败", f"--text={msg}"],
                check=False,
                env=os.environ.copy(),
            )
        except FileNotFoundError:
            subprocess.run(["notify-send", "翻译失败", msg], check=False, env=os.environ.copy())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
