import json
import boto3

region = 'ap-south-1' 
ami_id = 'ami-0b982602dbb32c5bd'
instance_type = 't2.micro'
security_group_id = 'sg-04bc4018472f19b46'

def get_running_instances(): 
    ec2_client = boto3.client('ec2', region_name=region)
    try:        
        instances = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]
        return instance_ids

    except Exception as e:
        print(f"Error getting running instances: {e}")
        return []

def print_instances_to_stop(instance_ids):
    if not instance_ids:
        print("No running instances found.")
    else:
        print("Instances to stop:")
        for instance_id in instance_ids:
            print(instance_id)

def stop_all_running_instances(instance_ids):
    ec2_client = boto3.client('ec2', region_name=region)
    try:
        if not instance_ids:
            print("No running instances to stop.")
            return        
        response = ec2_client.stop_instances(InstanceIds=instance_ids)        
        print(f"Instances stopped successfully: {response['StoppingInstances']}")

    except Exception as e:
        print(f"Error stopping instances: {e}")

def create_and_start_instance(key_name):
    ec2_client = boto3.client('ec2', region_name=region)
    try:
        key_pair = ec2_client.create_key_pair(KeyName=key_name)
        print(f"Key Pair Created: {key_name}")
        print(f"Private Key: {key_pair['KeyMaterial']}")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidKeyPair.Duplicate' in str(e):
            print(f"Key Pair '{key_name}' already exists.")
        else:
            response = ec2_client.describe_key_pairs(KeyNames=[key_name])
    try:
        response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            MinCount=1,
            MaxCount=1
        )
        instance_id = response['Instances'][0]['InstanceId']
        print(f"Instance created and started successfully. Instance ID: {instance_id}")

        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])

        instance_description = ec2_client.describe_instances(InstanceIds=[instance_id])
        public_ip = instance_description['Reservations'][0]['Instances'][0]['PublicIpAddress']
        print(f"Instance Public IP: {public_ip}")
        print(f"SSH Command: ssh -i {key_name}.pem ec2-user@{public_ip}")

        return(200,{'message': 'Instance created & started', 'instance_id': instance_id,'Private Key': key_pair['KeyMaterial']   })
    except Exception as e:
        print(f"Error creating and starting instance: {e}")
        return(500, {'message': 'Error creating and starting instance', 'error': str(e)})

def stop_and_delete_instance():
    ec2_client = boto3.client('ec2', region_name=region)
    try:
        instances = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        if not instances['Reservations']:
            print("No running instances found to stop and delete.")
            return(500, {'message': 'No running instances found to stop and delete'})
        instance_id = instances['Reservations'][0]['Instances'][0]['InstanceId']
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        print(f"Instance stopped and deleted successfully. Instance ID: {instance_id}")
        return(200,{'message': 'Instance terminated', 'instance_id': instance_id})
    except Exception as e:
        print(f"Error stopping and deleting instance: {e}")
        return(500, {'message': 'Error stopping and deleting instance', 'error': str(e)})

def lambda_handler(event, context):       
    print(event)
    action = event['action']    
    key_name = event['key_name']
    # action = json.loads(event.get('body', '{}')) # Extract JSON body
    # action = payload.get('action') # Example input field


    # action = str(event)
    print("Action: ", action)
    if action == "1":
        status_code,body = create_and_start_instance(key_name)
    elif action == "2":
        status_code,body = stop_and_delete_instance()
    else:
        status_code = 500
        body = {'message': 'Invalid action'}

    # running_instance_ids = get_running_instances()
    # print_instances_to_stop(running_instance_ids)
    # stop_all_running_instances(running_instance_ids)

    
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {'Content-Type': 'application/json'}
    }
