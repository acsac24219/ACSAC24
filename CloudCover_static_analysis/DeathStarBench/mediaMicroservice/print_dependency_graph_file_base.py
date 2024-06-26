import json
import networkx as nx
import matplotlib.pyplot as plt

# 读取JSON文件
# lsc-mediaMicroservices-file-base-dependency-graph-output.log.json
# lsc-socialNetwork-file-base-dependency-graph-output.log.json
with open('lsc-mediaMicroservices-file-base-dependency-graph-output.log.json', 'r') as file:
    data = json.load(file)

# 创建有向图
graph = nx.DiGraph()

# 添加节点和边
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

# 绘制图形
pos = nx.spring_layout(graph)
labels = nx.get_node_attributes(graph, 'label')
# method_labels = nx.get_node_attributes(graph, 'method_full_name')
# rpc_labels = nx.get_node_attributes(graph, 'rpc_func_name_symbol')

plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(graph, pos, node_size=500, alpha=0.8)
nx.draw_networkx_edges(graph, pos, arrows=True)
nx.draw_networkx_labels(graph, pos, labels=labels)
# nx.draw_networkx_labels(graph, pos, labels=method_labels, font_size=8, font_color='r', verticalalignment='bottom')
# nx.draw_networkx_labels(graph, pos, labels=rpc_labels, font_size=8, font_color='b', verticalalignment='top')

plt.axis('off')
plt.show()