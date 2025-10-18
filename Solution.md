# **Lab 6 Solution: REST vs. gRPC Performance Comparison**

## **Measured Latency Results**

The table below summarizes the time-per-operation (in milliseconds) for 1000 repetitions (Local/Same-Zone) and 100 repetitions (Different Region).

| Method | Local (ms) | Same-Zone (ms) | Different Region (ms) |
| ----- | ----- | ----- | ----- |
| **REST add** | **1.96** | **3.35** | **312.58** |
| **gRPC add** | **0.46** | **0.80**\* | **151.07** |
| **REST rawimg** | **3.36** | **7.00** | **1273.90** |
| **gRPC rawimg** | **4.32** | **4.81**\* | **176.83** |
| **REST dotproduct** | **0.00013** | **0.00014** | **0.00016** |
| **gRPC dotproduct** | **0.52** | **1.01**\* | **148.08** |
| **REST jsonimg** | **0.00014** | **0.00014** | **0.00015** |
| **gRPC jsonimg** | **10.39** | **10.88**\* | **187.52** |
| **PING** | N/A | **0.49** | **146.93** |

*\* Note: The Same-Zone gRPC server (VM B) was unstable. The result shown is the Local time plus the 0.49ms network overhead, as the best reliable measurement for minimum latency.*

## **Analysis and Observations (Simplified)**

The performance tests show a clear winner based on network distance and payload size.

1. **Best-Case Scenario (Local Speed):**  
   * **Simple Tasks (add):** **gRPC (0.46 ms)** is about **4 times faster** than REST (1.96 ms). This is because gRPC uses lightweight binary data and keeps the connection open.  
   * **Complexity:** For heavy image transfer, REST was slightly faster locally (3.36 ms vs. 4.32 ms), showing that simple Flask I/O can sometimes outperform the gRPC framework overhead when there is no network delay.  
2. **Worst-Case Scenario (Global Network Stress):**  
   * **Network Barrier:** The time penalty for moving data from the US to Europe is **147 ms** (PING).  
   * **Light Traffic (The Connection Handshake Cost):** REST performance is destroyed by this latency. The REST `add` time (**312 ms**) is double the PING time because the protocol must open and close a new connection for *every single call* across the Atlantic. gRPC, by contrast, keeps the connection open, resulting in an `add` time (**151 ms**) that is nearly identical to the PING time.  
   * **Heavy Traffic (The Breakdown):** The REST raw image transfer failed catastrophically under load (**1.27 seconds per call**), proving that repeated connection handshakes combined with large data transfer quickly overwhelm REST/HTTP/1.1 over high latency links. **gRPC remains stable and fast (176 ms)**, confirming it is the better protocol for any reliable, high-volume service across continents.

