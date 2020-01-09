# 2019 Jon Reus
#
"""Runs the training of the TACOTRON model"""

import argparse
import json
import os
from multiprocessing import cpu_count

import tensorflow as tf

from util import infolog
from trainer.hparams import hparams
import trainer.preprocess as preprocess
import trainer.train as train


if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  # INPUT ARGUMENTS FOR PREPROCESSOR
  parser.add_argument('--preprocess', dest='preprocess', action='store_true')
  parser.set_defaults(preprocess=False)
  parser.add_argument('--pre-datadir', default='', help='Filepath to input dataset')
  parser.add_argument('--pre-outdir', default='', help='Filepath to write mel and linear spectrograms')
  parser.add_argument('--dataset', required=True, choices=['blizzard', 'ljspeech'], help='Dataset format either follows LJSpeech or Blizzard2012 format.')
  #parser.add_argument('--num-workers', type=int, default=cpu_count())
  parser.add_argument('--num-workers', type=int, default=1)

  # TRAINING ARGUMENTS
  parser.add_argument('--trainingfile', default='training/train.txt')
  parser.add_argument('--model', default='tacotron')
  parser.add_argument('--jobname', default='', help='Name of the run. Used for output naming. Defaults to model name.')
  parser.add_argument('--job-dir', default='output', help='Root output directory for log files and models. Will create a folder inside this directory named after the current job, or if no jobname is provided, will use the model name.')
  parser.add_argument('--hparams', default='',
    help='Hyperparameter overrides as a comma-separated list of name=value pairs')
  parser.add_argument('--checkpoint-restore-path', help='Path to checkpoints from which to restore.')
  parser.add_argument('--restore-step', type=int, help='Global step to restore from checkpoint.')
  parser.add_argument('--batch-size', type=int, default=32, help='Training batch size.')
  parser.add_argument('--max-trainsteps', type=int, default=100000, help='Maximum number of training steps.')

  parser.add_argument('--summary-interval', type=int, default=100,
    help='Steps between running summary ops.')
  parser.add_argument('--checkpoint-interval', type=int, default=1000,
    help='Steps between writing checkpoints.')
  parser.add_argument('--slack-url', help='Slack webhook URL to get periodic reports.')
  parser.add_argument('--tf-loglevel', type=int, default=1, help='Tensorflow C++ log level.')
  parser.add_argument('--git', action='store_true', help='If set, verify that the client is clean.')
  args = parser.parse_args()

  # Preprocessor
  print("WHAT IS PREPROCESS?", args.preprocess)
  if args.preprocess is True:
      print('initializing preprocessing..')
      if args.dataset == 'blizzard':
          preprocess.preprocess_blizzard(args)
      elif args.dataset == 'ljspeech':
          preprocess.preprocess_ljspeech(args)

  os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(args.tf_loglevel)
  run_name = args.jobname or args.model
  output_dir = os.path.join(args.job_dir, 'logs-%s/' % run_name)
  os.makedirs(output_dir, exist_ok=True)
  infolog.init(os.path.join(output_dir, 'train.log'), run_name, args.slack_url)
  hparams.parse(args.hparams)
  train.train(output_dir, args)
