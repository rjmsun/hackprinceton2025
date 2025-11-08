#!/bin/bash

echo "🔑 Testing API Keys Configuration"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Run: cp env.example .env"
    echo "Then edit .env with your API keys"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Load .env and check keys
source .env

check_key() {
    local key_name=$1
    local key_value=$2
    local prefix=$3
    
    if [ -z "$key_value" ] || [ "$key_value" = "${key_name//_/ }" ]; then
        echo "❌ $key_name not set"
        return 1
    elif [[ "$key_value" == *"your_"* ]] || [[ "$key_value" == *"_here"* ]]; then
        echo "⚠️  $key_name still has placeholder value"
        return 1
    elif [ -n "$prefix" ] && [[ "$key_value" != $prefix* ]]; then
        echo "⚠️  $key_name doesn't start with expected prefix ($prefix)"
        return 1
    else
        echo "✅ $key_name configured"
        return 0
    fi
}

echo "Required Keys:"
echo "--------------"
check_key "OPENAI_API_KEY" "$OPENAI_API_KEY" "sk-"
check_key "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY" "sk-ant-"
check_key "ELEVENLABS_API_KEY" "$ELEVENLABS_API_KEY" ""

echo ""
echo "Optional Keys:"
echo "--------------"
check_key "GOOGLE_CLIENT_ID" "$GOOGLE_CLIENT_ID" ""
check_key "GOOGLE_CLIENT_SECRET" "$GOOGLE_CLIENT_SECRET" ""
check_key "AMPLITUDE_API_KEY" "$AMPLITUDE_API_KEY" ""

echo ""
echo "=================================="
echo "✅ Configuration check complete"
echo ""

