import socket
import threading
import struct

from des import encrypt_message, decrypt_message


SERVER_IP = "192.168.8.128"
PORT = 5050

KEY = b"KunciDES67"

running = True



def send_message(sock, message):


    ciphertext = encrypt_message(
        message,
        KEY
    )

    print("\nPlaintext:")
    print(message)

    print("\nCiphertext:")
    print(ciphertext.hex())


    header = struct.pack(
        "!I",
        len(ciphertext)
    )

    sock.sendall(
        header + ciphertext
    )

    print("\nCiphertext berhasil dikirim!")


def receive_exact(sock, size):

    data = b""

    while len(data) < size:

        chunk = sock.recv(
            size - len(data)
        )

        if not chunk:
            return None

        data += chunk

    return data


def receive_message(sock):

    header = receive_exact(
        sock,
        4
    )

    if header is None:
        return None

    message_length = struct.unpack(
        "!I",
        header
    )[0]

    ciphertext = receive_exact(
        sock,
        message_length
    )

    if ciphertext is None:
        return None

    plaintext = decrypt_message(
        ciphertext,
        KEY
    )

    return plaintext



def receive_loop(sock):

    global running

    while running:

        try:

            message = receive_message(sock)

            if message is None:

                print("\n[!] Koneksi ditutup oleh Ubuntu.")

                running = False

                break

            if message == "/exit":

                print("\n[Ubuntu] keluar dari chat.")

                running = False

                break

            print(f"\n[Ubuntu] {message}")
            print("Anda: ", end="", flush=True)

        except Exception as error:

            print("\n[!] Error menerima pesan:", error)

            running = False

            break


# MAINN PROGRAM

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

print("Menghubungkan ke Ubuntu...")

client.connect(
    (SERVER_IP, PORT)
)

print("Terhubung ke Ubuntu.")
print("Ketik /exit untuk keluar.\n")


receive_thread = threading.Thread(
    target=receive_loop,
    args=(client,),
    daemon=True
)

receive_thread.start()


while running:

    try:

        message = input("Anda: ")

        if not running:
            break

        send_message(
            client,
            message
        )

        if message == "/exit":

            running = False
            break

    except KeyboardInterrupt:

        running = False
        break

    except Exception as error:

        print("\n[!] Error mengirim pesan:", error)

        running = False
        break


try:
    client.close()
except:
    pass

print("\nChat ditutup.")