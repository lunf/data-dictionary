#!/bin/bash
# =====================================
# Business Term Extraction Project Setup
# =====================================

# Exit on error
set -e

echo "🚀 Setting up project environment..."

# 1️⃣ Create and activate virtual environment
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
else
  echo "✅ Virtual environment already exists."
fi

# Activate it
source venv/bin/activate

# 2️⃣ Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 3️⃣ Install dependencies
if [ -f "requirements.txt" ]; then
  echo "📚 Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
else
  echo "⚠️  requirements.txt not found!"
  exit 1
fi

# 4️⃣ Download NLP models
echo "🧠 Downloading NLP models..."
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger wordnet
python -m spacy download en_core_web_lg

# 5️⃣ Summary
echo ""
echo "✅ Setup complete!"
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "Then start the project with:"
echo "  python -m app.main"
