import grpc
from concurrent import futures
import time
import base64
import io
from PIL import Image
import lab6_pb2
import lab6_pb2_grpc

# gRPC runs on port 5001 to avoid conflict with REST server
GRPC_SERVER_PORT = 5001

# The implementation of the service methods
class Lab6Servicer(lab6_pb2_grpc.Lab6Servicer):

    def Add(self, request, context):
        """Handles the lightweight Add operation."""
        result = request.a + request.b
        return lab6_pb2.AddReply(sum=result)

    def GetRawImageInfo(self, request, context):
        """Processes raw binary image data (bytes type)."""
        try:
            ioBuffer = io.BytesIO(request.img)
            img = Image.open(ioBuffer)
            width, height = img.size
        except Exception:
            # Return 0, 0 on error
            width, height = 0, 0
            
        return lab6_pb2.ImageReply(width=width, height=height)

    def DotProduct(self, request, context):
        """Calculates the dot product of two vectors (repeated float types)."""
        vector_a = request.a
        vector_b = request.b
        
        if len(vector_a) != len(vector_b):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Vectors must be of the same length")
            
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        
        return lab6_pb2.DotProductReply(dotproduct=dot_product)

    def GetJsonImageInfo(self, request, context):
        """Processes Base64 encoded image data (string type)."""
        try:
            # 1. Decode the Base64 string back to binary data
            binary_image_data = base64.b64decode(request.img)
            
            # 2. Convert the data stream to a PIL image
            ioBuffer = io.BytesIO(binary_image_data)
            img = Image.open(ioBuffer)

            width, height = img.size
        except Exception:
            # Return 0, 0 on error
            width, height = 0, 0
            
        return lab6_pb2.ImageReply(width=width, height=height)

def serve():
    # Use a thread pool executor for non-blocking server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Add the servicer class to the server
    lab6_pb2_grpc.add_Lab6Servicer_to_server(Lab6Servicer(), server)
    
    # Listen on all interfaces on port 5001
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    
    print(f"gRPC Server starting on port {GRPC_SERVER_PORT}...")
    server.start()
    
    try:
        # Keep the server running
        while True:
            time.sleep(86400) # Sleep for one day
    except KeyboardInterrupt:
        server.stop(0)
        print("gRPC Server stopped.")

if __name__ == '__main__':
    serve()

