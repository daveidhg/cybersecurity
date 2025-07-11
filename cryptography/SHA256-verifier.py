from hashlib import sha256
import argparse

def get_sha256_hash(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks to avoid memory issues with large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_sha256(file_path, expected_hash):
    """Verify the SHA-256 hash of a file against an expected hash."""
    actual_hash = get_sha256_hash(file_path)
    if actual_hash == expected_hash:
        print(f"SHA-256 hash matches: {actual_hash}")
    else:
        print(f"SHA-256 hash does not match: {actual_hash} (expected: {expected_hash})")

def main():
    parser = argparse.ArgumentParser(description='Verify the SHA-256 hash of a file.')
    parser.add_argument('-f', '--file', help='Path to the file to verify')
    parser.add_argument('-H', '--hash', help='Expected SHA-256 hash to verify against')
    args = parser.parse_args()

    if not args.file or not args.hash:
        parser.error('Both file and hash arguments are required.')
    verify_sha256(args.file, args.hash)

if __name__ == "__main__":
    main()