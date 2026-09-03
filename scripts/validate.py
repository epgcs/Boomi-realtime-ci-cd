
import os
import json
import sys
import urllib.request
import urllib.error
import base64


def main():
    print("======================================")
    print("Boomi CI/CD - Validation")
    print("======================================")

    # --------------------------------------------------
    # 1. Read GitHub Secrets
    # --------------------------------------------------

    account_id = os.getenv("BOOMI_ACCOUNT_ID")
    username = os.getenv("BOOMI_API_USERNAME")
    token = os.getenv("BOOMI_API_TOKEN")

    if not account_id:
        print("ERROR: BOOMI_ACCOUNT_ID is not configured")
        sys.exit(1)

    if not username:
        print("ERROR: BOOMI_API_USERNAME is not configured")
        sys.exit(1)

    if not token:
        print("ERROR: BOOMI_API_TOKEN is not configured")
        sys.exit(1)

    print("✓ Boomi Account ID found")
    print("✓ Boomi API Username found")
    print("✓ Boomi API Token found")

    # --------------------------------------------------
    # 2. Read Beta configuration
    # --------------------------------------------------

    config_file = "config/beta.json"

    try:
        with open(config_file, "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found: {config_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in {config_file}")
        sys.exit(1)

    environment_id = config.get("environment_id")
    process_name = config.get("process_name")
    process_id = config.get("process_id")

    if not environment_id or environment_id.startswith("YOUR_"):
        print("ERROR: Beta environment_id is not configured")
        sys.exit(1)

    if not process_id or process_id.startswith("YOUR_"):
        print("ERROR: Process ID is not configured")
        sys.exit(1)

    print(f"✓ Environment: {config.get('environment')}")
    print(f"✓ Process: {process_name}")
    print(f"✓ Process ID: {process_id}")

    # --------------------------------------------------
    # 3. Call Boomi Component API
    # --------------------------------------------------

    url = (
        f"https://api.boomi.com/api/rest/v1/"
        f"{account_id}/Component/{process_id}"
    )

    print()
    print("Calling Boomi API...")
    print(f"Endpoint: {url}")

    credentials = f"{username}:{token}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("utf-8")

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/xml"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_body = response.read().decode("utf-8")

            print()
            print("======================================")
            print("Boomi API Response")
            print("======================================")
            print(f"HTTP Status: {response.status}")

            if response.status == 200:
                print("✓ Successfully connected to Boomi")
                print("✓ Process was successfully retrieved")
                print()
                print("VALIDATION SUCCESSFUL")
                sys.exit(0)

    except urllib.error.HTTPError as error:
        print()
        print("======================================")
        print("Boomi API Error")
        print("======================================")

        print(f"HTTP Status: {error.code}")

        try:
            error_body = error.read().decode("utf-8")
            print()
            print("Boomi Response:")
            print(error_body)
        except Exception:
            print("Could not read Boomi error response.")

        if error.code == 401:
            print()
            print("ERROR: Authentication failed.")

        elif error.code == 403:
            print()
            print("ERROR: Boomi rejected the request.")
            print("Check API token authentication and account authorization.")

        elif error.code == 404:
            print()
            print("ERROR: Component or endpoint not found.")

        else:
            print()
            print("ERROR: Boomi API request failed.")

        sys.exit(1)

    except urllib.error.URLError as error:
        print()
        print("ERROR: Could not connect to Boomi API.")
        print(error)
        sys.exit(1)

    except Exception as error:
        print()
        print("ERROR: Unexpected error occurred.")
        print(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
