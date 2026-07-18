#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
model_directory="${project_root}/models/gemma"

mkdir -p "${model_directory}"
echo "Created ${model_directory}. Place an approved local Gemma model here."
echo "Automatic model downloads are intentionally disabled."
