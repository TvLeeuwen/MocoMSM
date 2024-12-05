"""Conda environment setup for MocoMSM"""

# Imports ---------------------------------------------------------------------
import subprocess
import os
import textwrap

# Check for existing envMocoMSM
try:
    result = subprocess.run(["conda", "env", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if 'envMocoMSM' in result.stdout:
        try:
            subprocess.run(["conda", "remove", "-n", "envMocoMSM", "--all", "--y"])
        except Exception as e:
            print(f"Error removing envMocoMSM: {e}")
            os._exit(0)

except Exception as e:
    print(f"Error checking Conda environments: {e}")

try:
    subprocess.run(
        ["conda", "env", "create", "-f", "setup_envMocoMSM/envMocoMSM.yml"],
        check=True,
    )
except subprocess.CalledProcessError as e:
    print(f"Error installing envMocoMSM:\n {e}")
    os._exit(0)

print("Installing dependencies, this may take some time depending on your system...")

try:
    subprocess.run(
        [
            "conda",
            "run",
            "-n",
            "envMocoMSM",
            "pip",
            "install",
            "-r",
            "setup_envMocoMSM/requirements.txt",
        ],
        check=True,
    )

    print(
        textwrap.dedent(
            """
        #
        # Conda envMocoMSM installed. To activate this environment, use
        #
        #     $ conda activate envMocoMSM
        #
        # To deactivate an active environment, use
        #
        #     $ conda deactivate
        #
        # To uninstall this environment, use
        #
        #     $ conda remove -n envMocoMSM --all
        #
        """
        )
    )

except subprocess.CalledProcessError as e:
    print(f"Error during pip installation: {e}")
