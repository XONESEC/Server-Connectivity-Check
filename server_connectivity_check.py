
import platform
import socket
import subprocess
import streamlit as st
import ipaddress
import re

st.set_page_config(
    page_title="Server Connectivity Check",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 Server Connectivity Check")
st.write(
    "Deteksi nama komputer dan alamat IP lokal, "
    "lalu uji koneksi TCP ke server tujuan."
)


# ==================================================
# DETEKSI INFORMASI KOMPUTER LOKAL
# ==================================================

def get_local_info():
    server_name = platform.node() or socket.gethostname()
    ips = set()

    ps_command = (
        "Get-NetIPAddress -AddressFamily IPv4 "
        "| Where-Object { $_.IPAddress -ne '127.0.0.1' "
        "-and $_.AddressState -eq 'Preferred' } "
        "| Select-Object -ExpandProperty IPAddress"
    )

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps_command
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False
        )

        if result.returncode == 0:
            ips.update(
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip()
            )
        else:
            st.warning(
                "PowerShell tidak dapat mengambil daftar IP. "
                "Mencoba metode alternatif."
            )

    except (FileNotFoundError, subprocess.TimeoutExpired):
        st.warning(
            "PowerShell tidak tersedia atau deteksi IP timeout."
        )

    # Fallback jika PowerShell gagal
    if not ips:
        try:
            ips.update(
                ip for ip in socket.gethostbyname_ex(
                    socket.gethostname()
                )[2]
                if ip and not ip.startswith("127.")
            )
        except socket.gaierror:
            pass

    return server_name, sorted(ips)


# ==================================================
# VALIDASI TARGET SERVER
# ==================================================

def validate_target(target):
    target = target.strip()

    if not target:
        return False

    # Mendukung alamat IPv4
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass

    # Mendukung hostname atau FQDN
    if len(target) > 253:
        return False

    hostname_pattern = (
        r"^(?=.{1,253}$)"
        r"(?:[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)"
        r"(?:\.(?:[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*\.?$"
    )

    return bool(re.fullmatch(hostname_pattern, target))


# ==================================================
# TEST KONEKSI TCP
# ==================================================

def test_connection(target_server, target_port):
    # Escape tanda kutip tunggal untuk PowerShell
    safe_server = target_server.replace("'", "''")

    ps_command = (
        f"$r = Test-NetConnection "
        f"-ComputerName '{safe_server}' "
        f"-Port {target_port} "
        "-WarningAction SilentlyContinue; "
        "$r | Select-Object ComputerName,RemoteAddress,"
        "RemotePort,InterfaceAlias,SourceAddress,"
        "TcpTestSucceeded | Format-List"
    )

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps_command
            ],
            capture_output=True,
            text=True,
            timeout=35,
            check=False
        )

        return (
            result.stdout.strip(),
            result.stderr.strip(),
            result.returncode
        )

    except FileNotFoundError:
        return (
            "",
            "PowerShell tidak ditemukan. "
            "Jalankan aplikasi di Windows.",
            1
        )

    except subprocess.TimeoutExpired:
        return (
            "",
            "Pemeriksaan koneksi melebihi batas waktu 35 detik.",
            1
        )


# ==================================================
# INFORMASI KOMPUTER
# ==================================================

server_name, local_ips = get_local_info()

st.subheader("1. Informasi Komputer Lokal")

st.metric("Computer Name / Hostname", server_name)

if local_ips:
    st.write("**IP address lokal yang terdeteksi:**")

    for ip in local_ips:
        st.code(ip, language=None)
else:
    st.warning("Alamat IP lokal tidak berhasil dideteksi.")


# ==================================================
# INPUT SERVER DAN PORT
# ==================================================

st.divider()
st.subheader("2. Konfigurasi Target Server")

col1, col2 = st.columns([3, 1])

with col1:
    target_server = st.text_input(
        "Target Server IP / Hostname",
        value="192.168.21.14",
        placeholder="Contoh: 192.168.21.14",
        help="Masukkan alamat IP atau hostname server."
    ).strip()

with col2:
    target_port = st.number_input(
        "Target Port",
        min_value=1,
        max_value=65535,
        value=5093,
        step=1,
        help="Port TCP yang ingin diperiksa."
    )

st.info(
    f"Target pengujian: {target_server or '-'}:{int(target_port)}"
)


# ==================================================
# EKSEKUSI TEST-NETCONNECTION
# ==================================================

if st.button(
    "Jalankan Test-NetConnection",
    type="primary",
    use_container_width=True
):
    if not validate_target(target_server):
        st.error(
            "Masukkan alamat IPv4 atau hostname server yang valid."
        )

    else:
        with st.spinner(
            f"Menguji koneksi ke "
            f"{target_server}:{int(target_port)}..."
        ):
            stdout, stderr, returncode = test_connection(
                target_server,
                int(target_port)
            )

        st.subheader("3. Hasil Pengujian")

        if stdout:
            st.text_area(
                "Hasil PowerShell",
                value=stdout,
                height=240
            )

            if "TcpTestSucceeded : True" in stdout:
                st.success(
                    f"Koneksi TCP ke {target_server}:"
                    f"{int(target_port)} berhasil."
                )

            elif "TcpTestSucceeded : False" in stdout:
                st.error(
                    f"Koneksi TCP ke {target_server}:"
                    f"{int(target_port)} gagal."
                )

            else:
                st.info(
                    "Perintah selesai. "
                    "Periksa hasil PowerShell di atas."
                )

        if stderr:
            st.warning(stderr)

        if not stdout and not stderr:
            st.error(
                "Perintah tidak menghasilkan output "
                f"(exit code: {returncode})."
            )


# ==================================================
# CATATAN
# ==================================================

st.caption(
    "Catatan: jalankan aplikasi pada komputer Windows "
    "yang ingin diuji. Informasi IP lokal dan hasil "
    "Test-NetConnection berasal dari komputer tempat "
    "proses Streamlit berjalan."
)
