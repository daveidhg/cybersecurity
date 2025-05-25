import socket
import struct
import json
import threading

# Load spoofed domains and their IPs
with open('custom_domains.json') as f:
    custom_ips = json.load(f)


LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 53
GOOGLE_DNS = ('8.8.8.8', 53)

def parse_qname(data, offset):
    labels = []
    while True:
        length = data[offset]
        if length == 0:
            break
        labels.append(data[offset+1:offset+1+length].decode())
        offset += 1 + length
    return '.'.join(labels), offset + 1

def build_qname(domain):
    parts = domain.split('.')
    qname = b''
    for part in parts:
        qname += bytes([len(part)]) + part.encode()
    return qname + b'\x00'

def encode_https_params(params: dict) -> bytes:
    """
    Encode HTTPS RR parameters as length-prefixed key=value bytes.
    """
    encoded = b''
    for k, v in params.items():
        kv = f"{k}={v}".encode()
        encoded += bytes([len(kv)]) + kv
    return encoded

def build_https_rdata(priority: int, name: str, params: dict) -> bytes:
    """
    Build the RDATA field for HTTPS record.
    """
    rdata = struct.pack('!H', priority)  # priority: 2 bytes
    rdata += build_qname(name)            # encoded domain name
    rdata += encode_https_params(params)  # encoded params
    return rdata

def handle_request(data, addr, sock):
    try:
        transaction_id = data[:2]
        flags = data[2:4]
        qdcount = struct.unpack('!H', data[4:6])[0]

        offset = 12
        qname, offset = parse_qname(data, offset)
        qtype, qclass = struct.unpack('!HH', data[offset:offset+4])

        print(f"[+] Query: {qname} ({qtype}) from {addr}")

        qname_lower = qname.lower()
        response = None

        if qname_lower in custom_ips:
            record = custom_ips[qname_lower]

            if qtype == 1 and 'A' in record:
                # Build A record response
                ip = record['A']
                print(f"  ↳ Custom A IP: {ip}")

                flags = b'\x81\x80'  # Standard response, no error
                qdcount = b'\x00\x01'
                ancount = b'\x00\x01'
                nscount = arcount = b'\x00\x00'

                header = transaction_id + flags + qdcount + ancount + nscount + arcount
                question = data[12:offset+4]

                answer_name = b'\xc0\x0c'
                answer_type = b'\x00\x01'
                answer_class = b'\x00\x01'
                ttl = struct.pack('!I', 300)
                rdlength = struct.pack('!H', 4)
                rdata = socket.inet_aton(ip)

                answer = answer_name + answer_type + answer_class + ttl + rdlength + rdata
                response = header + question + answer

            elif qtype == 65 and 'HTTPS' in record:
                # Build HTTPS record response
                https_record = record['HTTPS']
                priority = https_record.get('priority', 1)
                name_target = https_record.get('name', '')
                params = https_record.get('params', {})

                print(f"  ↳ Custom HTTPS record: priority={priority} name={name_target} params={params}")

                flags = b'\x81\x80'  # Standard response, no error
                qdcount = b'\x00\x01'
                ancount = b'\x00\x01'
                nscount = arcount = b'\x00\x00'

                header = transaction_id + flags + qdcount + ancount + nscount + arcount
                question = data[12:offset+4]

                rdata = build_https_rdata(priority, name_target, params)
                rdlength = struct.pack('!H', len(rdata))

                answer_name = b'\xc0\x0c'
                answer_type = struct.pack('!H', 65)   # HTTPS type
                answer_class = b'\x00\x01'             # IN class
                ttl = struct.pack('!I', 300)

                answer = answer_name + answer_type + answer_class + ttl + rdlength + rdata
                response = header + question + answer

            else:
                # Custom domain but unsupported query type - respond with no answers
                print(f"  ↳ Custom domain: ignoring non-A/HTTPS type ({qtype})")

                flags = b'\x81\x80'  # Response with recursion available, no error
                qdcount = b'\x00\x01'
                ancount = nscount = arcount = b'\x00\x00'

                header = transaction_id + flags + qdcount + ancount + nscount + arcount
                question = data[12:offset+4]
                response = header + question

        else:
            # Forward all other queries to Google DNS
            forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            forward_sock.sendto(data, GOOGLE_DNS)
            response, _ = forward_sock.recvfrom(512)
            print("  ↳ Forwarded to Google DNS")

        if response:
            sock.sendto(response, addr)

    except Exception as e:
        print(f"[!] Error handling request from {addr}: {e}")


def start_dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"[+] DNS Server listening on {LISTEN_IP}:{LISTEN_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(512)
            threading.Thread(target=handle_request, args=(data, addr, sock), daemon=True).start()
        except ConnectionResetError:
            print("[-] Connection reset by peer (ignored).")
            continue
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            continue


if __name__ == '__main__':
    start_dns_server()
