import socket
import time
import os

def main():
    server_id = int(os.getenv("SERVER", "1"))
    callsign = os.getenv("CALLSIGN", "NOCALL")
    ssid = os.getenv("SSID", "10")
    lat = float(os.getenv("LAT", "0.0"))
    lon = float(os.getenv("LON", "0.0"))
    symbol_table = os.getenv("SYMBOL_TABLE", "/")
    symbol = os.getenv("SYMBOL", "-")
    comment = os.getenv("COMMENT", "No comment")
    interval = int(os.getenv("INTERVAL", "900"))

    interval = max(60, min(interval, 3600))
    elapsed_time = interval

    while True:
        if elapsed_time >= interval:
            try:
                passcode = generate_passcode(callsign)
                transmit_position(server_id, callsign, ssid, passcode, lat, lon, symbol_table, symbol, comment)
                elapsed_time = 0
            except Exception as e:
                print(f"Packet could not be sent: {e}")
        time.sleep(1)
        elapsed_time += 1

def get_server(server_id):
    servers = {
        1: "turkiye.aprs2.net",
        2: "euro.aprs2.net",
        3: "noam.aprs2.net",
        4: "soam.aprs2.net",
        5: "asia.aprs2.net",
        6: "aunz.aprs2.net",
    }
    return servers.get(server_id, "rotate.aprs2.net")

def transmit_position(server_id, callsign, ssid, passcode, latitude, longitude, symbol_table, symbol, comment="Aprsphere Beacon"):
    server = get_server(server_id)
    port = 14580

    lat_str = format_latitude(latitude)
    lon_str = format_longitude(longitude)

    position_packet = f"{callsign}-{ssid}>APWD01,TCPIP*:!{lat_str}{symbol_table}{lon_str}{symbol}{comment}\n"
    status_packet   = f"{callsign}-{ssid}>APWD01,TCPIP*:>Powered by https://github.com/orhunavcu/aprsphere\n"
    login_packet    = f"user {callsign} pass {passcode} vers Aprsphere 1.0\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        sock.connect((server, port))
        sock.sendall(login_packet.encode("utf-8"))
        sock.sendall(position_packet.encode("utf-8"))
        sock.sendall(status_packet.encode("utf-8"))
        raw = sock.recv(1024).decode("utf-8").strip()
        print(f"[{server}] Server response: {raw}")

def format_latitude(latitude):
    deg = int(abs(latitude))
    minutes = (abs(latitude) - deg) * 60
    direction = "N" if latitude >= 0 else "S"
    return f"{deg:02d}{minutes:05.2f}{direction}"

def format_longitude(longitude):
    deg = int(abs(longitude))
    minutes = (abs(longitude) - deg) * 60
    direction = "E" if longitude >= 0 else "W"
    return f"{deg:03d}{minutes:05.2f}{direction}"

def generate_passcode(callsign):
    assert isinstance(callsign, str)
    callsign = callsign.split("-")[0].upper()
    code = 0x73E2
    for i, char in enumerate(callsign):
        code ^= ord(char) << (8 if i % 2 == 0 else 0)
    return code & 0x7FFF

if __name__ == "__main__":
    main()
