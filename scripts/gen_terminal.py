#!/usr/bin/env python3
"""Render the README terminal GIF: a short boot line, then neofetch-style stats.

Config lives in config/ and must be copied to ~/.config/gifos before this runs;
gifos only reads its settings from that path. Needs GITHUB_TOKEN for the stats
query, ffmpeg for the encode.

    python3 scripts/gen_terminal.py

Writes terminal.gif to the working directory.
"""

import os
import sys

import gifos

USER = "syamxm"
IGNORE_REPOS = ["syamxm"]

WIDTH = 900
HEIGHT = 420
PADDING = 18

PURPLE = "\x1b[95m"
DIM = "\x1b[34m"
RESET = "\x1b[0m"

HOST_LINES = [
    ("host", "debian homeserver · cloudflare tunnel + tailscale"),
    ("shell", "fish"),
    ("editor", "neovim"),
    ("role", "final year cs (hons), uitm shah alam · devops intern"),
]


def labelled(label, value, width=9):
    return "%s%s%s  %s" % (PURPLE, label.ljust(width), RESET, value)


def stat_lines(stats):
    top_languages = ", ".join(name for name, _ in stats.languages_sorted[:5])
    return [
        labelled("repos", str(stats.total_repo_contributions)),
        labelled("commits", "%s all time · %s last year"
                 % (stats.total_commits_all_time, stats.total_commits_last_year)),
        labelled("pull reqs", "%s opened · %s merged"
                 % (stats.total_pull_requests_made, stats.total_pull_requests_merged)),
        labelled("stars", str(stats.total_stargazers)),
        labelled("rank", str(stats.user_rank.level)),
        labelled("langs", top_languages),
    ]


def render(terminal, lines):
    terminal.set_prompt("%ssyamxm@cachyos%s ~> " % (PURPLE, RESET))
    terminal.gen_prompt(1)
    terminal.gen_typing_text("neofetch", 1, contin=True)

    row = 3
    for label, value in HOST_LINES:
        terminal.gen_text(labelled(label, value), row)
        row += 1

    row += 1
    for line in lines:
        terminal.gen_text(line, row)
        row += 1

    row += 1
    terminal.gen_prompt(row)
    terminal.gen_typing_text("cat motd", row, contin=True)
    terminal.gen_text("%sinfrastructure that is defensible, not decorative.%s" % (DIM, RESET),
                      row + 2)
    terminal.gen_prompt(row + 4)


def main():
    if not os.getenv("GITHUB_TOKEN"):
        sys.exit("GITHUB_TOKEN is required for the stats query")

    stats = gifos.utils.fetch_github_stats(user_name=USER, ignore_repos=IGNORE_REPOS)
    terminal = gifos.Terminal(width=WIDTH, height=HEIGHT, xpad=PADDING, ypad=PADDING)
    render(terminal, stat_lines(stats))
    terminal.gen_gif()


if __name__ == "__main__":
    main()
