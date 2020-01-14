# TODO:
# add cmd arguments for selecting between running remotely or locally
# with arguments for remote bucket and so on.. see NOTES.md

PROJECT_ID=$(gcloud config list project --format "value(core.project)")
BUCKET_NAME=${PROJECT_ID}-taco2
REGION="europe-west1"
#REGION="europe-west4"

# Create a unique job label, and generate a name each time you submit a job to AI Platform
now=$(date +"%Y%m%d_%H%M%S")
PLATFORM_JOB_NAME="taco_MF1_32_$now"

# And a unique job label

# UNCOMMENT AND CONFIGURE THESE LINES IF YOU WANT TO RESTORE FROM AN EXISTING CHECKPOINT
# gs://tacotron-263615-taco2/logs-taco_MF1_train/logs-taco_MF1_train-4000
#RESTORE_JOB_NAME="taco_MF1_train"
#RESTORE_CHECKPOINT=4000
#RESTORE_PATH="gs://$BUCKET_NAME/logs-$RESTORE_JOB_NAME"
#RESTORE_FLAGS="--checkpoint-restore-path=$RESTORE_PATH --restore-step=$RESTORE_CHECKPOINT"


TRAINER_PACKAGE_PATH="./trainer"
TRAINER_MAIN_MODULE="trainer.task"
JOB_DIR="gs://$BUCKET_NAME" #job output path
# See RUNTIME VERSION LIST HERE
# https://cloud.google.com/ml-engine/docs/runtime-version-list
# Note that the 1.13.1 runtime will no longer be supported on March 6 2020
RUNTIME_VERSION="1.13"
PYTHON_VERSION="3.5"

DATASETDIR="gs://$BUCKET_NAME/datasets/MF1"
PREPROCESSDIR="$DATASETDIR/tacotron"
TACOTRAIN="$PREPROCESSDIR/train.txt"
SCALE_TIER="BASIC_GPU" # see documentation for more powerful systems to use
#SCALE_TIER="BASIC"
# It's also important to check which regions have what accelerators available..
# see: https://cloud.google.com/compute/docs/gpus/
# https://cloud.google.com/ml-engine/docs/machine-types

BATCH_SIZE=32  # try different batch sizes, maybe 16, 32, 64 for small datasets
TRAINING_STEPS=200000
SUMMARY_EVERY=250
CHECKPOINT_EVERY=1000
LOG_LEVEL=1

# see: https://cloud.google.com/sdk/gcloud/reference/ai-platform/jobs/submit/training

gcloud ai-platform jobs submit training $PLATFORM_JOB_NAME --module-name=$TRAINER_MAIN_MODULE --package-path=$TRAINER_PACKAGE_PATH --scale-tier=$SCALE_TIER --staging-bucket=$JOB_DIR --region=$REGION --job-dir=$JOB_DIR --python-version=$PYTHON_VERSION --runtime-version=$RUNTIME_VERSION --stream-logs -- --dataset=ljspeech --pre-outdir=$PREPROCESSDIR --trainingfile=$TACOTRAIN --model='tacotron' --jobname=$PLATFORM_JOB_NAME --batch-size=$BATCH_SIZE --max-trainsteps=$TRAINING_STEPS $RESTORE_FLAGS --summary-interval=$SUMMARY_EVERY --checkpoint-interval=$CHECKPOINT_EVERY --tf-loglevel=$LOG_LEVEL



# gcloud ai-platform jobs list
# gcloud ai-platform cancel JOB_ID
