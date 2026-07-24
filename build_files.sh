# build_files.sh
echo "BUILD START"

# Create a temporary virtual environment for the build phase
python3 -m venv venv_build
source venv_build/bin/activate

# Install requirements inside the virtual environment
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

echo "BUILD END"

