#!/usr/bin/env python3

import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import json
import uinput
import time

_CHAR_MAP = {
    "a":  uinput.KEY_A,
    "b":  uinput.KEY_B,
    "c":  uinput.KEY_C,
    "d":  uinput.KEY_D,
    "e":  uinput.KEY_E,
    "f":  uinput.KEY_F,
    "g":  uinput.KEY_G,
    "h":  uinput.KEY_H,
    "i":  uinput.KEY_I,
    "j":  uinput.KEY_J,
    "k":  uinput.KEY_K,
    "l":  uinput.KEY_L,
    "m":  uinput.KEY_M,
    "n":  uinput.KEY_N,
    "o":  uinput.KEY_O,
    "p":  uinput.KEY_P,
    "q":  uinput.KEY_Q,
    "r":  uinput.KEY_R,
    "s":  uinput.KEY_S,
    "t":  uinput.KEY_T,
    "u":  uinput.KEY_U,
    "v":  uinput.KEY_V,
    "w":  uinput.KEY_W,
    "x":  uinput.KEY_X,
    "y":  uinput.KEY_Y,
    "z":  uinput.KEY_Z,
    "1":  uinput.KEY_1,
    "2":  uinput.KEY_2,
    "3":  uinput.KEY_3,
    "4":  uinput.KEY_4,
    "5":  uinput.KEY_5,
    "6":  uinput.KEY_6,
    "7":  uinput.KEY_7,
    "8":  uinput.KEY_8,
    "9":  uinput.KEY_9,
    "0":  uinput.KEY_0,
    "\t": uinput.KEY_TAB,
    "\n": uinput.KEY_ENTER,
    " ":  uinput.KEY_SPACE,
    ".":  uinput.KEY_DOT,
    ",":  uinput.KEY_COMMA,
    "/":  uinput.KEY_SLASH,
    "\\": uinput.KEY_BACKSLASH,
    "[": uinput.KEY_LEFTBRACE,
    "]": uinput.KEY_RIGHTBRACE,
    ";": uinput.KEY_SEMICOLON,
    "'": uinput.KEY_APOSTROPHE,
    "-": uinput.KEY_KPMINUS,
    "`": uinput.KEY_GRAVE,
}

en_layout = 'qwertyuiop[]asdfghjkl;\'zxcvbnm,./`'
ru_layout = 'йцукенгшщзхъфывапролджэячсмитьбю.ё'

for i in range(len(en_layout)):
	_CHAR_MAP[ru_layout[i]] = _CHAR_MAP[en_layout[i]]

event_map = []

for char in _CHAR_MAP:
	event_map.append(_CHAR_MAP[char])

event_map.append(uinput.KEY_BACKSPACE)
#event_map.append(uinput.KEY_LEFTCTRL)

input_device = uinput.Device(event_map)
time.sleep(1)


def _chars_to_events(chars):
    events = []
    for char in chars:
        events.append(_CHAR_MAP.get(char))
    return events

def uinput_print(chars):
	events = _chars_to_events(chars)

	for event in events:
		if event:
			#input_device.emit(uinput.KEY_LEFTCTRL, 0)
			input_device.emit_click(event)


q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-m', '--model', type=str, metavar='MODEL_PATH',
    help='Path to the model')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

result_prev = ''

try:
    if args.model is None:
        args.model = "model"
    if not os.path.exists(args.model):
        print ("Please download a model for your language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(args.model)	


    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                            channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            while True:
                data = q.get()
                
                result = ''
                final = False
                
                if rec.AcceptWaveform(data):
                    result = ' ' + json.loads(rec.Result())["text"]
                    final = True
                    if result_prev == '' and result != ' ':
                        uinput_print(result)
                        result_prev == ''
                else:
                    result = ' ' + json.loads(rec.PartialResult())["partial"]
                
                if result != '' and result != ' ' and result != result_prev:
                    #print(result[0:len(result_prev)], result_prev)
                    
                    if result[0:len(result_prev)] == result_prev:
                        #print(result_prev, result)
                        uinput_print(result[len(result_prev):])
                        
                        result_prev = result
                    else:
                        output = ''
                        state = 0
                        symbol_start = 0
                        # найти когда начинаются изменения в фразе
                        for i in range(min(len(result), len(result_prev))):
                        	if result[i] != result_prev[i]:
                        	    symbol_start = i
                        	    break
                        # если изменений не нашлось то скорее всего фраза стала короче
                        if symbol_start == 0:
                            symbol_start = len(result)
                        for i in range(max(0, len(result_prev) - symbol_start)):
                            input_device.emit_click(uinput.KEY_BACKSPACE)
                        
                        uinput_print(result[symbol_start:])
                        print(result + ', ' + result_prev, symbol_start)
                        
                        result_prev = result
                if final:
                    result_prev = ''
                
                	

except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
