#!/usr/bin/env bash
# Test every processor in SharedProcessors/ by importing it as a module.
# Uses .venv/bin/python with autopkg sourced from ../autopkg/Code.
#
# Exit codes:
#   0  all processors imported successfully
#   1  one or more processors failed

set -uo pipefail

VERBOSE=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose) VERBOSE=1; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Windows venv uses Scripts/, Unix uses bin/
PYTHON="${SCRIPT_DIR}/.venv/bin/python"
[[ ! -x "${PYTHON}" ]] && PYTHON="${SCRIPT_DIR}/.venv/Scripts/python"
# Check adjacent repo first (local dev), then within repo (CI checkout via setup-autopkg)
AUTOPKG_PATH="${SCRIPT_DIR}/../autopkg/Code"
[[ ! -d "${AUTOPKG_PATH}" ]] && AUTOPKG_PATH="${SCRIPT_DIR}/autopkg/Code"
PROCESSORS_DIR="${SCRIPT_DIR}/SharedProcessors"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [[ ! -x "${PYTHON}" ]]; then
    echo "Python not found at ${PYTHON}" >&2
    PYTHON="$(command -v python3 || command -v python || true)"
    if [[ -z "${PYTHON}" ]]; then
        echo "Python not found in PATH" >&2
        exit 1
    fi
fi

if [[ ! -d "${AUTOPKG_PATH}" ]]; then
    echo "autopkg not found at ${AUTOPKG_PATH}" >&2
    AUTOPKG_PATH="$(command -v autopkg || true)"
    if [[ -z "${AUTOPKG_PATH}" ]]; then
        AUTOPKG_PATH="autopkg/Code/autopkg"
        if [[ ! -d "${AUTOPKG_PATH}" ]]; then
            echo "autopkg not found in PATH or at ${AUTOPKG_PATH}" >&2
            exit 1
        fi
    fi
fi

pass=0
fail=0
declare -a failures

# Use `timeout` if available to prevent a hanging import from blocking the whole run
TIMEOUT_CMD=""
if command -v timeout &>/dev/null; then
    TIMEOUT_CMD="timeout 60"
fi

# Test importing each processor as a module to ensure it can be imported without error:
for script in "${PROCESSORS_DIR}"/*.py; do
    name="$(basename "${script}")"
    output=$(PYTHONPATH="${AUTOPKG_PATH}:${PROCESSORS_DIR}" ${TIMEOUT_CMD} "${PYTHON}" - "${script}" 2>&1 <<'EOF'
import importlib.util, sys, warnings
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("module", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
EOF
)
    if [[ $? -eq 0 ]]; then
        echo -e "  ${GREEN}PASS${NC}  ${name}"
        if [[ ${VERBOSE} -eq 1 && -n "${output}" ]]; then
            echo -e "${YELLOW}        ${output//$'\n'/$'\n'        }${NC}"
        fi
        (( pass++ ))
    else
        echo -e "  ${RED}FAIL${NC}  ${name}"
        echo -e "${YELLOW}        ${output//$'\n'/$'\n'        }${NC}"
        failures+=("${name}")
        (( fail++ ))
    fi
done

# # run main() for each processor to ensure it runs without error:
# for script in "${PROCESSORS_DIR}"/*.py; do
#     name="$(basename "${script}" .py)"
#     output=$(PYTHONPATH="${AUTOPKG_PATH}:${PROCESSORS_DIR}" "${PYTHON}" - "${script}" 2>&1 <<EOF
# from ${name} import ${name}

# p = ${name}({})
# p.main()
# print(p.env)
# EOF
# )
#     if [[ $? -eq 0 ]]; then
#         echo -e "  ${GREEN}PASS${NC}  ${name}"
#         if [[ ${VERBOSE} -eq 1 && -n "${output}" ]]; then
#             echo -e "${YELLOW}        ${output//$'\n'/$'\n'        }${NC}"
#         fi
#         (( pass++ ))
#     else
#         echo -e "  ${RED}FAIL${NC}  ${name}"
#         echo -e "${YELLOW}        ${output//$'\n'/$'\n'        }${NC}"
#         failures+=("${name}")
#         (( fail++ ))
#     fi
# done

echo ""
echo -e "Results: ${GREEN}${pass} passed${NC}, ${RED}${fail} failed${NC}  ($(( pass + fail )) total)"

if [[ ${fail} -gt 0 ]]; then
    echo ""
    echo "Failed processors:"
    for f in "${failures[@]}"; do
        echo "  - ${f}"
    done
    exit 1
fi
