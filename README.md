# HTTP Request Smuggling Tester

A Python security testing tool for detecting potential HTTP request smuggling vulnerabilities.

# Overview

This modular testing tool sends HTTP requests with conflicting Content-Length and Transfer-Encoding headers to detect potential request smuggling vulnerabilities. It supports both HTTP and HTTPS protocols and uses multiprocessing for efficient parallel testing.

# Features

Parallel Processing: Utilizes multiprocessing to test multiple hosts simultaneously
SSL/TLS Support: Tests HTTPS endpoints with SSL socket connections
HTTP Testing: Tests HTTP endpoints (port 80)
Response Analysis: Detects multiple HTTP status codes in responses (indicative of smuggling)
Cache Busting: Generates random cache buster parameters to avoid cached responses
Robust Error Handling: Handles various network exceptions gracefully
Progress Tracking: Real-time console output of testing progress
Configurable I/O: Custom input and output file paths
# Requirements

Python 3.x
Standard library modules (no external dependencies required):
argparse
multiprocessing
random
re
socket
ssl
string
time
itertools
Installation

No installation required beyond Python 3. Simply clone or download the script:

git clone <repository-url>
cd <repository-directory>

# Usage

Basic Usage

python3 smuggling_tester_modular.py --input <input_file>

With Custom Output File

python3 smuggling_tester_modular.py --input hosts.txt --output results.txt

Command-Line Arguments

Argument	Short	Required	Default	Description
--input	-i	Yes	-	Path to input file containing target hosts
--output	-o	No	output	Path to output file for results
Input File Format

Create a text file with one hostname per line (no protocol prefix):

example.com
test.example.org
api.website.net

Output File Format

The output file contains results in the format:

example.com/?cache_buster=abc12 200
test.example.org/?cache_buster=abc12 404
api.website.net/?cache_buster=abc12 multiple status codes in response

Status code 000 indicates no valid HTTP response was detected.

# How It Works

Testing Methodology

Base Request: Sends a normal HTTP/HTTPS GET request to each host
Modified Requests: Sends 20 crafted requests per host with:
Conflicting Content-Length and Transfer-Encoding headers
Cache buster parameters to avoid caching
Smuggled request in the body
Request Smuggling Payload

The tool sends a POST request with conflicting headers:

POST / HTTP/1.1
Host: target.com
Content-Length: 55
Transfer-Encoding: chunked
Content-Type: application/x-www-form-urlencoded
Connection: keep-alive

1
A
0

GET / HTTP/1.1
Host: attacker-test.test


This payload attempts to smuggle a second GET request after the chunked body.

Detection Logic

The tool detects potential vulnerabilities by:

Searching for multiple HTTP status codes in a single response
Analyzing response patterns that indicate request desynchronization
Logging all response status codes for manual review
Architecture

# Key Functions

checkArguments(): Parses command-line arguments
get_hosts(): Reads target hosts from input file
make_socket_ssl_request(): Sends HTTPS requests (port 443)
make_socket_request(): Sends HTTP smuggling requests (port 80)
listener(): Async process that writes results to output file
Multiprocessing Design

Uses Python's multiprocessing.Pool for parallel execution
CPU count determines the number of worker processes
Queue-based communication between workers and listener process
Graceful shutdown with 'kill' signal
Performance

The tool automatically scales to your CPU core count, testing multiple hosts in parallel. Execution time depends on:

Number of target hosts
Network latency
Server response times
Number of CPU cores
Example output:

Execution time: 45.23 seconds

# Error Handling

The tool handles various network errors:

GAI Error: DNS resolution failures
SSL Error: SSL/TLS handshake failures
Timeout Error: Connection or socket timeouts
Connection Refused: Target not accepting connections
Connection Reset: Connection dropped by target
Unicode Decode Error: Non-UTF8 response content
Errors are logged to console with the affected hostname.

