#!/usr/bin/env python3
from ..src.database_wrapper import NimbusMySQLAlchemy

db = NimbusMySQLAlchemy(config_file="config.json")
db._create_all_tables()
