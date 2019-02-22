import os
import time
import webbrowser
import asyncio

async def main():
  await asyncio.sleep(3)
  webbrowser.open("http://127.0.0.1:5000")

os.system("cat app.py")
asyncio.run(main())

# This is on UNIX systems only
# If using something other than a UNIX-based system,
# Uncomment the next line and remove the last line
# os.system("flask run")
os.system("gunicorn -w 4 -b 127.0.0.1:5000 app:app")