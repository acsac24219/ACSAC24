import json

def build_long_service_call_chains(json_records):
    """
    Build long service call chains from JSON records.
    
    Args:
    json_records (list of dict): List of JSON records with service call information.
    
    Returns:
    list: A list of strings representing the long service call chains.
    """
    # Initialize a dictionary to store the mapping of service calls
    service_map = {}
    for record in json_records:
        current_service = record['current_service_name']
        call_service = record['call_service_name']
        service_map.setdefault(current_service, set()).add(call_service)

    # Function to recursively build the call chain
    def build_chain(current_service, visited_services):
        """
        Recursively build the service call chain.

        Args:
        current_service (str): The current service name.
        visited_services (list): List of already visited services in the current chain.

        Returns:
        list: A list of complete service call chains starting from the current service.
        """
        chains = []
        for called_service in service_map.get(current_service, []):
            if called_service not in visited_services:  # Avoid loops
                new_visited = visited_services + [called_service]
                sub_chains = build_chain(called_service, new_visited)
                for sub_chain in sub_chains:
                    chains.append(current_service + " -> " + sub_chain)
        if not chains:  # End of chain
            return [current_service]
        return chains

    # Build long service call chains
    long_chains = []
    for service in service_map:
        long_chains.extend(build_chain(service, [service]))

    return long_chains

# Read JSON data from the file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Path to the JSON file
json_file_path = 'lsc-mediaMicroservices-file-base-dependency-graph-output.log.json'

# Read and parse the JSON file
try:
    json_data = read_json_file(json_file_path)
    long_service_call_chains = build_long_service_call_chains(json_data)
    print(long_service_call_chains)
except FileNotFoundError:
    print("File not found. Please check the file path.")
except json.JSONDecodeError:
    print("Error in decoding JSON. Please check the file content.")
