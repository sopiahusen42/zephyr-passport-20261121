import os, shutil, sys


def fail(msg):
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out, exist_ok=True)
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
if not os.path.isfile(src):
    fail("entry.png not found at %s" % src)
with open(src, "rb") as f:
    data = f.read()
if data[:8] != b"\x89PNG\r\n\x1a\n":
    fail("entry.png is not a valid PNG (bad magic bytes)")
if len(data) > 1048576:
    fail("entry.png too large: %d bytes (max 1048576)" % len(data))
shutil.copyfile(src, os.path.join(out, "entry.png"))
