import json
import os
import threading
import time

def criar_config_padrao():
    config = {
        "directories": ["dir_A", "dir_B", "dir_C"],
        "operations": [
            ["dir_A", "dir_B"], 
            ["dir_B", "dir_A"], 
            ["dir_A", "dir_C"]
        ],
        "threads": 2,
        "hold_time": 1.0,
        "timeout": 2.0
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    print("Arquivo config.json criado automaticamente!")
    return config


class Directory:
    def __init__(self, name):
        self.name = name
        self.lock = threading.Lock()


def operar(fs, seq, hold_time, timeout):
    acquired = []

    for d in seq:
        print(f"{threading.current_thread().name} tentando bloquear {d}...")

        ok = fs[d].lock.acquire(timeout=timeout)
        if not ok:
            print(f"{threading.current_thread().name} ERRO: timeout em {d} (deadlock detectado)")
            return

        print(f"{threading.current_thread().name} bloqueou {d}")
        acquired.append(fs[d])
        time.sleep(0.2)

    print(f"{threading.current_thread().name} operando em {seq}")
    time.sleep(hold_time)

    for d in reversed(acquired):
        d.lock.release()
        print(f"{threading.current_thread().name} liberou {d.name}")


def worker(fs, operations, hold_time, timeout):
    for seq in operations:
        operar(fs, seq, hold_time, timeout)
        time.sleep(0.5)

def main():
    if not os.path.exists("config.json"):
        config = criar_config_padrao()
    else:
        with open("config.json", "r") as f:
            config = json.load(f)
            print("config.json carregado!")

    fs = {name: Directory(name) for name in config["directories"]}

    threads = []
    for i in range(config["threads"]):
        t = threading.Thread(
            target=worker,
            name=f"Thread-{i+1}",
            args=(fs, config["operations"], config["hold_time"], config["timeout"])
        )
        threads.append(t)

    print("\n=== Iniciando simulação de deadlock ===\n")

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("\n=== Fim da simulação ===")


if __name__ == "__main__":
    main()
