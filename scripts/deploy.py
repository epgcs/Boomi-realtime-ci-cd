import os
import json
import sys
import urllib.request
import urllib.error
import base64
import time


def get_auth_headers(username, token):

    credentials = f"{username}:{token}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("utf-8")

    return {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def verify_deployment(
    account_id,
    deployment_id,
    package_id,
    package_version,
    environment_id,
    process_id,
    username,
    token
):

    url = (
        f"https://api.boomi.com/api/rest/v1/"
        f"{account_id}/DeployedPackage/{deployment_id}"
    )

    headers = get_auth_headers(username, token)

    request = urllib.request.Request(
        url,
        method="GET",
        headers=headers
    )

    print()
    print("======================================")
    print("Boomi Deployment Verification")
    print("======================================")

    print(f"Deployment ID: {deployment_id}")
    print(f"Endpoint: {url}")

    # --------------------------------------------------
    # Retry verification
    #
    # Sometimes the deployment response is returned
    # before the deployment status is fully available.
    # --------------------------------------------------

    max_attempts = 5
    wait_seconds = 5

    for attempt in range(1, max_attempts + 1):

        print()
        print(
            f"Verification attempt "
            f"{attempt}/{max_attempts}..."
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                response_body = response.read().decode("utf-8")

                print(f"HTTP Status: {response.status}")

                if response.status != 200:

                    print(
                        "ERROR: Deployment verification "
                        "returned unexpected HTTP status."
                    )

                    if attempt < max_attempts:
                        time.sleep(wait_seconds)
                        continue

                    return False

                try:

                    result = json.loads(response_body)

                except json.JSONDecodeError:

                    print(
                        "ERROR: Boomi returned invalid JSON "
                        "during verification."
                    )

                    if attempt < max_attempts:
                        time.sleep(wait_seconds)
                        continue

                    return False

                # --------------------------------------------------
                # Read deployment information
                # --------------------------------------------------

                verified_package_id = result.get("packageId")
                verified_package_version = result.get("packageVersion")
                verified_environment_id = result.get("environmentId")
                verified_component_id = result.get("componentId")
                active = result.get("active")
                verified_deployment_id = result.get("deploymentId")

                print()
                print("Verification Response:")
                print(
                    json.dumps(
                        result,
                        indent=2
                    )
                )

                # --------------------------------------------------
                # Verify Deployment ID
                # --------------------------------------------------

                if verified_deployment_id != deployment_id:

                    print()
                    print("❌ Deployment ID verification failed.")
                    print(
                        f"Expected: {deployment_id}"
                    )
                    print(
                        f"Received: {verified_deployment_id}"
                    )

                    return False

                print()
                print("✓ Deployment ID verified")

                # --------------------------------------------------
                # Verify Package ID
                # --------------------------------------------------

                if verified_package_id != package_id:

                    print()
                    print("❌ Package ID verification failed.")
                    print(
                        f"Expected: {package_id}"
                    )
                    print(
                        f"Received: {verified_package_id}"
                    )

                    return False

                print("✓ Package ID verified")

                # --------------------------------------------------
                # Verify Package Version
                # --------------------------------------------------

                if (
                    package_version
                    and verified_package_version != package_version
                ):

                    print()
                    print(
                        "❌ Package version verification failed."
                    )

                    print(
                        f"Expected: {package_version}"
                    )

                    print(
                        f"Received: {verified_package_version}"
                    )

                    return False

                print("✓ Package version verified")

                # --------------------------------------------------
                # Verify Environment
                # --------------------------------------------------

                if verified_environment_id != environment_id:

                    print()
                    print(
                        "❌ Environment verification failed."
                    )

                    print(
                        f"Expected: {environment_id}"
                    )

                    print(
                        f"Received: {verified_environment_id}"
                    )

                    return False

                print("✓ Environment verified")

                # --------------------------------------------------
                # Verify Process
                # --------------------------------------------------

                if verified_component_id != process_id:

                    print()
                    print(
                        "❌ Process verification failed."
                    )

                    print(
                        f"Expected: {process_id}"
                    )

                    print(
                        f"Received: {verified_component_id}"
                    )

                    return False

                print("✓ Process verified")

                # --------------------------------------------------
                # Verify ACTIVE status
                # --------------------------------------------------

                if active is True:

                    print()
                    print("✓ Deployment is ACTIVE")

                    print()
                    print(
                        "======================================"
                    )
                    print(
                        "DEPLOYMENT VERIFICATION SUCCESSFUL"
                    )
                    print(
                        "======================================"
                    )

                    return True

                elif active is False:

                    print()
                    print(
                        "⚠ Deployment exists but is not "
                        "currently ACTIVE."
                    )

                    if attempt < max_attempts:

                        print(
                            f"Waiting {wait_seconds} seconds "
                            "before checking again..."
                        )

                        time.sleep(wait_seconds)
                        continue

                    print()
                    print(
                        "❌ Deployment verification failed."
                    )

                    print(
                        "Package is not active after "
                        f"{max_attempts} attempts."
                    )

                    return False

                else:

                    print()
                    print(
                        "⚠ Boomi did not return a valid "
                        "'active' value."
                    )

                    if attempt < max_attempts:

                        time.sleep(wait_seconds)
                        continue

                    return False

        except urllib.error.HTTPError as error:

            print()
            print(
                f"Verification HTTP Error: {error.code}"
            )

            try:

                error_body = (
                    error.read()
                    .decode("utf-8")
                )

                print()
                print("Boomi Response:")
                print(error_body)

            except Exception:

                print(
                    "Could not read verification error."
                )

            if error.code == 404:

                if attempt < max_attempts:

                    print(
                        "Deployment record not available yet."
                    )

                    print(
                        f"Waiting {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)
                    continue

                print()
                print(
                    "❌ Deployment verification failed."
                )

                return False

            elif error.code == 401:

                print()
                print(
                    "❌ Authentication failed during "
                    "deployment verification."
                )

                return False

            elif error.code == 403:

                print()
                print(
                    "❌ Access denied during "
                    "deployment verification."
                )

                return False

            else:

                if attempt < max_attempts:

                    time.sleep(wait_seconds)
                    continue

                return False

        except urllib.error.URLError as error:

            print()
            print(
                "Could not connect to Boomi "
                "for verification."
            )

            print(error)

            if attempt < max_attempts:

                time.sleep(wait_seconds)
                continue

            return False

        except Exception as error:

            print()
            print(
                "Unexpected verification error:"
            )

            print(error)

            return False

    return False


def main():

    print("======================================")
    print("Boomi CI/CD - Deploy Package")
    print("======================================")

    # --------------------------------------------------
    # 1. Read GitHub Secrets
    # --------------------------------------------------

    account_id = os.getenv("BOOMI_ACCOUNT_ID")
    username = os.getenv("BOOMI_API_USERNAME")
    token = os.getenv("BOOMI_API_TOKEN")

    if not account_id:

        print(
            "ERROR: BOOMI_ACCOUNT_ID is not configured"
        )

        sys.exit(1)

    if not username:

        print(
            "ERROR: BOOMI_API_USERNAME is not configured"
        )

        sys.exit(1)

    if not token:

        print(
            "ERROR: BOOMI_API_TOKEN is not configured"
        )

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
            f"ERROR: Configuration file not found: "
            f"{config_file}"
        )

        sys.exit(1)

    except json.JSONDecodeError:

        print(
            f"ERROR: Invalid JSON in {config_file}"
        )

        sys.exit(1)

    environment = config.get("environment")
    environment_id = config.get("environment_id")
    process_name = config.get("process_name")
    process_id = config.get("process_id")

    if not environment_id:

        print(
            "ERROR: environment_id is missing"
        )

        sys.exit(1)

    if not process_id:

        print(
            "ERROR: process_id is missing"
        )

        sys.exit(1)

    print(f"✓ Environment: {environment}")
    print(f"✓ Environment ID: {environment_id}")
    print(f"✓ Process: {process_name}")
    print(f"✓ Process ID: {process_id}")

    # --------------------------------------------------
    # 3. Read Package ID
    # --------------------------------------------------

    package_id = os.getenv("BOOMI_PACKAGE_ID")
    package_version = os.getenv("BOOMI_PACKAGE_VERSION")

    if not package_id:

        print(
            "ERROR: BOOMI_PACKAGE_ID is not configured"
        )

        sys.exit(1)

    print(f"✓ Package ID: {package_id}")

    if package_version:

        print(
            f"✓ Package Version: {package_version}"
        )

    else:

        print(
            "⚠ Package version was not provided."
        )

    # --------------------------------------------------
    # 4. Prepare deployment API
    # --------------------------------------------------

    url = (
        f"https://api.boomi.com/api/rest/v1/"
        f"{account_id}/DeployedPackage"
    )

    payload = {
        "packageId": package_id,
        "environmentId": environment_id,
        "notes": (
            f"GitHub CI/CD deployment for "
            f"{process_name}"
        )
    }

    json_data = json.dumps(payload).encode("utf-8")

    headers = get_auth_headers(
        username,
        token
    )

    request = urllib.request.Request(
        url,
        data=json_data,
        method="POST",
        headers=headers
    )

    # --------------------------------------------------
    # 5. Deploy Package
    # --------------------------------------------------

    print()
    print("Deploying package to BETA...")
    print(f"Endpoint: {url}")

    try:

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            response_body = (
                response.read()
                .decode("utf-8")
            )

            print()
            print(
                "======================================"
            )
            print(
                "Boomi Deployment Response"
            )
            print(
                "======================================"
            )

            print(
                f"HTTP Status: {response.status}"
            )

            print()
            print("Response:")
            print(response_body)

            if response.status not in (
                200,
                201,
                202
            ):

                print()
                print(
                    "ERROR: Deployment request "
                    "failed."
                )

                sys.exit(1)

            try:

                result = json.loads(
                    response_body
                )

            except json.JSONDecodeError:

                print()
                print(
                    "ERROR: Boomi returned invalid "
                    "deployment JSON."
                )

                sys.exit(1)

            deployment_id = result.get(
                "deploymentId"
            )

            returned_package_id = result.get(
                "packageId"
            )

            returned_package_version = result.get(
                "packageVersion"
            )

            returned_environment_id = result.get(
                "environmentId"
            )

            returned_component_id = result.get(
                "componentId"
            )

            active = result.get(
                "active"
            )

            if not deployment_id:

                print()
                print(
                    "ERROR: Boomi did not return "
                    "deploymentId."
                )

                sys.exit(1)

            print()
            print(
                "✓ Package deployment request successful"
            )

            print(
                f"✓ Deployment ID: {deployment_id}"
            )

            print(
                f"✓ Package: {returned_package_id}"
            )

            print(
                f"✓ Package Version: "
                f"{returned_package_version}"
            )

            print(
                f"✓ Environment ID: "
                f"{returned_environment_id}"
            )

            print(
                f"✓ Component ID: "
                f"{returned_component_id}"
            )

            print(
                f"✓ Active in deployment response: "
                f"{active}"
            )

            # --------------------------------------------------
            # 6. Verify Deployment
            # --------------------------------------------------

            verification_success = verify_deployment(
                account_id=account_id,
                deployment_id=deployment_id,
                package_id=package_id,
                package_version=package_version,
                environment_id=environment_id,
                process_id=process_id,
                username=username,
                token=token
            )

            if not verification_success:

                print()
                print(
                    "======================================"
                )
                print(
                    "DEPLOYMENT VERIFICATION FAILED"
                )
                print(
                    "======================================"
                )

                sys.exit(1)

            # --------------------------------------------------
            # 7. Final Success
            # --------------------------------------------------

            print()
            print(
                "======================================"
            )
            print(
                "DEPLOYMENT SUCCESSFUL"
            )
            print(
                "======================================"
            )

            print(
                f"Process: {process_name}"
            )

            print(
                f"Package ID: {package_id}"
            )

            print(
                f"Package Version: "
                f"{returned_package_version}"
            )

            print(
                f"Environment: {environment}"
            )

            print(
                f"Deployment ID: {deployment_id}"
            )

            print(
                "Status: ACTIVE"
            )

            print(
                "Deployment verification: PASSED"
            )

            sys.exit(0)

    except urllib.error.HTTPError as error:

        print()
        print(
            "======================================"
        )
        print(
            "Boomi Deployment Error"
        )
        print(
            "======================================"
        )

        print(
            f"HTTP Status: {error.code}"
        )

        try:

            error_body = (
                error.read()
                .decode("utf-8")
            )

            print()
            print("Boomi Response:")
            print(error_body)

        except Exception:

            print(
                "Could not read Boomi error response."
            )

        if error.code == 401:

            print()
            print(
                "ERROR: Authentication failed."
            )

        elif error.code == 403:

            print()
            print(
                "ERROR: Access denied."
            )

            print(
                "Check Packaged Component "
                "Deployment permissions."
            )

        elif error.code == 404:

            print()
            print(
                "ERROR: Package or environment "
                "was not found."
            )

        elif error.code == 400:

            print()
            print(
                "ERROR: Invalid deployment request."
            )

        else:

            print()
            print(
                "ERROR: Boomi deployment API "
                "request failed."
            )

        sys.exit(1)

    except urllib.error.URLError as error:

        print()
        print(
            "ERROR: Could not connect to "
            "Boomi API."
        )

        print(error)

        sys.exit(1)

    except Exception as error:

        print()
        print(
            "ERROR: Unexpected error occurred."
        )

        print(error)

        sys.exit(1)


if __name__ == "__main__":
    main()
