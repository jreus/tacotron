#!/usr/bin/env python
"""
Batch synthesize audio files from a csv including
model / text info...
"""
from __future__ import print_function
import os
import wave
import sys
import argparse
import csv
import string
import tensorflow as tf
from hparams import hparams, hparams_debug_string
from synthesizer import Synthesizer


def generate(text, synth, outfile):
    print("Synthesizing {}".format(outfile))
    wavdata = synth.synthesize(text)
    with open(outfile, 'wb') as wf: # write wave file...
        wf.write(wavdata)
        print("Writing {}".format(outfile))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model1', help='Input model 1')
    parser.add_argument('model2', help='Input model 2')
    parser.add_argument('-o', '--outdir', default="./two_model_render", help="Output directory (by default writes two_model_render)")
    parser.add_argument('--hparams', default='', help='Hyperparameter overrides as a comma-separated list of name=value pairs')
    args = parser.parse_args()

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    hparams.parse(args.hparams)
    print(hparams_debug_string())

    modelpath1 = args.model1
    modelpath2 = args.model2

    if not os.path.exists(modelpath1 + ".index"):
        raise Exception("Model 1 {} does not exist".format(modelpath1))
    if not os.path.exists(modelpath2 + ".index"):
        raise Exception("Model 2 {} does not exist".format(modelpath2))

    outdir = args.outdir
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    synth1 = Synthesizer()
    synth1.load(modelpath1)

    # See: https://stackoverflow.com/questions/46056206/tensorflow-value-error-variable-already-exists-disallowed
    tf.get_variable_scope().reuse_variables()


    synth2 = Synthesizer()
    synth2.load(modelpath2)

    generate("watt will not", synth1, os.path.join(outdir, "0_model1.wav"))
    generate("abate one jot", synth2, os.path.join(outdir, "1_model2.wav"))
    generate("im a good", synth1, os.path.join(outdir, "2_model3.wav"))
    generate("person to compose with", synth2, os.path.join(outdir, "3_model4.wav"))

    print("DONE")
