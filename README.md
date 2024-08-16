# Sound Marshal

Sound Marshal is a Django-based web application designed to connect artists, curators, and fans, allowing them to share and discover new music.

## Features

- User roles: Artist, Curator, and Fan
- Track uploads and playback
- Profile management
- Track liking and commenting
- Explore page with related tracks and profiles
- Secure authentication with Django Allauth

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+**: Make sure Python is installed on your machine.
- **Pip**: Ensure pip is installed (`pip` usually comes with Python).
- **Virtualenv**: Install `virtualenv` for creating isolated Python environments.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sound-marshal.git
cd sound-marshal
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment to isolate your dependencies:

- On macOS/Linux:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- On Windows:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 3. Install Dependencies

Install the necessary Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up the Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables:

```plaintext
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgres://user:password@localhost:5432/dbname

STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLIC_KEY=your-stripe-public-key
```

### 5. Apply Migrations

Apply the database migrations to set up the necessary tables:

```bash
python manage.py migrate
```

### 6. Create a Superuser

Create a superuser to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set the username, email, and password.

### 7. Collect Static Files

Collect all static files into a single location:

```bash
python manage.py collectstatic
```

### 8. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your web browser to see the application running.

## Usage

Once the server is running, you can:

- **Log in** as the superuser or create a new user account.
- **Upload tracks** (if logged in as an artist).
- **Explore** tracks and profiles from the Explore page.
- **Like tracks**, comment on them, and interact with other users.

## Deployment

To deploy this project, you will need to:

- Set up a production database (e.g., PostgreSQL)
- Configure a web server (e.g., Nginx) and WSGI server (e.g., Gunicorn)
- Set `DEBUG=False` in your environment variables
- Securely manage your `SECRET_KEY` and other sensitive data

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## License

This project belongs to Joshua Howard and all rights are reserved.

## Contact

If you have any questions or need further assistance, feel free to contact the project maintainers.
```

### Usage Instructions:
- Copy this markdown text into a `README.md` file in the root of your project.
- Update the repository URL in the "Clone the Repository" section.
- Replace placeholders such as `your-secret-key`, `your-stripe-secret-key`, etc., with actual values or instructions.
