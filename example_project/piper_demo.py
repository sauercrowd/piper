import urllib3
from piper.piper_import import piper_import

def main():
    # First, let's check the version of urllib3 in our main environment
    print(f"Main environment urllib3 version: {urllib3.__version__}")

    # Now, let's import the old requests version installed by Piper
    requests_old = piper_import('requests_old')

    # Check the version of requests
    print(f"Piper-installed requests version: {requests_old.__version__}")

    # Now, let's check what version of urllib3 this old requests is using
    requests_old_urllib3 = requests_old.packages.urllib3
    print(f"urllib3 version used by Piper-installed requests: {requests_old_urllib3.__version__}")

    # Let's make a request using both versions to ensure they're working
    try:
        response_main = urllib3.request("GET", "http://example.com")
        print(f"Main urllib3 request successful: {response_main.status}")
    except Exception as e:
        print(f"Main urllib3 request failed: {e}")

    try:
        response_old = requests_old.get("http://example.com")
        print(f"Old requests request successful: {response_old.status_code}")
    except Exception as e:
        print(f"Old requests request failed: {e}")

if __name__ == "__main__":
    main()

