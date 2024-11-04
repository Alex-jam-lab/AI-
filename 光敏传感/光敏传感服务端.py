import socket
import openpyxl
from datetime import datetime
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 设置最终Excel文件名和临时文件名
final_excel_filename = 'server_data.xlsx'
temp_excel_filename = 'server_data_temp.xlsx'

# 删除原有的最终Excel文件（如果存在）
if os.path.exists(final_excel_filename):
    os.remove(final_excel_filename)
    logging.info(f"已删除旧文件：{final_excel_filename}")

# 创建一个新的Excel工作簿并设置表头
wb = openpyxl.Workbook()
ws = wb.active
ws.append(['时间', '数据值', '光线类型'])
wb.save(temp_excel_filename)

# 定义光强度分类阈值
THRESHOLDS = {
    '强光': 8000,
    '正常光': 30000,
    '弱光': 45000,
    '暗光': 60000
}

# 创建socket对象并绑定到指定端口
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 9988
serversocket.bind((host, port))
serversocket.listen(5)
logging.info(f"服务器启动，正在监听接口 {host}:{port}")

# 设置数据集目录
dataset_type = '光敏数据集'
os.makedirs(dataset_type, exist_ok=True)

def get_light_type(data_value):
    """根据数据值获取光线类型"""
    if data_value < THRESHOLDS['强光']:
        return '强光'
    elif data_value < THRESHOLDS['正常光']:
        return '正常光'
    elif data_value < THRESHOLDS['弱光']:
        return '弱光'
    else:
        return '暗光'

def log_data(timestamp, data_value, light_type, addr):
    """记录数据到Excel和文本文件"""
    # 更新Excel文件
    wb = openpyxl.load_workbook(temp_excel_filename)
    ws = wb.active
    ws.append([timestamp, data_value, light_type])
    wb.save(temp_excel_filename)
    logging.info(f"从 {addr} 接收到数据：{data_value}, 光线类型：{light_type} 已记录到Excel文件")

    # 更新相应光线类型的文本文件
    light_data_file_path = os.path.join(dataset_type, f'{light_type}.txt')
    with open(light_data_file_path, 'a') as light_data_file:
        light_data_file.write(f"{timestamp}, {data_value}\n")
    logging.info(f"数据已追加到文件：{light_data_file_path}")

def handle_client(clientsocket, addr):
    """处理客户端连接"""
    try:
        while True:
            data = clientsocket.recv(1024)
            if not data:
                break
            data_value = int(data.decode('utf-8'))

            # 获取光线类型
            light_type = get_light_type(data_value)

            # 记录时间和数据
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_data(timestamp, data_value, light_type, addr)

            # 向客户端发送确认
            clientsocket.sendall(b"Data received")
    except Exception as e:
        logging.error(f"处理客户端 {addr} 时发生错误：{e}")
    finally:
        clientsocket.close()

def main():
    try:
        while True:
            # 接受客户端连接
            clientsocket, addr = serversocket.accept()
            logging.info(f"连接地址：{addr}")
            handle_client(clientsocket, addr)
    except KeyboardInterrupt:
        logging.info("服务器关闭")
    except Exception as e:
        logging.error(f"发生错误：{e}")
    finally:
        # 将临时文件重命名为最终文件
        if os.path.exists(temp_excel_filename):
            os.rename(temp_excel_filename, final_excel_filename)
            logging.info(f"临时文件已重命名为最终文件：{final_excel_filename}")
        serversocket.close()

if __name__ == "__main__":
    main()