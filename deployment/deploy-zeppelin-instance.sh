#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

createCluster () {
  aws emr create-cluster --termination-protected \
    --applications \
        Name=Hadoop \
        Name=Hive \
        Name=Pig \
        Name=Hue \
        Name=Zeppelin \
        Name=Spark \
    --ec2-attributes \
      '{"KeyName":"keypair","InstanceProfile":"EMR_EC2_DefaultRole","SubnetId":"subnet-48b8c02f","EmrManagedSlaveSecurityGroup":"sg-0202ff79","EmrManagedMasterSecurityGroup":"sg-667f821d"}' \
    --release-label emr-5.9.0 \
    --log-uri 's3n://aws-logs-920822283306-eu-west-1/elasticmapreduce/' \
    --instance-groups '[{"InstanceCount":2,"InstanceGroupType":"CORE","InstanceType":"r3.xlarge","Name":"Core - 2"},{"InstanceCount":1,"InstanceGroupType":"MASTER","InstanceType":"r3.xlarge","Name":"Master - 1"}]' \
    --auto-scaling-role EMR_AutoScaling_DefaultRole \
    --bootstrap-action "Path=s3://twde-datalab/bootstrap-action.sh" \
    --ebs-root-volume-size 10 \
    --service-role EMR_DefaultRole \
    --enable-debugging \
    --name ${cluster_name:-'Deployed from CLI'} \
    --scale-down-behavior TERMINATE_AT_INSTANCE_HOUR \
    --region eu-west-1 \
    --steps Type=CUSTOM_JAR,Name=CustomJAR,ActionOnFailure=CONTINUE,Jar=s3://eu-west-1.elasticmapreduce/libs/script-runner/script-runner.jar,Args=["s3://twde-datalab/steps/zeppelin-python-version.sh"]
}



sshWithKeypair() {
  echo "Connecting to cluster via ssh on port 8157"
  chmod 600 ~/keypair.pem
  ssh -i ~/keypair.pem -ND 8157 hadoop@ec2-XX-XXX-XXX-XX.eu-west-1.compute.amazonaws.com
}

push_latest_bootstrap_actions(){
  aws s3 cp ./bootstrap-action.sh s3://twde-datalab/
}
push_latest_configuration_file(){
  aws s3 cp ./configuration.json s3://twde-datalab/
}


while getopts 'n:' arg
do
  case ${arg} in
    n) cluster_name=${OPTARG};;
    *) echo "Unexpected argument"
  esac
done
echo  

push_latest_configuration_file
push_latest_bootstrap_actions
createCluster
sshWithKeypair
