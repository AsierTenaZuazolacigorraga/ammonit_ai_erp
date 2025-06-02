#!/usr/bin/env bash

# Change to the backend directory
cd "$(dirname "$0")"
cd ..

# Activate env and change path
source ./.venv/bin/activate
cd bridge

# Arguments
ENTRY_FILE="$1"
if [[ -z "$ENTRY_FILE" ]]; then
  echo "Usage: $0 <entry_python_file.py>"
  exit 1
fi
BASE_NAME=$(basename "$ENTRY_FILE" .py)
SERVICE_NAME="ubuntu_service_${BASE_NAME}"

# Clean
mkdir -p "$SERVICE_NAME"
rm -rf "$SERVICE_NAME"/*

# Create binary with all files going to build_output directory
pyinstaller --onefile \
    --name $SERVICE_NAME \
    --distpath "$SERVICE_NAME/dist" \
    --workpath "$SERVICE_NAME/build" \
    --specpath "$SERVICE_NAME" \
    --paths ../../ \
    --paths ../ \
    --collect-data dotenv \
    --hidden-import pkg_resources.py2_warn \
    "$ENTRY_FILE"

echo "Binary generated successfully!"
echo "You can find the executable at: ./$SERVICE_NAME/dist/$SERVICE_NAME"
echo ""
echo "To test the binary:"
echo "  ./$SERVICE_NAME/dist/$SERVICE_NAME"
echo ""
echo "To install as a system service, run:"
echo "  sudo cp ./$SERVICE_NAME/dist/$SERVICE_NAME /usr/local/bin/"
echo "  sudo chmod +x /usr/local/bin/$SERVICE_NAME"
echo ""
echo "All build files are organized in: ./$SERVICE_NAME/"
echo "  - dist/           : Final executable"
echo "  - build/          : Temporary build files"
echo "  - *.spec          : PyInstaller specification file"
