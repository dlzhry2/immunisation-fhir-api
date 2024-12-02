import os
import sys

maindir = os.path.dirname(__file__)
srcdir = "../src"
sys.path.insert(0, os.path.abspath(os.path.join(maindir, srcdir)))
