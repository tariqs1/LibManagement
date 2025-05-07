# Library Management System

A comprehensive library management system built with Django, featuring user authentication, book management, borrowing system, and administrative features.

## Features

### User Features
- User registration and authentication
- Book browsing and searching
- Book borrowing and returning
- Book reservation system
- Due date extensions
- User profile management
- Book reviews and ratings

### Admin Features
- Book management (add, edit, delete)
- User management
- Transaction tracking
- Report generation
- Overdue book tracking
- Revenue monitoring

### System Features
- Responsive design
- Email notifications
- Search functionality
- Report generation
- Data visualization
- Secure authentication

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- Redis (for background tasks)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/library-management.git
cd library-management
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the database:
- Create a MySQL database
- Update database settings in `settings.py`

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost:3306/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Project Structure

```
library-management/
├── CS557FinalProject/
│   ├── LibraryManagement/
│   │   ├── templates/
│   │   ├── static/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── forms.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Usage

1. Access the admin interface at `/admin`
2. Regular users can access the system at the root URL
3. Use the search functionality to find books
4. Borrow books through the book detail page
5. Manage your profile and borrowed books in the user dashboard

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
This project follows PEP 8 guidelines. Use a linter to maintain code quality:
```bash
flake8
```

### Database Migrations
When making model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Documentation
- Bootstrap
- Font Awesome
- All contributors and users

## Support

For support, email support@librarymanagement.com or create an issue in the repository.

## Roadmap

- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Integration with external book APIs
- [ ] E-book support
- [ ] Multi-language support
- [ ] Advanced search filters
- [ ] Book recommendations system
- [ ] Social features
- [ ] API documentation
- [ ] Automated testing suite 