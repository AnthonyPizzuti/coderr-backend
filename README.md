# Coderr Backend

Django REST API for the Coderr freelance platform. Business users publish
offers, customers order and review them. Authentication uses DRF token auth.

This repository contains the backend only. The frontend is not included.

## Frontend

Built against the Coderr frontend **v1.2.1** (see its `CHANGELOG.md`).

Required change in the frontend file `shared/scripts/config.js`:

- The customer guest password was changed from `login26` to `coderr26`.
  Django's `MinimumLengthValidator` requires at least 8 characters.
- The business guest password was already `coderr26` and stayed unchanged.

Guest logins (these users must exist in the database):

| Username | Password | Type     |
| -------- | -------- | -------- |
| Mike     | coderr26 | customer |
| Anthony  | coderr26 | business |

Register both accounts through the frontend registration page after the
first migrate. They are not part of this repository.

## Requirements

- Python 3.14
- The packages in `requirements.txt`

## Setup

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
