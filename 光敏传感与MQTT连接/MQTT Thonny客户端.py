import network
from machine import ADC, Pin
import time
from umqtt.simple import MQTTClient

# 配置信息
WIFI_SSID = 'caixukun'
WIFI_PASSWORD = '12345688'
MQTT_SERVER = '192.168.190.215'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'sunxiaochuan'
MQTT_TOPIC = 'base/light'
RETRY_DELAY = 5  # 重试延迟时间（秒）
KEEPALIVE = 60  # 心跳包间隔（秒）

# 初始化ADC和数字输入引脚
light_adc = ADC(Pin(35, mode=Pin.IN))
light_dig = Pin(32, mode=Pin.IN)

# 连接到WiFi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print('正在连接WiFi...')
            time.sleep(RETRY_DELAY)
        print('WiFi连接成功')
        print('当前IP地址:', wlan.ifconfig()[0])
    else:
        print('已经连接到WiFi')

# 连接到MQTT服务器
def connect_to_mqtt(server, port, client_id):
    client = MQTTClient(client_id, server, port, keepalive=KEEPALIVE)
    while True:
        try:
            client.connect(clean_session=True)
            print('已连接到MQTT服务器')
            return client
        except Exception as e:
            print(f'连接MQTT服务器失败: {e}')
            time.sleep(RETRY_DELAY)  # 等待一段时间后重试

# 主循环
def main_loop(mqtt_client, adc_pin, dig_pin, topic):
    while True:
        try:
            # 读取传感器值
            ana_val = adc_pin.read_u16()
            dig_val = dig_pin.value()

            # 打印并发布消息
            message = f'{ana_val},{dig_val}'
            print('采集到的光感数据:', message)
            mqtt_client.publish(topic, message)
            
            # 延迟一秒
            time.sleep(1)
        except Exception as e:
            print(f'遇到错误: {e}')
            print('尝试重新连接MQTT服务器...')
            mqtt_client = connect_to_mqtt(MQTT_SERVER, MQTT_PORT, MQTT_CLIENT_ID)

# 主程序入口
if __name__ == '__main__':
    connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)
    client = connect_to_mqtt(MQTT_SERVER, MQTT_PORT, MQTT_CLIENT_ID)
    main_loop(client, light_adc, light_dig, MQTT_TOPIC)