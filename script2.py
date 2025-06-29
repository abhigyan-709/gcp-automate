import pandas as pd
from googleapiclient import discovery
from google.auth import default

# Authenticate and get project
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
                    'internal_ip': internal_ip,
                    'external_ip': external_ip,
                    'labels': str(labels),
                    'tags': ", ".join(tags)
                })

        request = compute.instances().aggregatedList_next(previous_request=request, previous_response=response)

    return all_instances

# Fetch instance data
instances = list_detailed_instances(project)

# Convert to DataFrame
df = pd.DataFrame(instances)

# Save to Excel
df.to_excel("gcp_vm_inventory.xlsx", index=False)

print("✅ VM data saved to gcp_vm_inventory.xlsx")
