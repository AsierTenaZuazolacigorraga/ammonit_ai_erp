#! /usr/bin/env bash

set -e
set -x

cd backend
python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
mkdir -p backend/app/client
openapi-python-client generate \
    --overwrite \
    --path openapi.json \
    --output-path backend/app/api_client/
mv openapi.json frontend/
cd frontend
npm run generate-client
# NOTE: disabled formatting due to too many exceptions in the generated code
# npx biome format --write ./src/client
