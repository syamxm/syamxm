#!/usr/bin/env python3
"""Render the README terminal GIF: BIOS post, boot, login, then a fastfetch panel.

Config lives in config/ and must be copied to ~/.config/gifos before this runs;
gifos only reads its settings from that path. Needs GITHUB_TOKEN for the stats
query, ffmpeg for the encode.

    python3 scripts/gen_terminal.py

Writes terminal.gif to the working directory.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

import gifos

USER = "syamxm"
IGNORE_REPOS = ["syamxm"]
TIMEZONE = timezone(timedelta(hours=8))

WIDTH = 1000
HEIGHT = 500
PADDING = 15

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDMARK_SOURCE = os.path.join(REPO_ROOT, "assets", "syamxm.txt")

PURPLE = "\x1b[95m"
DEEP = "\x1b[94m"
INK = "\x1b[97m"
DIM = "\x1b[34m"
BANNER = "\x1b[30;105m"
RESET = "\x1b[0m"

DETAILS_COLUMN = 58

PROMPT = "%ssyamxm@cachyos%s ~> " % (PURPLE, RESET)

MEMORY_TOTAL = 65536
MEMORY_STEP = 7168
HOLD_SHORT = 5
HOLD_LONG = 150


def ascii_wordmark(scale=1):
    """The wordmark, flattened to ASCII.

    gohufont-uni-14.pil is a latin-1 bitmap font, so the U+2550-U+2588 box and
    block glyphs the art is drawn with raise UnicodeEncodeError. Only the solid
    blocks become '#'; the box-drawing characters are the shadow bevel, and
    filling those too turns the letterforms into an unreadable slab.
    """
    with open(WORDMARK_SOURCE, encoding="utf-8") as handle:
        lines = handle.read().rstrip("\n").split("\n")

    scaled = []
    for line in lines:
        row = "".join(("#" if char == "\u2588" else " ") * scale for char in line)
        scaled.extend([row] * scale)
    return scaled


def post_screen(terminal, year):
    terminal.gen_text("", 1, count=20)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("SYAMXM Modular BIOS v2.6.0", 1)
    terminal.gen_text("Copyright (C) %s, %sAhmad Syamim%s" % (year, PURPLE, RESET), 2)
    terminal.gen_text("%sGitHub Profile Terminal, Rev 0926%s" % (DEEP, RESET), 4)
    terminal.gen_text("CachyOS GIFCPU - 250Hz", 6)
    terminal.gen_text(
        "Press %sDEL%s to enter SETUP, %sESC%s to cancel Memory Test"
        % (DEEP, RESET, DEEP, RESET),
        terminal.num_rows,
    )

    for used in range(0, MEMORY_TOTAL + MEMORY_STEP, MEMORY_STEP):
        terminal.delete_row(8)
        count = 2 if used < MEMORY_TOTAL // 2 else 1
        terminal.gen_text("Memory Test: %d" % used, 8, count=count, contin=True)

    terminal.delete_row(8)
    terminal.gen_text("Memory Test: 64KB OK", 8, count=10, contin=True)
    terminal.gen_text("", 10, count=10, contin=True)


def boot_screen(terminal):
    terminal.clear_frame()
    terminal.gen_text("Initiating Boot Sequence ", 1, contin=True)
    terminal.gen_typing_text(".....", 1, contin=True)

    logo = ascii_wordmark(2)
    top_row = (terminal.num_rows - len(logo)) // 2
    left_col = (terminal.num_cols - len(logo[0])) // 2 + 1
    for offset, line in enumerate(logo):
        terminal.gen_text("%s%s%s" % (PURPLE, line, RESET), top_row + offset, left_col)

    tagline = "devsecops"
    tagline_col = (terminal.num_cols - len(tagline)) // 2 + 1
    tagline_row = top_row + len(logo) + 2
    for line in gifos.effects.text_scramble_effect_lines(tagline, 3, include_special=False):
        terminal.delete_row(tagline_row)
        terminal.gen_text("%s%s%s" % (DEEP, line, RESET), tagline_row, tagline_col)

    terminal.gen_text("", tagline_row, count=HOLD_SHORT * 3)


def login_screen(terminal, stamp):
    terminal.clear_frame()
    terminal.set_prompt(PROMPT)
    terminal.clone_frame(HOLD_SHORT)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("%sCachyOS 6.17 (tty1)%s" % (DEEP, RESET), 1, count=HOLD_SHORT)
    terminal.gen_text("login: ", 3, count=HOLD_SHORT)
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text(USER, 3, contin=True)
    terminal.gen_text("", 4, count=HOLD_SHORT)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("password: ", 4, count=HOLD_SHORT)
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text("**************", 4, contin=True)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("Last login: %s on tty1" % stamp, 6, count=HOLD_SHORT)


def fetch_panel(terminal, stats, year):
    logo = ascii_wordmark()
    top_languages = ", ".join(name for name, _ in stats.languages_sorted[:5])

    def field(label, value):
        return "%s%s%s%s%s" % (DEEP, label.ljust(17), INK, value, RESET)

    details = [
        "%s syamxm@GitHub %s" % (BANNER, RESET),
        "--------------",
        field("OS:", "CachyOS, Debian homeserver"),
        field("Host:", "UiTM Shah Alam"),
        field("Kernel:", "Computer Science (Hons), final year"),
        field("Role:", "DevOps intern, 7 Sep 2026 - 5 Mar 2027"),
        field("Shell:", "fish"),
        field("Editor:", "neovim"),
        field("Network:", "Cloudflare Tunnel + Tailscale, no open ports"),
        "",
        "%s GitHub Stats %s" % (BANNER, RESET),
        "--------------",
        field("Rank:", stats.user_rank.level),
        field("Stars:", stats.total_stargazers),
        field("Commits (%s):" % year, stats.total_commits_last_year),
        field("Pull Requests:", "%s merged of %s"
              % (stats.total_pull_requests_merged, stats.total_pull_requests_made)),
        field("Contributions:", stats.total_repo_contributions),
        field("Top Languages:", top_languages),
    ]

    terminal.clear_frame()
    terminal.set_prompt(PROMPT)
    terminal.gen_prompt(1)
    prompt_col = terminal.curr_col
    terminal.clone_frame(HOLD_SHORT * 2)
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text("\x1b[91mfastfetc", 1, contin=True)
    terminal.delete_row(1, prompt_col)
    terminal.gen_text("%sfastfetch%s" % (DEEP, RESET), 1, contin=True)
    terminal.gen_typing_text(" --config syamxm", 1, contin=True)

    terminal.toggle_show_cursor(False)
    for offset in range(max(len(logo), len(details))):
        art = logo[offset] if offset < len(logo) else ""
        info = details[offset] if offset < len(details) else ""
        terminal.gen_text(
            "%s%s%s%s" % (PURPLE, art.ljust(DETAILS_COLUMN - 1), RESET, info), 3 + offset
        )

    terminal.gen_text("", 3 + max(len(logo), len(details)), count=HOLD_SHORT)

    terminal.toggle_show_cursor(True)
    terminal.gen_prompt(terminal.curr_row + 1)
    terminal.gen_typing_text(
        "%s# infrastructure that is defensible, not decorative.%s" % (DIM, RESET),
        terminal.curr_row,
        contin=True,
    )
    terminal.gen_text("", terminal.curr_row, count=HOLD_LONG, contin=True)


def main():
    if not os.getenv("GITHUB_TOKEN"):
        sys.exit("GITHUB_TOKEN is required for the stats query")

    now = datetime.now(TIMEZONE)
    year = now.strftime("%Y")
    stamp = now.strftime("%a %b %d %I:%M:%S %p %Z %Y")

    stats = gifos.utils.fetch_github_stats(user_name=USER, ignore_repos=IGNORE_REPOS)

    terminal = gifos.Terminal(WIDTH, HEIGHT, PADDING, PADDING)
    post_screen(terminal, year)
    boot_screen(terminal)
    login_screen(terminal, stamp)
    fetch_panel(terminal, stats, year)
    terminal.gen_gif()


if __name__ == "__main__":
    main()
