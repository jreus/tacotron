# -*- coding: utf-8 -*-
"""
Stand-alone script runs a tacotron model and allows real-time requests to be
made via an OpenSoundControl to a synthesizer instance.
"""

from scrapy import signals
import argparse
from trainer.hparams import hparams, hparams_debug_string
import os
import sys
from util import infolog
from synthesizer import Synthesizer
from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

log = infolog.log

synthesizer = Synthesizer()
osc_send_ip = "127.0.0.1"
osc_send_port = 57120
osc_root = "/taco/modelname"
model_id = None
wavfile_count = 0
wav_write_path = "wordless_tmp"
connected = False
client = None
server = None

# See: https://python-osc.readthedocs.io/en/latest/
# See: https://github.com/attwad/python-osc


# OSC handler callbacks
def sendMsg(*args):
    if connected:
        global client, osc_root
        client.send_message(osc_root, args)
        print('Sent {} {}'.format(osc_root, args))
    else:
        print("Error: cannot send OSC when not connected")

def generate_utterance(addr, *args):
    if connected:
        global wavfile_count
        input_text = args[0]
        print("Generate Request Recieved with input text: {}".format(input_text))
        wavfileid = "{}_{:04d}".format(model_id, wavfile_count)
        wavfilename = wavfileid + '.wav'
        wavfile_count += 1
        wavfilepath = os.path.join(wav_write_path, wavfilename)
        sendMsg("recieved", input_text, wavfileid)
        audio_data = synthesizer.synthesize(input_text)
        with open(wavfilepath,'wb') as f:
            f.write(audio_data)
        print("Wrote file: {}".format(wavfilepath))
        sendMsg("finished", wavfilepath)
    else:
        print("Error: cannot generate utterances before handshake connection")


def handshake(addr, *args):
    global client, osc_send_ip, osc_send_port, connected
    if not connected:
        print("Handshake Recieved: ", addr, args)
        client = udp_client.SimpleUDPClient(osc_send_ip, osc_send_port)
        connected = True
        sendMsg("hello", 1)
        print('Sending messages to {} {}'.format(osc_send_ip, osc_send_port))
        print('Awaiting commands...')
    else:
        print("Handshake already made, coupled with {} {}".format(osc_send_ip, osc_send_port))

def close(addr, *args):
    global connected
    print("Recieved Goodbye Trigger")
    if connected:
        sendMsg("goodbye")
        connected = False
        raise Exception("Recieved shutdown message from {}".format(addr))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('model_path', help='Full path to model checkpoint')
  parser.add_argument('--model-id', help='A unique identifier used to create an OSC address path for this process. Defaults to the name of the file given in model-path.')
  parser.add_argument('--wav-write-path', help='Directory where wav files should be stored, if the directory does not exist it is created. By default uses the directory of model-path and creates a wordless_tmp directory within it. ')
  parser.add_argument('--osc-listen-ip', default='127.0.0.1')
  parser.add_argument('--osc-listen-port', type=int, default=9800)
  parser.add_argument('--osc-send-ip', default='127.0.0.1')
  parser.add_argument('--osc-send-port', type=int, default=57120)
  parser.add_argument('--generate_test', dest='generate_test', action='store_true')
  parser.set_defaults(generate_test=False)

  parser.add_argument('--logdir', default="")
  parser.add_argument('--hparams', default='',
    help='Hyperparameter overrides as a comma-separated list of name=value pairs')
  args = parser.parse_args()

  model_path = os.path.abspath(args.model_path)
  model_filepath = model_path+'.index'
  if not os.path.exists(model_filepath):
      raise Exception("File {} does not exist".format(model_filepath))

  root, ext = os.path.splitext(model_filepath)
  dir = os.path.dirname(root)
  filename = os.path.basename(root)

  model_id = args.model_id
  if model_id is None:
      model_id = filename

  osc_root = "/taco/{}".format(model_id)

  wav_write_path = args.wav_write_path
  if wav_write_path is None:
      wav_write_path = os.path.join(dir, "wordless_tmp")

  wav_write_path = os.path.abspath(wav_write_path)
  if not os.path.exists(wav_write_path):
      os.mkdir(wav_write_path)

  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

  infolog.init(os.path.join(args.logdir, 'server.log'), "serverlog")
  hparams.parse(args.hparams)
  print("LOADING SYNTHESIZER: {}".format(hparams_debug_string()))
  synthesizer.load(model_path)

  if args.generate_test:
    text_request = "with in emptiness in words enclose"
    print("Generating test: '{}'".format(text_request))
    utterance_data = synthesizer.synthesize(text_request)
    wavfilename = os.path.join(wav_write_path, "test.wav")
    with open(wavfilename,'wb') as f:
        f.write(utterance_data)
    print("Wrote test file to: {}".format(wavfilename))

  # Set up OSC server and wait for handshake
  print('Starting OSC server with address {}  ...'.format(osc_root))
  dispatcher = dispatcher.Dispatcher()
  dispatcher.map("{}/generate".format(osc_root), generate_utterance)
  dispatcher.map("{}/handshake".format(osc_root), handshake)
  dispatcher.map("{}/close".format(osc_root), close)
  server = osc_server.ThreadingOSCUDPServer((args.osc_listen_ip, args.osc_listen_port), dispatcher)
  osc_send_addr = args.osc_send_ip
  osc_send_port = args.osc_send_port
  print("Waiting for handshake on {}".format(server.server_address))
  server.serve_forever()
