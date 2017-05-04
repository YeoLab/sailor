#!/usr/bin/env rnaediting

export PATH=$(dirname "$PWD")/src/py/:$PATH

cwl-runner --jobStore /projects/ps-yeolab3/bay001/hundley_rnae_20160210/pipeline/tmp/wtbam ../src/cwl/rnaediting2strands.workflow.cwl workflow_se.2strands.FULL.yml
