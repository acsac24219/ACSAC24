import json
import networkx as nx
import matplotlib.pyplot as plt

# Load the JSON file
with open('lsc-socialNetwork-file-base-dependency-graph-output.log.json', 'r') as file:
    data = json.load(file)

# Create a directed graph
graph = nx.DiGraph()

# Add nodes and edges
for item in data:
    current_service_name = item.get('current_service_name')
    call_service_name = item.get('call_service_name')
    current_service_method_full_name = item.get('current_service_method_full_name')
    rpc_func_name_symbol = item.get('rpc_func_name_symbol')

    graph.add_node(current_service_name, label=current_service_name,
                   method_full_name=current_service_method_full_name,
                   rpc_func_name_symbol=rpc_func_name_symbol)
    graph.add_node(call_service_name, label=call_service_name)
    graph.add_edge(current_service_name, call_service_name)

# Draw the graph, adjusting node distances
pos = nx.spring_layout(graph, k=2.5)  # Increase the k value to increase the distance between nodes

plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(graph, pos, node_size=500, alpha=0.8)
nx.draw_networkx_edges(graph, pos, arrows=True)

# Adjust font size
nx.draw_networkx_labels(graph, pos, labels=nx.get_node_attributes(graph, 'label'), font_size=10)

plt.axis('off')
plt.show()
