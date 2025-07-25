from googleapiclient import discovery
from google.auth import default

# Authenticate and get project info
credentials, project = default()

# Initialize the Compute Engine client
compute = discovery.build('compute', 'v1', credentials=credentials)

def list_detailed_instances(project):
    request = compute.instances().aggregatedList(project=project)
    all_instances = []

    while request is not None:
        response = request.execute()

        for zone, instances_in_zone in response.get('items', {}).items():
            for instance in instances_in_zone.get('instances', []):
                name = instance.get('name')
                zone_name = instance['zone'].split('/')[-1]
                machine_type = instance['machineType'].split('/')[-1]
                status = instance.get('status')
                cpu_platform = instance.get('cpuPlatform')
                creation_time = instance.get('creationTimestamp')
                labels = instance.get('labels', {})
                tags = instance.get('tags', {}).get('items', [])

                # Get internal and external IPs
                internal_ip = external_ip = None
                for iface in instance.get('networkInterfaces', []):
                    internal_ip = iface.get('networkIP')
                    access_configs = iface.get('accessConfigs', [])
                    if access_configs:
                        external_ip = access_configs[0].get('natIP')

                all_instances.append({
                    'name': name,
                    'zone': zone_name,
                    'machine_type': machine_type,
                    'status': status,
                    'cpu_platform': cpu_platform,
                    'creation_time': creation_time,
                    'labels': labels,
                    'tags': tags,
                    'internal_ip': internal_ip,
                    'external_ip': external_ip
                })

        request = compute.instances().aggregatedList_next(previous_request=request, previous_response=response)

    return all_instances

# Call and print results
instances = list_detailed_instances(project)
for vm in instances:
    print(f"Name: {vm['name']}")
    print(f"Zone: {vm['zone']}")
    print(f"Machine Type: {vm['machine_type']}")
    print(f"CPU Platform: {vm['cpu_platform']}")
    print(f"Status: {vm['status']}")
    print(f"Created On: {vm['creation_time']}")
    print(f"Internal IP: {vm['internal_ip']}")
    print(f"External IP: {vm['external_ip']}")
    print(f"Labels: {vm['labels']}")
    print(f"Tags: {vm['tags']}")
    print('-' * 60)
