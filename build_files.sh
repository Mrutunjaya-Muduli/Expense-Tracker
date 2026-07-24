# build_files.sh
echo "BUILD START"

# Install requirements
python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"
