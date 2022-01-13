
import argparse
from pathlib import Path
from http.client import responses as RESPONSE_CODES
import re
import time

import pyttsx3
import requests
from bs4 import BeautifulSoup

URL_TOC = "https://katalepsis.net/table-of-contents/"
CHAPTER_PATTERN = re.compile(r"[0-9]+.[0-9]+")

def check_status_code(r):
   if r.status_code != 200:
      msg = (
         f"Received unexpected status code {r.status_code} "
         f"({RESPONSE_CODES[r.status_code]}) looking for `{r.url}`"
      )
      raise RuntimeError(msg)

def grab_toc():
   r = requests.get(URL_TOC)
   check_status_code(r)

   soup = BeautifulSoup(r.content, "html.parser")

   anchors = soup.find_all("a")

   toc = {}
   for a in anchors:
      if CHAPTER_PATTERN.search(a.text):
         toc[a.text] = a["href"]

   return toc

def grab_chapter(toc, chapter):
   try:
      url = toc[chapter]
   except KeyError:
      last = toc.keys()[-1]
      msg = (
         f"Could not find chapter {chapter!r}. The latest chapter I could "
         f"find on the site was {last!r}."
      )

   r = requests.get(url)
   check_status_code(r)

   soup = BeautifulSoup(r.content, "html.parser")

   content = soup.find("div", "entry-content").find_all("p")[1]
   txt = content.get_text(separator="\n\n")
   return txt

def replace_smart_quotes(txt):
   txt = txt.replace("“", "\"")
   txt = txt.replace("”", "\"")
   txt = txt.replace("‘", "'")
   txt = txt.replace("’", "'")
   return txt

def replace_em_dashes(txt):
   txt = txt.replace("—", "-")
   return txt

def replace_ellipses(txt):
   txt = txt.replace("…", "...")
   return txt

def check_chapter(arg):
   if not CHAPTER_PATTERN.search(arg):
      msg = (
         "Chapter argument must have the form containing the arc & chapter, "
         "e.g. '1.1', for Arc 1 Chapter 1"
      )
      raise argparse.ArgumentTypeError(msg)

   return arg

def parser():
   gist = "Convert Katalepsis chapters to audio files."
   parser = argparse.ArgumentParser(description=gist)
   
   parser.add_argument("chapter", metavar="CHAPTER", type=check_chapter,
      help="chapter (arc.chapter)")
   parser.add_argument("outfile", metavar="OUT", type=Path, nargs="?",
      help="output audio file name")
   parser.add_argument("-v", "--verbose", action="count", default=0)

   return parser

def main():
   args = parser().parse_args()
   verbosity = args.verbose

   def notepad(v, *args, **kwargs):
      if verbosity >= v:
         print(*args, **kwargs)

   if args.outfile is None:
      stem = args.chapter.replace(".", "-")
      args.outfile = Path(f"./{stem}.mp3")

   notepad(1, "Fetching TOC...")
   toc = grab_toc()
   if verbosity >= 2:
      print(f"Found {len(toc)} chapters:")
      for chapter in toc.keys():
         print("*", chapter)

   notepad(1, "Fetching text...")
   txt = grab_chapter(toc, args.chapter)

   for preprocess in (
      replace_smart_quotes,
      replace_em_dashes,
      replace_ellipses,
   ):
      txt = preprocess(txt)
   notepad(3, txt)

   notepad(1, "Converting to speech...")
   engine = pyttsx3.init()

   voices = engine.getProperty("voices")
   engine.setProperty("voice", voices[1].id)
   #engine.setProperty("rate", 125)

   engine.save_to_file(txt, args.outfile.as_posix())
   engine.runAndWait()
   notepad(1, "Done!")

   notepad(2, f"File saved to: `{args.outfile}`")

if __name__ == "__main__":
   main()
