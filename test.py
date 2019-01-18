import os
import time
import webbrowser
import asyncio

async def main():
  await asyncio.sleep(2)
  webbrowser.open("http://127.0.0.1:5000")

os.system("cat app.py")
time.sleep(2)
asyncio.run(main())
os.system("gunicorn -w 4 -b 127.0.0.1:5000 app:app")