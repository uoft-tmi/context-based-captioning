#!/bin/bash

# Helper script to view the project components

show_help() {
    echo "Usage: bash view.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --app        Run the main Streamlit application (root app.py)"
    echo "  --dashboard  Run the Streamlit analytics dashboard (dashboard/app.py)"
    echo "  --next       Run the Next.js production dashboard (rescoring-dashboard)"
    echo "  --help       Show this help message"
}

if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

case "$1" in
    --app)
        echo "Starting Main Streamlit App..."
        streamlit run app.py
        ;;
    --dashboard)
        echo "Starting Streamlit Analytics Dashboard..."
        streamlit run dashboard/app.py
        ;;
    --next)
        echo "Starting Next.js Dashboard..."
        cd rescoring-dashboard
        if [ ! -d "node_modules/next" ]; then
            echo "Dependencies missing. Running 'npm install'..."
            npm install
        fi
        npm run dev
        ;;
    --help)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
