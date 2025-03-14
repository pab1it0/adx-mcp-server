#!/usr/bin/env python

import os
import sys
import pytest
from pathlib import Path

# Add the source directory to the path so we can import the modules
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(src_dir / "adx_mcp_server"))

# Import server module for direct access
import adx_mcp_server.server

