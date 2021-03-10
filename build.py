#!/usr/bin/env python3

import os, sys

sources = [
    "IC22.oph",
    "IC23.oph",
    "IC24-SK1.oph",
    "IC24-SK2.oph"
    ]

if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <output directory>\n" % sys.argv[0])
        sys.exit(1)

    dest_dir = sys.argv[1]

    for source_file in sources:

        rom_file = os.path.join(dest_dir, source_file.replace(".oph", ".rom"))
        os.system("ophis -o " + rom_file + " " + source_file)
