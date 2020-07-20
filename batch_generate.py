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

def load_csv(infile, delim='|'):
    root, ext = os.path.splitext(infile)
    dir = os.path.dirname(root)
    filename = os.path.basename(root)
    data = {'indexof': {}, 'rows': [], 'models': []}

    with open(infile, 'r', newline='') as csv_in:
        reader = csv.reader(csv_in, delimiter=delim, quoting=csv.QUOTE_NONE)
        for idx, row in enumerate(reader, start=0):
            if idx is 0:
                # header...
                data['header'] = row
                for ix, heading in enumerate(row, start=0):
                    data['indexof'][heading] = ix
            else:
                data['rows'].append(row)
                model = row[data['indexof']['model']]
                if model not in data['models']:
                    data['models'].append(model)

    return data

def generate_files(data, synthesizers, outdir):
    cnt = 0
    outpath = os.path.join(outdir, "conversation.csv")
    with open(outpath, 'w', newline='') as csv_out:
        metawriter = csv.writer(csv_out, delimiter='|', quoting=csv.QUOTE_NONE)
        metawriter.writerow(['speaker', 'line', 'file'])
        for row in data['rows']:
            model = row[data['indexof']['model']]
            text = row[data['indexof']['text']]
            speaker = row[data['indexof']['speaker']]
            synth = synthesizers[model]
            outfile = "{}_{}.wav".format(cnt, speaker)
            print("Synthesizing {}".format(outfile))

            metawriter.writerow([speaker, text, outfile])
            outfile = os.path.join(outdir, outfile)
            synth = synthesizers[model]
            wavdata = synth.synthesize(text)

            with open(outfile, 'wb') as wf: # write wave file...
                wf.write(wavdata)
                print("Writing {}".format(outfile))
            cnt = cnt + 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', help='Input csv file')
    parser.add_argument('--modeldir', default='../models/tacotron/', help="Root directory of models referred to in csv file")
    parser.add_argument('-o', '--outdir', help="Output directory (by default writes inputfile_render)")
    parser.add_argument('--hparams', default='', help='Hyperparameter overrides as a comma-separated list of name=value pairs')
    args = parser.parse_args()

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    hparams.parse(args.hparams)
    print(hparams_debug_string())

    infile = os.path.abspath(args.inputfile)

    if not os.path.exists(infile):
        raise Exception("CSV File {} does not exist".format(infile))

    modelroot = args.modeldir
    if not os.path.exists(modelroot):
        raise Exception("Model directory {} does not exist".format(modelroot))


    root, ext = os.path.splitext(infile)
    infilename = os.path.basename(root)

    outdir = args.outdir

    if not outdir:
        outdir = "./{}_render/".format(infilename)
    elif os.path.exists(outdir):
        raise Exception("Output Directory {} does not exist".format(outdir))

    data = load_csv(infile)

    print("CSV RESULT", data)

    # if CSV loaded successfully... create synthesizers for each voice and make sure all checkpoint files exist...
    synthesizers = {}
    for model in data['models']:
        modeldir = os.path.join(modelroot, model)
        if not os.path.exists(modeldir + ".index"):
            raise Exception("Model {} does not exist".format(modeldir))
        synthesizers[model] = Synthesizer()
        synthesizers[model].load(modeldir)

        # See: https://stackoverflow.com/questions/46056206/tensorflow-value-error-variable-already-exists-disallowed
        tf.get_variable_scope().reuse_variables()


    print("SYNTHESIZERS RESULT", synthesizers)

    # if they do, create the output directory and get started...
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # generate audio files and conversation file
    generate_files(data, synthesizers, outdir)

    print("DONE")
