import grpc
import time
import sys
import random
import base64
import os
from time import perf_counter

# Import generated code
import lab6_pb2
import lab6_pb2_grpc

# --- Configuration ---
GRPC_SERVER_PORT = 5001
FLATIRONS_IMAGE_PATH = "Flatirons_Winter_Sunrise_edit_2.jpg"

# --- Client Functions ---

def client_add(stub, debug=False):
    """Client for the Add service."""
    response = stub.Add(lab6_pb2.AddMsg(a=5, b=10))
    if debug:
        print(f"Add Result: {response.sum}")
    return response

def client_raw_image(stub, debug=False):
    """Client for the rawImage service (sends binary bytes)."""
    try:
        with open(FLATIRONS_IMAGE_PATH, 'rb') as image_file:
            img_data = image_file.read()
    except FileNotFoundError:
        print(f"Error: Image file not found at {FLATIRONS_IMAGE_PATH}")
        return None

    response = stub.GetRawImageInfo(lab6_pb2.RawImageMsg(img=img_data))
    if debug:
        print(f"Raw Image Result: Width={response.width}, Height={response.height}")
    return response

def client_dot_product(stub, debug=False):
    """Client for the DotProduct service."""
    # Generate two 100-element vectors with floats between 0 and 1
    vector_len = 100
    a = [random.random() for _ in range(vector_len)]
    b = [random.random() for _ in range(vector_len)]

    response = stub.DotProduct(lab6_pb2.DotProductMsg(a=a, b=b))
    if debug:
        print(f"Dot Product Result: {response.dotproduct:.4f}")
    return response

def client_json_image(stub, debug=False):
    """Client for the jsonImage service (sends Base64 string)."""
    try:
        with open(FLATIRONS_IMAGE_PATH, 'rb') as image_file:
            binary_image_data = image_file.read()
    except FileNotFoundError:
        print(f"Error: Image file not found at {FLATIRONS_IMAGE_PATH}")
        return None
        
    # Base64 encode the binary data to a string for transmission
    encoded_string = base64.b64encode(binary_image_data).decode('utf-8')

    response = stub.GetJsonImageInfo(lab6_pb2.JsonImageMsg(img=encoded_string))
    if debug:
        print(f"JSON Image Result: Width={response.width}, Height={response.height}")
    return response

# Mapping endpoints to their client functions
CLIENT_FUNCTIONS = {
    'add': client_add,
    'rawimage': client_raw_image,
    'dotproduct': client_dot_product,
    'jsonimage': client_json_image
}

# --- Main Logic ---

def run_tests(host, endpoint, iterations):
    """Establishes gRPC connection and runs the performance test loop."""
    addr = f'{host}:{GRPC_SERVER_PORT}'
    print(f"Running {iterations} reps against {addr} for {endpoint}")
    
    # Establish channel (gRPC uses a persistent connection)
    channel = grpc.insecure_channel(addr)
    stub = lab6_pb2_grpc.Lab6Stub(channel)
    client_func = CLIENT_FUNCTIONS[endpoint]

    # Run once to ensure function works (optional warm-up/debug)
    initial_result = client_func(stub, debug=False)
    if initial_result is None:
        print("Initial test failed. Aborting measurement.")
        return

    # Start the timer
    start_time = perf_counter()

    # Loop the test
    for _ in range(iterations):
        client_func(stub)

    # Stop the timer
    end_time = perf_counter()

    # Calculate time metrics
    total_time_s = end_time - start_time
    time_per_query_ms = (total_time_s / iterations) * 1000

    print("\n--- Results ---")
    print(f"Total time for {iterations} queries: {total_time_s:.4f} seconds")
    print(f"Time per query: {time_per_query_ms:.4f} milliseconds")
    print("---------------")

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <server ip> <cmd> <reps>")
        print(f"where <cmd> is one of {list(CLIENT_FUNCTIONS.keys())}")
        sys.exit(1)

    host = sys.argv[1]
    cmd = sys.argv[2].lower()
    
    try:
        reps = int(sys.argv[3])
    except ValueError:
        print("Error: Repetitions must be an integer.")
        sys.exit(1)

    if cmd not in CLIENT_FUNCTIONS:
        print(f"Unknown option '{cmd}'. Available: {list(CLIENT_FUNCTIONS.keys())}")
        sys.exit(1)

    # Handle special case for localhost vs. internal IP
    if host == 'localhost':
        host = '127.0.0.1'

    run_tests(host, cmd, reps)

if __name__ == '__main__':
    main()
