data = f"""Name Mean Max
gw_elk1
79.3% 79.5%
gw_elk2
77.8% 78.1%
gw_elk3
77.8% 78.0%
gw_k8s_node_4
75.3% 75.7%
gw_k8s_node_8
41.5% 47.4%
gw_k8s_node_7
46.5% 46.8%
gw_k8s_node_1
41.5% 41.8%
gw_k8s_node_3
39.1% 40.0%
gw_kafka2
39.0% 39.2%
gw_k8s_node_2
34.5% 35.0%
gw_kafka1
27.7% 27.9%
gw_k8s_node_5
24.9% 25.2%
gw_k8s_node_6
24.6% 25.0%
gw_kafka3
24.4% 24.6%"""


lines = [line.strip() for line in data.split('\n') if line.strip()]
print(lines)

