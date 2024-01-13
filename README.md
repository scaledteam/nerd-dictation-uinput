# nerd-dictation-uinput
Simple speech to text using Vosk and Uinput with russian language support.

## Usage
1. Download language model from [Vosk website](https://alphacephei.com/vosk/models). Unpack it and rename model folder into just "model".

2. Activate uinput module. It can be done in multiple ways (modprobe, useadd, etc.) but you can activate it without root using "keyboard-events.c" program. It's self-comiling code, just run it and it will compile and run by itself.
```
./keyboard-events.c
```

3. Then install python requirements
```
pip install -r requirements.txt
```

4. And run program
```
./nerd-dictation.py
```

## Difference comparing to original nerd-dictation
[Original nerd-dictation program](https://github.com/ideasman42/nerd-dictation) is great for english language, but extremely laggy for russian. At least for the time of creating this program (year 2023).
