from scapy.all import *

# Simulate a client logging into an internal HR portal over plain HTTP.
# The flag is embedded in a POST body, exactly as if a real credential
# had been sent in cleartext -- realistic and findable via "Follow TCP Stream".

client_ip = "10.10.14.22"
server_ip = "10.10.14.50"
client_port = 51234
server_port = 80

packets = []

# TCP handshake
syn = IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="S", seq=100)
syn_ack = IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="SA", seq=200, ack=101)
ack = IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="A", seq=101, ack=201)
packets += [syn, syn_ack, ack]

# HTTP POST request with the flag in the body, as if it were a leaked API key
http_body = "username=hr_admin&password=TempPass2026&api_key=CTF{p4ck3ts_never_lie}"
http_request = (
    "POST /internal/hr-portal/login HTTP/1.1\r\n"
    "Host: hr-internal.corp.local\r\n"
    "User-Agent: Mozilla/5.0\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    f"Content-Length: {len(http_body)}\r\n"
    "Connection: keep-alive\r\n"
    "\r\n"
    f"{http_body}"
)
push = IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="PA", seq=101, ack=201)/Raw(load=http_request)
packets.append(push)

server_ack = IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="A", seq=201, ack=101+len(http_request))
packets.append(server_ack)

# HTTP response
http_response_body = "Login successful. Redirecting..."
http_response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    f"Content-Length: {len(http_response_body)}\r\n"
    "Connection: keep-alive\r\n"
    "\r\n"
    f"{http_response_body}"
)
resp_push = IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="PA", seq=201, ack=101+len(http_request))/Raw(load=http_response)
packets.append(resp_push)

client_final_ack = IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="A", seq=101+len(http_request), ack=201+len(http_response))
packets.append(client_final_ack)

# FIN teardown
fin = IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="FA", seq=101+len(http_request), ack=201+len(http_response))
fin_ack = IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="FA", seq=201+len(http_response), ack=102+len(http_request))
last_ack = IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="A", seq=102+len(http_request), ack=202+len(http_response))
packets += [fin, fin_ack, last_ack]

# Add some decoy background noise -- a DNS query, unrelated to the flag
dns_query = IP(src=client_ip, dst="10.10.14.1")/UDP(sport=53211, dport=53)/DNS(rd=1, qd=DNSQR(qname="hr-internal.corp.local"))
dns_response = IP(src="10.10.14.1", dst=client_ip)/UDP(sport=53, dport=53211)/DNS(qr=1, aa=1, qd=DNSQR(qname="hr-internal.corp.local"), an=DNSRR(rrname="hr-internal.corp.local", ttl=300, rdata=server_ip))
packets = [dns_query, dns_response] + packets

wrpcap("traffic-capture.pcap", packets)
print("pcap written: traffic-capture.pcap")
print(f"Total packets: {len(packets)}")
