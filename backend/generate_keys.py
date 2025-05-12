from Crypto.PublicKey import RSA
import os

def generate_keypair(usn):
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    os.makedirs("keys", exist_ok=True)

    with open(f"keys/{usn}_private.pem", "wb") as prv_file:
        prv_file.write(private_key)

    with open(f"keys/{usn}_public.pem", "wb") as pub_file:
        pub_file.write(public_key)

    print(f"Keypair generated for USN: {usn}")

# Example usage
generate_keypair("4SF22CD023")  # Replace with real USNs
