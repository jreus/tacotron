# Field Notes

This package is Tacotron test trainer packaged for use with Google Cloud Compute.
This is a new branch on the fork of the original Tacotron repository.


## A Tip on Training Neural Networks

While training neural networks, mostly a target error is defined alongside with a maximum amount of iterations to train. So for example, a target error could be 0.001MSE. Once this error has been reached, the training will stop - if this error has not been reached after the maximum amount of iterations, the training will also stop.

But it seems like you want to train until you know the network can't do any better. Saving the 'best' parameters like you're doing is a fine approach, but do realise that once some kind of minimum cost has been reached, the error won't fluctuate that much anymore. It won't be like the error suddenly goes up significantly, so it is not completely necessary to save the network.

There is no such thing as 'minimal cost' - the network is always trying to go to some local minima, and it will always be doing so. There is not really way you (or an algorithm) can figure out that there is no better error to be reached anymore.

tl;dr - just set a target reasonable target error alongside with a maximum amount of iterations.


## HOW TO RUN LOCAL GCLOUD TEST
```
DATASETDIR=../datasets/LJSpeech-Mini/
PREPROCESSDIR=../datasets/LJSpeech-Mini/tacotron/
TACOTRAIN=$PREPROCESSDIR/train.txt
LOGDIR=bucket

gcloud ai-platform local train --module-name=trainer.task --package-path=trainer -- --pre-datadir=$DATASETDIR --dataset=ljspeech --pre-outdir=$PREPROCESSDIR --trainingfile=$TACOTRAIN --model='tacotron' --jobname=taco_LJM_001 --job-dir=$LOGDIR --max-trainsteps=5 --batch-size=32 --summary-interval=2 --checkpoint-interval=5 --tf-loglevel=1
```

#### On SB1 dataset
Remember to add the --preprocess flag if you need to do preprocessing.
Preprocessing can take some time and generates a lot of files, so don't do it more than once unless your core dataset changes!
```
DATASETDIR=../datasets/SB1/
PREPROCESSDIR=../datasets/SB1/tacotron
TACOTRAIN=$PREPROCESSDIR/train.txt
LOGDIR=bucket
JOBNAME='taco_SB1_test'

gcloud ai-platform local train --module-name=trainer.task --package-path=trainer -- --pre-datadir=$DATASETDIR --dataset=ljspeech --preprocess --pre-outdir=$PREPROCESSDIR --trainingfile=$TACOTRAIN --model='tacotron' --jobname=$JOBNAME --job-dir=$LOGDIR --max-trainsteps=5 --batch-size=32 --summary-interval=2 --checkpoint-interval=5 --tf-loglevel=1
```

#### On SB2 dataset
Remember to add the --preprocess flag if you need to do preprocessing.
Preprocessing can take some time and generates a lot of files, so don't do it more than once unless your core dataset changes!
```
DATASETDIR=../datasets/SB2/
PREPROCESSDIR=../datasets/SB2/tacotron
TACOTRAIN=$PREPROCESSDIR/train.txt
LOGDIR=bucket
JOBNAME='taco_SB2_test'

gcloud ai-platform local train --module-name=trainer.task --package-path=trainer -- --pre-datadir=$DATASETDIR --dataset=ljspeech --preprocess --pre-outdir=$PREPROCESSDIR --trainingfile=$TACOTRAIN --model='tacotron' --jobname=$JOBNAME --job-dir=$LOGDIR --max-trainsteps=10 --batch-size=32 --summary-interval=2 --checkpoint-interval=5 --tf-loglevel=1
```


#### On MF1 dataset
Remember to add the --preprocess flag if you need to do preprocessing.
Preprocessing can take some time and generates a lot of files, so don't do it more than once unless the core dataset changes!
```
DATASETDIR=../datasets/MF1/
PREPROCESSDIR=../datasets/MF1/tacotron
TACOTRAIN=$PREPROCESSDIR/train.txt
LOGDIR=bucket
JOBNAME='taco_MF1_test'
#PREPROCESS='--preprocess' # comment this to dodge preprocessing

gcloud ai-platform local train --module-name=trainer.task --package-path=trainer -- --pre-datadir=$DATASETDIR --dataset=ljspeech $PREPROCESS --pre-outdir=$PREPROCESSDIR --trainingfile=$TACOTRAIN --model='tacotron' --jobname=$JOBNAME --job-dir=$LOGDIR --max-trainsteps=10 --batch-size=64 --summary-interval=5 --checkpoint-interval=5 --tf-loglevel=1
```


## Try to synthesize something...

1. **Run the demo server**:
Point it at whatever checkpoint you want to use.
```
python demo_server.py --checkpoint ../models/tacotron/model.ckpt-10
```

2. **Point your browser at localhost:9000** to do some synthesis
   * Type what you want to synthesize

You can use some phrases from the dataset itself, such as..

Printing, in the only sense with which we are at present concerned, differs from most if not from all the arts and crafts represented in the Exhibition

the invention of movable metal letters in the middle of the fifteenth century may justly be considered as the invention of the art of printing


## GET YOUR CLOUD STORAGE SET UP
Create a storage bucket where the training will happen, datasets will be stored, and trained models will be saved...
See locations: https://cloud.google.com/storage/docs/locations
```
PROJECT_ID=$(gcloud config list project --format "value(core.project)")
BUCKET_NAME=${PROJECT_ID}-taco2
echo $BUCKET_NAME
REGION=EUROPE-WEST4
gsutil mb -l $REGION gs://$BUCKET_NAME # this actually makes the bucket
```
If needed you can set the core project using `gcloud config set project myprojectid-271656`

If you need to recall your project bucket name later use `gsutil ls`
```
BUCKET_NAME=tacotron-263615-taco2
REGION=EUROPE-WEST4
```

### Upload your training data
Use gsutil to copy the training data files to your Cloud Storage bucket.
You'll also want to do all the preprocessing locally, because it's a PITA to
open files on the AI platform.
```
DATASETDIR=gs://$BUCKET_NAME/datasets/LJSpeech-Mini
gsutil -m cp -r ../datasets/LJSpeech-Mini/ $DATASETDIR
```

...this could take a little while, and it might be worth reading this first...
NOTE: You are performing a sequence of gsutil operations that may
run significantly faster if you instead use gsutil -m cp ... Please
see the -m section under "gsutil help options" for further information
about when gsutil -m can be advantageous.

##### For the SB1 dataset
```
DATASETDIR=gs://$BUCKET_NAME/datasets/SB1
gsutil -m cp -r ../datasets/SB1/ $DATASETDIR
```

##### For MF1
```
DATASETDIR=gs://$BUCKET_NAME/datasets/MF1
gsutil -m cp -r ../datasets/MF1/ $DATASETDIR
```


### SUBMIT A CLOUD PROCESSING JOB
The following variables contain values used for staging a job:
Remember we won't be doing preprocessing in the cloud, so only the TACOTRAIN path is needed. (see runjob.sh for the latest)
```
PROJECT_ID=$(gcloud config list project --format "value(core.project)")
BUCKET_NAME=${PROJECT_ID}-taco2
REGION=EUROPE-WEST4

# Create a unique job name
now=$(date +"%Y%m%d_%H%M%S")
JOB_NAME="taco_$now"

TRAINER_PACKAGE_PATH="./trainer"
TRAINER_MAIN_MODULE="trainer.task"
JOB_DIR="gs://$BUCKET_NAME" #job output path
RUNTIME_VERSION="1.14"
PYTHON_VERSION="3.5"

DATASETDIR="datasets/LJSpeech-Mini"
PREPROCESSDIR="$DATASETDIR/tacotron"
TACOTRAIN="gs://$PREPROCESSDIR/train.txt"
SCALE_TIER="basic" # see documentation for more powerful systems to use

```

Debugging is a bitch
https://cloud.google.com/ml-engine/docs/troubleshooting

USING CLOUD API IN PYTHON
https://cloud.google.com/storage/docs/reference/libraries
https://googleapis.dev/python/storage/latest/client.html


Finally start the training job:
See: https://cloud.google.com/sdk/gcloud/reference/ai-platform/jobs/submit/training

```
gcloud ai-platform jobs submit training $JOB_NAME --module-name=$TRAINER_MAIN_MODULE --package-path=$TRAINER_PACKAGE_PATH --scale-tier=$SCALE_TIER --staging-bucket=$JOB_DIR --region=$REGION --job-dir=$JOB_DIR --python-version=$PYTHON_VERSION --runtime-version=$RUNTIME_VERSION --stream-logs -- --dataset=ljspeech --pre-outdir=$PREPROCESSDIR --trainingfile=$TACOTRAIN --model='tacotron' --jobname=taco001 --max-trainsteps=10 --summary-interval=2 --checkpoint-interval=5 --tf-loglevel=1


```



You may see a response like this...

```
Job [taco_20191228_234923] submitted successfully.
Your job is still active. You may view the status of your job with the command

  $ gcloud ai-platform jobs describe taco_20191228_234923

or continue streaming the logs with the command

  $ gcloud ai-platform jobs stream-logs taco_20191228_234923
jobId: taco_20191228_234923
state: QUEUED
```

You can also view the status on your cloud console...
https://console.cloud.google.com
https://cloud.google.com/ml-engine/docs/training-jobs

### Monitor status on tensorboard
Run tensorboard and point it at your remote logs directory. Then visit localhost:6006
```

tensorboard --logdir=gs://tacotron-263615-taco2/logs-taco_sb1_20200103_131437/
tensorboard --logdir=gs://tacotron-263615-taco2/
```

__NOTE__: you may first need to get authentification credentials to log in remotely
```
gcloud auth application-default login
```
See: https://stackoverflow.com/questions/40830085/tensorboard-can-not-read-summaries-on-google-cloud-storage


## DOWNLOAD THE TRAINED MODEL
```
# There it is!
gsutil ls gs://tacotron-263615-taco2/logs-taco001/
gsutil ls gs://tacotron-263615-taco2/logs-taco_MF1_20200105_133301/
gsutil ls gs://tacotron-263615-taco2/logs-taco_MF1_32_20200106_130237/
gsutil ls gs://tacotron-263615-taco2/logs-taco_sb2_20200106_143755/
```

```
gsutil -m cp gs://tacotron-263615-taco2/logs-taco_sb2_20200106_143755/model.ckpt-84000* ../models/tacotron/sb2/

```

## Run the demo server using the checkpoint you just downloaded
```
python demo_server.py --checkpoint output/gcloud/logs-taco001/model.ckpt-20
```
