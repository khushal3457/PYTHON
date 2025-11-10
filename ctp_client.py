 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTP Protocol Client
Used to send STA_SSID_INFO commands to devices
"""

import socket
import struct
import json
import time

class CTPClient:
    def __init__(self, host='192.168.4.1', port=3333):
        """
        Initialize CTP Client
        
        Args:
            host: Device IP address
            port: Device port number
        """
        self.host = host
        self.port = port
        self.sock = None
        
        # CTP Protocol Constants
        self.CTP_PREFIX = b"CTP:"
        self.CTP_PREFIX_LEN = 4
        self.CTP_TOPIC_LEN = 2
        self.CTP_TOPIC_CONTENT_LEN = 4
        
    def connect(self):
        """Connect to device"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)  # 设置超时时间
            self.sock.connect((self.host, self.port))
            print(f"Successfully connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Disconnected")
    
    def send_ctp_message(self, topic, content):
        """
        Send CTP message
        
        Args:
            topic: Topic name
            content: Message content
            
        Returns:
            bool: Whether sending was successful
        """
        if not self.sock:
            print("Not connected to device")
            return False
        
        try:
            # Construct CTP message
            topic_bytes = topic.encode('utf-8')
            content_bytes = content.encode('utf-8') if content else b''
            
            # Calculate length (little endian)
            topic_len = len(topic_bytes)
            content_len = len(content_bytes)
            
            # Construct complete CTP message packet
            message = (
                self.CTP_PREFIX +                                    # "CTP:" (4 bytes)
                struct.pack('<H', topic_len) +                      # topic length (2 bytes, little endian)
                topic_bytes +                                        # topic content
                struct.pack('<I', content_len) +                    # content length (4 bytes, little endian)
                content_bytes                                        # content data
            )
            
            # Send message
            self.sock.sendall(message)
            print(f"CTP message sent:")
            print(f"  Topic: {topic}")
            print(f"  Content: {content}")
            print(f"  Message length: {len(message)} bytes")
            
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def send_sta_ssid_info(self, ssid, password):
        """
        Send STA_SSID_INFO command
        
        Args:
            ssid: WiFi name
            password: WiFi password
            
        Returns:
            bool: Whether sending was successful
        """
        # Construct JSON content
        content = {
            "op": "PUT",
            "param": {
                "ssid": JioFiber-EASO,
                "pwd": 7285045500,
                "status": "0"
            }
        }
        
        # Convert to JSON string
        content_str = json.dumps(content, separators=(',', ':'))
        
        # Send CTP message
        return self.send_ctp_message("STA_SSID_INFO", content_str)
    
    def receive_response(self, timeout=5):
        """
        Receive device response
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            str: Response content, returns None if timeout
        """
        if not self.sock:
            return None
        
        try:
            self.sock.settimeout(timeout)
            
            # Receive CTP prefix
            prefix = self.sock.recv(self.CTP_PREFIX_LEN)
            if len(prefix) != self.CTP_PREFIX_LEN:
                print("Failed to receive CTP prefix")
                return None
            
            if prefix != self.CTP_PREFIX:
                print(f"Invalid CTP prefix: {prefix}")
                return None
            
            # Receive topic length
            topic_len_data = self.sock.recv(self.CTP_TOPIC_LEN)
            if len(topic_len_data) != self.CTP_TOPIC_LEN:
                print("Failed to receive topic length")
                return None
            
            topic_len = struct.unpack('<H', topic_len_data)[0]
            
            # Receive topic content
            topic = self.sock.recv(topic_len).decode('utf-8')
            
            # Receive content length
            content_len_data = self.sock.recv(self.CTP_TOPIC_CONTENT_LEN)
            if len(content_len_data) != self.CTP_TOPIC_CONTENT_LEN:
                print("Failed to receive content length")
                return None
            
            content_len = struct.unpack('<I', content_len_data)[0]
            
            # Receive content data
            if content_len > 0:
                content = self.sock.recv(content_len).decode('utf-8')
            else:
                content = ""
            
            print(f"Response received:")
            print(f"  Topic: {topic}")
            print(f"  Content: {content}")
            
            return content
            
        except socket.timeout:
            print("Response timeout")
            return None
        except Exception as e:
            print(f"Failed to receive response: {e}")
            return None

def main():
    """Main function"""
    # Create CTP client
    client = CTPClient(host='192.168.1.100', port=8080)
    
    try:
        # Connect to device
        if not client.connect():
            return
        
        # Send STA_SSID_INFO command
        ssid = "JioFiber-EASO"
        password = "7285045500"
        
        print(f"\nSending WiFi configuration command...")
        print(f"SSID: {ssid}")
        print(f"Password: {password}")
        
        if client.send_sta_ssid_info(ssid, password):
            print("\nCommand sent successfully, waiting for device response...")
            
            # Receive device response
            response = client.receive_response(timeout=10)
            if response:
                try:
                    # Parse JSON response
                    response_json = json.loads(response)
                    print(f"\nDevice response parsed:")
                    print(json.dumps(response_json, indent=2, ensure_ascii=False))
                    
                    # Check response status
                    if response_json.get('errno') == 0:
                        print("\n✅ WiFi configuration successful!")
                    else:
                        print(f"\n❌ WiFi configuration failed: {response_json.get('param', {}).get('error', 'Unknown error')}")
                        
                except json.JSONDecodeError:
                    print(f"\n⚠️ Response format error: {response}")
            else:
                print("\n⚠️ No device response received")
        else:
            print("\n❌ Command sending failed")
    
    except KeyboardInterrupt:
        print("\nUser interrupted operation")
    except Exception as e:
        print(f"\nProgram execution error: {e}")
    finally:
        # Disconnect
        client.disconnect()

if __name__ == "__main__":
    print("CTP Protocol Client - WiFi Configuration Tool")
    print("=" * 50)
    
    # You can modify device IP and port here
    # client = CTPClient(host='192.168.1.100', port=8080)
    
    main() 