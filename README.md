# rna_editing_pipeline

```
conda env create -f conda_env.txt

export PATH=$PATH:/path/to/scripts/bin

cd job_files

sh run_workflow_v1.sh
```


```
docker-machine create -d virtualbox singularity
docker-machine env singularity
eval $(docker-machine env singularity)

```