import platform
import socket
import ipaddress
import re
import time
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Server Connectivity Check",
    page_icon="🌐",
    layout="centered",
)

st.title("🌐 Server Connectivity Check")
st.write(
    "Detect the runtime hostname and IP addresses, "
    "then test TCP connectivity to a target server."
)


# ==================================================
# LOCAL COMPUTER INFORMATION
# ==================================================

def get_local_info():
    hostname = platform.node() or socket.gethostname()
    ips = set()

    try:
        for result in socket.getaddrinfo(
            socket.gethostname(),
            None,
            family=socket.AF_INET,
        ):
            ip = result[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except socket.gaierror:
        pass

    # Include the default outbound interface IP when available.
    # UDP connect does not send application data.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 80))
            local_ip = s.getsockname()[0]
            if local_ip and not local_ip.startswith("127."):
                ips.add(local_ip)
    except OSError:
        pass

    return hostname, sorted(ips)


# ==================================================
# TARGET VALIDATION
# ==================================================

def validate_target(target):
    target = target.strip()

    if not target or len(target) > 253:
        return False

    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass

    hostname_pattern = (
        r"^(?=.{1,253}$)"
        r"(?:[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)"
        r"(?:\.(?:[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*\.?$"
    )

    return bool(re.fullmatch(hostname_pattern, target))


# ==================================================
# TCP CONNECTIVITY TEST
# ==================================================

def test_connection(target_server, target_port, timeout=5):
    start_time = time.perf_counter()
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    try:
        # Resolve hostname and establish TCP connection.
        with socket.create_connection(
            (target_server, target_port),
            timeout=timeout,
        ) as conn:
            remote_ip = conn.getpeername()[0]
            local_ip = conn.getsockname()[0]

        elapsed = (time.perf_counter() - start_time) * 1000

        return {
            "success": True,
            "target": target_server,
            "remote_ip": remote_ip,
            "port": target_port,
            "source_ip": local_ip,
            "duration_ms": round(elapsed, 2),
            "timestamp": timestamp,
            "message": "TCP connection established successfully.",
        }

    except socket.gaierror as exc:
        message = f"Hostname resolution failed: {exc}"

    except (socket.timeout, TimeoutError):
        message = f"Connection timed out after {timeout} seconds."

    except ConnectionRefusedError:
        message = "Connection refused. The port may not be listening."

    except OSError as exc:
        message = f"Network error: {exc}"

    elapsed = (time.perf_counter() - start_time) * 1000

    return {
        "success": False,
        "target": target_server,
        "remote_ip": "-",
        "port": target_port,
        "source_ip": "-",
        "duration_ms": round(elapsed, 2),
        "timestamp": timestamp,
        "message": message,
    }


# ==================================================
# DISPLAY RUNTIME INFORMATION
# ==================================================

hostname, local_ips = get_local_info()

st.subheader("1. Runtime Information")
st.caption(
    "These details belong to the machine running the Streamlit app, "
    "which may be a cloud server rather than your workstation."
)

st.metric("Runtime Hostname", hostname)

if local_ips:
    st.write("**Detected local IPv4 addresses:**")
    for ip in local_ips:
        st.code(ip, language=None)
else:
    st.info("No local IPv4 address could be detected.")


# ==================================================
# TARGET CONFIGURATION
# ==================================================

st.divider()
st.subheader("2. Target Server Configuration")

with st.form("connectivity_form"):
    col1, col2 = st.columns([3, 1])

    with col1:
        target_server = st.text_input(
            "Target Server IP / Hostname",
            value="192.168.21.14",
            placeholder="Example: 192.168.21.14",
        ).strip()

    with col2:
        target_port = st.number_input(
            "TCP Port",
            min_value=1,
            max_value=65535,
            value=5093,
            step=1,
        )

    timeout = st.slider(
        "Connection Timeout (seconds)",
        min_value=1,
        max_value=30,
        value=5,
    )

    submitted = st.form_submit_button(
        "Test TCP Connection",
        type="primary",
        use_container_width=True,
    )


# ==================================================
# RUN TEST
# ==================================================

if submitted:
    if not validate_target(target_server):
        st.error("Enter a valid IP address or hostname.")

    else:
        with st.spinner(
            f"Testing {target_server}:{int(target_port)}..."
        ):
            result = test_connection(
                target_server,
                int(target_port),
                timeout=int(timeout),
            )

        st.divider()
        st.subheader("3. Connection Test Results")

        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "TCP Status",
                "SUCCESS" if result["success"] else "FAILED",
            )
        with col2:
            st.metric(
                "Response Time",
                f'{result["duration_ms"]} ms',
            )

        st.write("**Detailed Results**")

        st.table(
            {
                "Property": [
                    "Test Time",
                    "Target Server",
                    "Resolved Remote IP",
                    "Target Port",
                    "Source IP",
                    "TCP Connection",
                    "Duration",
                    "Result",
                ],
                "Value": [
                    result["timestamp"],
                    result["target"],
                    result["remote_ip"],
                    result["port"],
                    result["source_ip"],
                    str(result["success"]),
                    f'{result["duration_ms"]} ms',
                    result["message"],
                ],
            }
        )

        st.caption(
            "The test is executed from the machine hosting Streamlit."
        )


st.divider()
st.caption(
    "Note: a successful TCP test confirms that a TCP connection "
    "could be established from the runtime to the specified target. "
    "It does not verify that the licensing application itself is functional."
)
