import os
import logging
import paho.mqtt.client as mqtt
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取配置，或者使用默认值
broker_address = os.getenv('MQTT_BROKER_ADDRESS', '192.168.190.215')
port = int(os.getenv('MQTT_BROKER_PORT', 1883))
topic = os.getenv('MQTT_TOPIC', 'base/light')
client_id = os.getenv('MQTT_CLIENT_ID', 'sunxiaochuan')
max_retries = 5  # 最大重试次数
retry_delay = 5  # 每次重试之间的延迟（秒）

# 回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(topic)
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        light_adc, light_dig = map(int, msg.payload.decode('utf-8').split(','))
        logger.info(f'Received message on topic "{msg.topic}": Light ADC={light_adc}, Light DIG={light_dig}')
    except ValueError as e:
        logger.error(f"Error parsing message: {e}")

# 创建MQTT客户端实例
# 注意：这里我们仍然使用旧版的CallbackAPIVersion
client = mqtt.Client(client_id=client_id, clean_session=True, protocol=mqtt.MQTTv311)

# 设置回调函数
client.on_connect = on_connect
client.on_message = on_message

# 尝试连接到MQTT代理
retries = 0
while retries < max_retries:
    try:
        logger.info(f"Attempting to connect to {broker_address}:{port}")
        client.connect(broker_address, port=port)
        break
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        retries += 1
        if retries < max_retries:
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            logger.error("Max retries reached. Exiting.")
            exit(1)

# 开始网络循环
try:
    client.loop_forever()
except KeyboardInterrupt:
    logger.info("Stopping MQTT client due to keyboard interrupt.")
finally:
    client.disconnect()
    logger.info("Disconnected from MQTT broker.")