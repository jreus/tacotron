# Field Notes and Changes

## Preprocessing a Custom Dataset
I've changed some of the input arguments of the preprocessor to be a bit more flexible and to allow for other datasets in the same 'format' as LJSpeech-1.1 and Blizzard2012.

Here is an example run.

```
python preprocess.py --dataset=ljspeech --datadir=../datasets/LJSpeech-Mini/ --outdir=../datasets/LJSpeech-Mini/tacotron/

```

## Training on a Custom Dataset
Again I've changed some of the input arguments of train.py, removing the base_dir and instead opting to provide explicit file paths to the training data and output directories. I also added a --max_train_steps argument.

```
python train.py --trainingfile=../datasets/LJSpeech-Mini/tacotron/train.txt --model=tacotron --jobname=taco001 --outdir=output/ --summary_interval=5 --checkpoint_interval=2 --max_train_steps=2
```

## Synthesis
1. **Run the demo server**:
Point it at whatever checkpoint you want to use.
```
python demo_server.py --checkpoint output/logs-taco001/model.ckpt-6
```

2. **Point your browser at localhost:9000**
   * Type what you want to synthesize




## ALSO CHECK OUT

### Audio Samples

  * **[Audio Samples](https://keithito.github.io/audio-samples/)** from models trained using this repo.
    * The first set was trained for 441K steps on the [LJ Speech Dataset](https://keithito.com/LJ-Speech-Dataset/)
      * Speech started to become intelligible around 20K steps.
    * The second set was trained by [@MXGray](https://github.com/MXGray) for 140K steps on the [Nancy Corpus](http://www.cstr.ed.ac.uk/projects/blizzard/2011/lessac_blizzard2011/).


### Recent Updates

1. @npuichigo [fixed](https://github.com/keithito/tacotron/pull/205) a bug where dropout was not being applied in the prenet.

2. @begeekmyfriend created a [fork](https://github.com/begeekmyfriend/tacotron) that adds location-sensitive attention and the stop token from the [Tacotron 2](https://arxiv.org/abs/1712.05884) paper. This can greatly reduce the amount of data required to train a model.
