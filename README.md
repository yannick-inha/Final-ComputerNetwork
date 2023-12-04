# Final-ComputerNetwork

By Cyprien Yannick and Clement

**README for Multi-Client File Sharing Server**

This Python script implements a multi-client file-sharing server using sockets and threading. The server allows clients to connect, share various file types (CSV, PNG, JSON), and visualize PNG images in ASCII art. Below is a guide on how to use the server.

### Prerequisites
- Python 3.x
- Required Python packages: `PIL`, `tabulate`

### Getting Started

1. **Run the Server:**
   - Execute the script in your terminal:
     ```bash
     python essai.py
     ```
   - Enter the desired port when prompted.

2. **Server Menu:**
   - The server displays a menu with the following options:
     - `1. Send a message`: Choose a client to send a file (CSV, PNG, JSON).
     - `2. List connected clients`: Display connected clients.
     - `3. Wait for a connection`: Wait for a new client to connect.
     - `4. Share all sockets`: Not implemented.
     - `5. Exit`: Close all connections and exit the server.

3. **Sending Files:**
   - Choose a client index to send a file to.
   - Choose the file type (1 for CSV, 2 for PNG, 3 for JSON).
   - Follow the prompts to provide the file path.

4. **ASCII Art for PNG:**
   - If sending a PNG file, the server converts it to ASCII art for visualization.

5. **Exiting the Server:**
   - Select option `5` to gracefully exit the server.


### Example Usage:

1. Start the server:
   ```bash
   python essai.py
   ```
2. Choose option `3` to wait for a connection.
3. In a separate terminal, run a client script and connect to the server.
