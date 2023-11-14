import yaml
import json
import urllib.request
import logging


# 提取节点
def process_urls(url_file, processor):
    try:
        with open(url_file, 'r') as file:
            urls = file.read().splitlines()

        for index, url in enumerate(urls):
            try:
                response = urllib.request.urlopen(url)
                data = response.read().decode('utf-8')
                processor(data, index + 1)
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")
    except Exception as e:
        logging.error(f"Error reading file {url_file}: {e}")


# 处理hysteria2
def process_hysteria2(data, index):
    try:
        json_data = json.loads(data)
        # 处理 hysteria2 数据
        # 提取所需字段
        auth = json_data["auth"]
        server_ports = json_data["server"]
        server_ports_slt = server_ports.split(":")
        server = server_ports_slt[0]
        ports = server_ports_slt[1]
        ports_slt = ports.split(",")
        server_port = int(ports_slt[0])
        fast_open = json_data["fastOpen"]
        insecure = json_data["tls"]["insecure"]
        sni = json_data["tls"]["sni"]
        name = f"hysteria2-{index}"

        # 创建当前网址的proxy字典
        proxy = {
            "name": name,
            "type": "hysteria2",
            "server": server,
            "port": server_port,
            "password": auth,
            "fast-open": fast_open,
            "sni": sni,
            "skip-cert-verify": insecure
        }

        # 将当前proxy字典添加到所有proxies列表中
        merged_proxies.append(proxy)

    except Exception as e:
        logging.error(f"Error processing hysteria2 data for index {index}: {e}")


def update_proxy_groups(config_data, merged_proxies):
    for group in config_data['proxy-groups']:
        if group['name'] in ['🚀 节点选择', '♻️ 自动选择', '🐟 漏网之鱼']:
            if 'proxies' not in group or not group['proxies']:
                group['proxies'] = [proxy['name'] for proxy in merged_proxies]
            else:
                group['proxies'].extend(proxy['name'] for proxy in merged_proxies)


def update_warp_proxy_groups(config_warp_data, merged_proxies):
    for group in config_warp_data['proxy-groups']:
        if group['name'] in ['🚀 节点选择', '♻️ 自动选择', '负载均衡', '🐟 漏网之鱼']:
            if 'proxies' not in group or not group['proxies']:
                group['proxies'] = [proxy['name'] for proxy in merged_proxies]
            else:
                group['proxies'].extend(proxy['name'] for proxy in merged_proxies)


# 包含hysteria2
merged_proxies = []

# 处理 hysteria2 URLs
process_urls('./urls/hysteria2_urls.txt', process_hysteria2)

# 读取普通的配置文件内容
with open('./templates/clash_template.yaml', 'r', encoding='utf-8') as file:
    config_data = yaml.safe_load(file)

# 读取warp配置文件内容
with open('./templates/clash_warp_template.yaml', 'r', encoding='utf-8') as file:
    config_warp_data = yaml.safe_load(file)

# 添加合并后的代理到proxies部分
if 'proxies' not in config_data or not config_data['proxies']:
    config_data['proxies'] = merged_proxies
else:
    config_data['proxies'].extend(merged_proxies)

if 'proxies' not in config_warp_data or not config_warp_data['proxies']:
    config_warp_data['proxies'] = merged_proxies
else:
    config_warp_data['proxies'].extend(merged_proxies)

# 更新自动选择和节点选择的proxies的name部分
update_proxy_groups(config_data, merged_proxies)
update_warp_proxy_groups(config_warp_data, merged_proxies)

# 将更新后的数据写入到一个YAML文件中，并指定编码格式为UTF-8
with open('./sub/hysteria2.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config_data, file, sort_keys=False, allow_unicode=True)

with open('./sub/hysteria2_warp.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config_warp_data, file, sort_keys=False, allow_unicode=True)

print("聚合完成")
