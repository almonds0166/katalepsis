
# Katalepsis TTS

I opened the first chapter of [Katalepsis](https://katalepsis.net/), and huh, that's a lot of text. Yeah, sure, I used to read thousands of pages a week as an optimistic kid, yet now, as an exhausted adult, I'm basically illiterate.

This project takes in the chapter and creates a text-to-speech (TTS) MP3 file.

I recommend the Katalepsis web serial plus this Python project; the TTS is nice to follow along with or merely to listen to with one's lifeless body resting prone in bed and face caressed in their pillow.

Usage:

```bash
# convert the first chapter to speech
# saves to 1-1.mp3 by default
python tts.py 1.1
````

See ``python tts.py --help`` for a few extra features

Requirements (`pip install`):

- `requests`
- `beautifulsoup4`
- `pyttsx3`