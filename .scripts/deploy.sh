#!/bin/bash
set -e

echo "Deployment started ..."

echo "Copying New changes...."
git pull origin main
echo "New changes copied to server !"

source venv/bin/activate
echo "Virtual env 'venv' Activated !"

echo "Installing Dependencies..."
pip install -r requirements.txt --no-input

echo "Running Database migration..."
python manage.py migrate --no-input

deactivate
echo "Virtual env 'venv' Deactivated !"

echo "Reloading App..."
sudo supervisorctl restart daphne1
sudo supervisorctl restart daphne2
sudo supervisorctl restart celery
sudo systemctl reload nginx

echo "Deployment Finished !"