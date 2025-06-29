import pandas as pd
from googleapiclient import discovery
from google.auth import default

credentials, project = default()
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

                # Get internal and external IP
                internal_ip = external_ip = None
                for iface in instance.get('networkInterfaces', []):
                    internal_ip = iface.get('networkIP')
                    access_configs = iface.get('accessConfigs', [])
                    if access_configs:
                        external_ip = access_configs[0].get('natIP')

                # Labels
                labels = instance.get('labels', {})
                owner_name = labels.get('owner_name', '')
                owner_state = labels.get('owner_state', '')

                # Tags
                tags = instance.get('tags', {}).get('items', [])
                tag_1 = tags[0] if len(tags) > 0 else ''
                tag_2 = tags[1] if len(tags) > 1 else ''

                all_instances.append({
                    'name': name,
                    'zone': zone_name,
                    'machine_type': machine_type,
                    'cpu_platform': cpu_platform,
                    'status': status,
                    'creation_time': creation_time,
                    'internal_ip': internal_ip,
                    'external_ip': external_ip,
                    'owner_name': owner_name,
                    'owner_state': owner_state,
                    'tag_1': tag_1,
                    'tag_2': tag_2
                })

        request = compute.instances().aggregatedList_next(previous_request=request, previous_response=response)

    return all_instances

# Fetch and save to Excel
instances = list_detailed_instances(project)
df = pd.DataFrame(instances)
df.to_excel("gcp_vm_inventory.xlsx", index=False)

print("✅ VM data with labels and tags saved to gcp_vm_inventory.xlsx")
