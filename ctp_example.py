#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTP Protocol Client Usage Example
Quick sending of STA_SSID_INFO commands
"""

import socket
import struct
import json

def send_sta_ssid_info(host, port, ssid, password, mqtt_server="95.216.222.194", mqtt_port=1883):
    """
    Send STA_SSID_INFO command
    
    Args:
        host: Device IP address
        port: Device port number
        ssid: WiFi name
        password: WiFi password
        mqtt_server: MQTT server address or domain
        mqtt_port: MQTT server port number
    """
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        print(f"✅ Connected to {host}:{port}")
        
        # Construct JSON content
        content = {
            "op": "PUT",
            "param": {
                "ssid": ssid,
                "pwd": password,
                "status": "1",
                "mqtt_server": mqtt_server,
                "mqtt_port": str(mqtt_port)
            }
        }
        content_str = json.dumps(content, separators=(',', ':'))
        
        # Construct CTP message packet
        topic = "STA_SSID_INFO"
        topic_bytes = topic.encode('utf-8')
        content_bytes = content_str.encode('utf-8')
        
        # Little endian length
        topic_len = len(topic_bytes)
        content_len = len(content_bytes)
        
        message = (
            b"CTP:" +                                    # CTP prefix
            struct.pack('<H', topic_len) +              # topic length (little endian)
            topic_bytes +                                # topic content
            struct.pack('<I', content_len) +            # content length (little endian)
            content_bytes                                # content data
        )
        
        # Send message
        sock.sendall(message)
        print(f"📤 STA_SSID_INFO command sent")
        print(f"   SSID: {ssid}")
        print(f"   Password: {password}")
        print(f"   MQTT Server: {mqtt_server}")
        print(f"   MQTT Port: {mqtt_port}")
        print(f"   Message length: {len(message)} bytes")
        
        # Receive response
        print("⏳ Waiting for device response...")
        sock.settimeout(5)
        
        # Receive CTP prefix
        prefix = sock.recv(4)
        if prefix != b"CTP:":
            print("❌ Invalid CTP prefix")
            return False
        
        # Receive topic length and content
        topic_len_data = sock.recv(2)
        topic_len = struct.unpack('<H', topic_len_data)[0]
        topic = sock.recv(topic_len).decode('utf-8')
        
        # Receive content length and data
        content_len_data = sock.recv(4)
        content_len = struct.unpack('<I', content_len_data)[0]
        
        if content_len > 0:
            response_content = sock.recv(content_len).decode('utf-8')
            print(f"📥 Response received:")
            print(f"   Topic: {topic}")
            print(f"   Content: {response_content}")
            # Content: {"op":"NOTIFY","param":{"ssid":"TJxu","pwd":"Xu***888","status":"1","mqtt_server":"broker.emqx.io","mqtt_port":"1883"}}
            # Parse response
            try:
                response_json = json.loads(response_content)
                if response_json.get('op') == 'NOTIFY':
                    print("✅ WiFi and MQTT configuration successful!")
                    param = response_json.get('param', {})
                    if 'mqtt_server' in param and 'mqtt_port' in param:
                        print(f"   MQTT Server: {param['mqtt_server']}")
                        print(f"   MQTT Port: {param['mqtt_port']}")
                    return True
                else:
                    print(f"❌ WiFi configuration failed: {response_json.get('param', {}).get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"⚠️ Response format error: {response_content}")
                return False
        else:
            print("⚠️ Received empty response")
            return False
            
    except socket.timeout:
        print("❌ Response timeout")
        return False
    except ConnectionRefusedError:
        print(f"❌ Connection refused, please check device IP and port: {host}:{port}")
        return False
    except Exception as e:
        print(f"❌ Send failed: {e}")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    # Configuration parameters
    DEVICE_IP = "192.168.4.1"    # Modify to your device IP
    DEVICE_PORT = 3333             # Modify to your device port
    WIFI_SSID = "JioFiber-EASO"          # WiFi name
    WIFI_PASSWORD = "7285045500"     # WiFi password
    MQTT_SERVER = "95.216.222.194"  # MQTT server address
    # MQTT_SERVER = "172.20.10.3"  # MQTT server address
    MQTT_PORT = 1883               # MQTT server port
    
    print("CTP Protocol Client - Quick WiFi Configuration")
    print("=" * 40)
    print(f"Device address: {DEVICE_IP}:{DEVICE_PORT}")
    print(f"WiFi name: {WIFI_SSID}")
    print(f"WiFi password: {WIFI_PASSWORD}")
    print(f"MQTT server: {MQTT_SERVER}:{MQTT_PORT}")
    print("=" * 40)
    
    # Send command
    success = send_sta_ssid_info(DEVICE_IP, DEVICE_PORT, WIFI_SSID, WIFI_PASSWORD, MQTT_SERVER, MQTT_PORT)
    
    if success:
        print("\n🎉 Operation completed!")
    else:
        print("\n💥 Operation failed!") 