# Server-Connectivity-Check
# 🌐 Server Connectivity Check

A lightweight web application built with **Python and Streamlit** to display local computer information and test TCP connectivity to a target server using PowerShell `Test-NetConnection`.

The application allows users to enter a target server IP address or hostname and a custom TCP port, making it useful for checking network connectivity to services such as the Harmony License Server.

## ✨ Features

- **Local Computer Information** — Detects the computer hostname and available local IPv4 addresses.
- **Custom Server Input** — Enter a target server IP address or hostname.
- **Custom Port Input** — Specify any TCP port from `1` to `65535`.
- **TCP Connectivity Test** — Executes PowerShell `Test-NetConnection` against the specified target.
- **Connection Status** — Displays whether the TCP connection succeeds or fails.
- **PowerShell Output** — Shows connection details, including remote address, remote port, source address, and connection status.
- **Input Validation** — Validates the target IP address or hostname before testing.

## 🛠️ Technologies

- Python
- Streamlit
- Windows PowerShell
- PowerShell `Test-NetConnection`

## 📋 Requirements

- Python 3.10 or later recommended.
- Windows operating system for the machine executing the PowerShell commands.
- Network access to the target server.
- The target server must be reachable through the configured network and firewall rules.

## 📁 Project Structure

```text
server-connectivity-check/
├── app.py
├── requirements.txt
└── README.md
```

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/server-connectivity-check.git
```

Navigate to the project directory:

```bash
cd server-connectivity-check
```

### 2. Create a virtual environment (optional)

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your default browser. If it does not open automatically, navigate to:

```text
http://localhost:8501
```

## 📖 How to Use

1. Launch the Streamlit application.
2. Review the detected computer hostname and local IPv4 addresses.
3. Enter the target server IP address or hostname.
4. Enter the TCP port you want to test.
5. Click **Run Test-NetConnection**.
6. Review the PowerShell output and connection status.

### Example Configuration

| Parameter | Example |
|---|---|
| Target Server | `192.168.21.14` |
| Target Port | `5093` |
| Test Command | `Test-NetConnection` |
| Protocol | TCP |

### Example Result

**Successful connection**

```text
ComputerName     : 192.168.21.14
RemotePort       : 5093
TcpTestSucceeded : True
```

**Failed connection**

```text
ComputerName     : 192.168.21.14
RemotePort       : 5093
TcpTestSucceeded : False
```

These examples illustrate the expected output format. Actual results depend on the network environment.

## 🔧 Use Case: Harmony License Server

This application can help troubleshoot TCP connectivity between a workstation and a Harmony License Server.

For example, when checking port `5093`, a successful TCP test indicates that a TCP connection to the specified server and port could be established from the machine running the test.

If the test fails, possible causes include:

- Incorrect server IP address or hostname.
- Incorrect target port.
- Firewall rules blocking the connection.
- Network routing or connectivity issues.
- The target service is not listening on the specified port.

A successful TCP test does not necessarily confirm that the licensing application is fully functional. Additional checks may be required.

## ⚠️ Deployment Notes

**Important:** The application executes PowerShell commands on the machine running the Streamlit Python process.

- **Local Windows deployment:** PowerShell commands run on the local Windows computer.
- **Central server deployment:** PowerShell commands run on the central server, not automatically on the user's workstation.
- **Linux-based cloud deployment:** The Windows-specific commands `powershell.exe`, `Get-NetIPAddress`, and `Test-NetConnection` are not available by default.

If the objective is to test connectivity from individual workstations while displaying results on a central dashboard, a separate workstation-side execution mechanism is required.

Do not expose the application publicly without appropriate access controls, because it can be used to probe connectivity to user-specified server addresses and ports.

## 📄 License

Specify the license for this project before distributing or reusing the source code. For example, you may choose the MIT License if its terms suit your intended use.

---

**Developed with Python and Streamlit.**
