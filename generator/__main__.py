import sys
import os
import generator
from generator.app import App
from generator.app_config import AppConfig

app_config = AppConfig()

app = App(app_config=app_config)
app.start_cli(sys.argv[1:])
