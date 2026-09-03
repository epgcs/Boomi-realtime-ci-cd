import os
import json
import sys
import urllib.request
import urllib.error
import base64


def get_auth_headers(username, token):
    credentials = f"{username}:{token}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("utf-8")

    return {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def get_latest_package_version(account_id, process_id, username, token):

    url = (
        f"https://api.boomi.com/api/rest/v1/"
        f"{account_id}/PackagedComponent"
    )

    headers = get_auth_headers(username, token)

    payload = {
        "componentId": process_id
    }

    json_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=json_data,
        method="POST",
        headers=headers
    )

    print()
    print("Checking existing package version...")

    try:

        with urllib.request.urlopen(request, timeout=60) as response:

            response_body = response.read().decode("utf-8")

            if response.status != 200:
                print(f"ERROR: HTTP Status {response.status}")
                print(response_body)
                sys.exit(1)

            result = json.loads(response_body)

            package_version = result.get("packageVersion")
            package_id = result.get("packageId")
            component_id = result.get("componentId")

            if not package_version:
                print()
                print("ERROR: Boomi did not return packageVersion.")
                print()
                print("Boomi response:")
                print(json.dumps(result, indent=2))
                sys.exit(1)

            if component_id != process_id:
                print()
                print("ERROR: Returned package belongs to a different process.")
                print(f"Expected Process ID: {process_id}")
                print(f"Returned Component ID: {component_id}")
                sys.exit(1)

            print()
            print(f"✓ Current package ID: {package_id}")
            print(f"✓ Current package version: {package_version}")

            # --------------------------------------------------
            # Calculate next version
            # Example:
            # 1.0 -> 1.1
            # 1.1 -> 1.2
            # 4.0 -> 4.1
            # --------------------------------------------------

            try:

                version_parts = package_version.split(".")

                if len(version_parts) != 2:
                    raise ValueError(
                        f"Unsupported package version format: "
                        f"{package_version}"
                    )

                major = int(version_parts[0])
                minor = int(version_parts[1])

                next_version = f"{major}.{minor + 1}"

            except (ValueError, TypeError) as error:

                print()
                print("ERROR: Could not calculate next package version.")
                print(f"Current version: {package_version}")
                print(error)
                sys.exit(1)

            print(f"✓ Next package version: {next_version}")

            return next_version

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
            print("ERROR: Access denied.")
            print("Check Packaged Component permissions.")

        elif error.code == 404:

            print()
            print("ERROR: Boomi endpoint or account was not found.")

        else:

            print()
            print("ERROR: Unable to retrieve package information.")

        sys.exit(1)

    except urllib.error.URLError as error:

        print()
        print("ERROR: Could not connect to Boomi API.")
        print(error)
        sys.exit(1)

    except json.JSONDecodeError:

        print()
        print("ERROR: Boomi returned invalid JSON.")
        sys.exit(1)

    except Exception as error:

        print()
        print("ERROR while checking package version.")
        print(error)
        sys.exit(1)


def create_package(
    account_id,
    process_id,
    process_name,
    package_version,
    username,
    token
):

    url = (
        f"https://api.boomi.com/api/rest/v1/"
        f"{account_id}/PackagedComponent"
    )

    payload = {
        "componentId": process_id,
        "packageVersion": package_version,
        "notes": f"GitHub CI/CD package for {process_name}"
    }

    json_data = json.dumps(payload).encode("utf-8")

    headers = get_auth_headers(username, token)

    request = urllib.request.Request(
        url,
        data=json_data,
        method="POST",
        headers=headers
    )

    print()
    print("Creating Packaged Component...")
    print(f"Endpoint: {url}")
    print(f"Package Version: {package_version}")

    try:

        with urllib.request.urlopen(request, timeout=60) as response:

            response_body = response.read().decode("utf-8")

            print()
            print("======================================")
            print("Boomi API Response")
            print("======================================")

            print(f"HTTP Status: {response.status}")

            if response.status != 200:

                print("ERROR: Package creation failed.")
                print(response_body)
                sys.exit(1)

            try:

                result = json.loads(response_body)

            except json.JSONDecodeError:

                print("ERROR: Boomi returned unexpected response.")
                print(response_body)
                sys.exit(1)

            package_id = result.get("packageId")
            returned_version = result.get("packageVersion")

            if not package_id:

                print()
                print("ERROR: Boomi did not return Package ID.")
                print(response_body)
                sys.exit(1)

            print()
            print("✓ Packaged Component created successfully")
            print(f"Package ID: {package_id}")
            print(f"Package Version: {returned_version}")

            # --------------------------------------------------
            # Pass values to GitHub Actions
            # --------------------------------------------------

            github_output = os.getenv("GITHUB_OUTPUT")

            if not github_output:

                print()
                print("ERROR: GITHUB_OUTPUT is not available.")
                print("Cannot pass Package ID to deployment step.")
                sys.exit(1)

            with open(github_output, "a") as output_file:

                output_file.write(
                    f"package_id={package_id}\n"
                )

                output_file.write(
                    f"package_version={returned_version}\n"
                )

            print()
            print("✓ Package ID exported to GitHub Actions")
            print("✓ Package version exported to GitHub Actions")

            print()
            print("PACKAGE CREATION SUCCESSFUL")

            return package_id, returned_version

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

        if error.code == 400:

            print()
            print("ERROR: Invalid PackagedComponent request.")

        elif error.code == 401:

            print()
            print("ERROR: Authentication failed.")

        elif error.code == 403:

            print()
            print("ERROR: Access denied.")
            print(
                "The API user may not have "
                "Packaged Component Management permission."
            )

        elif error.code == 404:

            print()
            print("ERROR: Boomi endpoint or account was not found.")

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


def main():

    print("======================================")
    print("Boomi CI/CD - Package Component")
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
    # 2. Read BETA configuration
    # --------------------------------------------------

    config_file = "config/beta.json"

    try:

        with open(config_file, "r") as file:
            config = json.load(file)

    except FileNotFoundError:

        print(
            f"ERROR: Configuration file not found: {config_file}"
        )
        sys.exit(1)

    except json.JSONDecodeError:

        print(
            f"ERROR: Invalid JSON in {config_file}"
        )
        sys.exit(1)

    process_name = config.get("process_name")
    process_id = config.get("process_id")

    if not process_id or process_id.startswith("YOUR_"):

        print("ERROR: Process ID is not configured")
        sys.exit(1)

    print(f"✓ Process: {process_name}")
    print(f"✓ Process ID: {process_id}")

    # --------------------------------------------------
    # 3. Get latest package version
    # --------------------------------------------------

    next_version = get_latest_package_version(
        account_id,
        process_id,
        username,
        token
    )

    # --------------------------------------------------
    # 4. Create new package
    # --------------------------------------------------

    create_package(
        account_id,
        process_id,
        process_name,
        next_version,
        username,
        token
    )


if __name__ == "__main__":
    main()
