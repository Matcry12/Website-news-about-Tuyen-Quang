# Tuyen Quang Explorer

A comprehensive hotel booking and management system for Tuyen Quang province, Vietnam. This Django-based web application provides a platform for users to explore, book, and manage hotel accommodations in the Tuyen Quang region.

## Features

### For Customers
- Browse and search hotels in Tuyen Quang
- View detailed hotel information including rooms, prices, and ratings
- Book hotel rooms with real-time availability
- User registration and authentication
- Booking history and order management
- Rate and comment on hotels
- Multi-language support (Vietnamese and English)

### For Hotel Owners
- Hotel management dashboard
- Room management (add, update, delete rooms)
- View and manage bookings
- Update hotel information and images
- Track booking statistics

### For Administrators
- User account management
- Hotel verification and approval
- System-wide statistics and reporting
- Export booking data to Excel

## Technology Stack

- **Backend**: Django 5.1.4
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (development), MySQL support
- **Image Processing**: Pillow
- **Data Export**: Pandas, OpenPyXL
- **Static Files**: WhiteNoise
- **Internationalization**: Django i18n framework

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Tuyen-Quang-Explorer.git
cd Tuyen-Quang-Explorer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser account:
```bash
python manage.py createsuperuser
```

6. Collect static files:
```bash
python manage.py collectstatic
```

7. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Project Structure

```
Tuyen-Quang-Explorer/
├── home/                    # Main application
│   ├── models.py           # Database models
│   ├── views/              # View modules
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, images
│   └── migrations/         # Database migrations
├── mywebsite/              # Django project settings
├── locale/                 # Translation files
├── staticfiles/            # Collected static files
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Key Models

- **User**: Extended Django user model with profile
- **Product**: Hotel listings
- **Room**: Individual rooms within hotels
- **Order**: Booking records
- **Comment**: User reviews and ratings
- **History**: Booking history tracking

## Configuration

### Environment Variables
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Change the default secret key
- `ALLOWED_HOSTS`: Update for production deployment

### Database
The project uses SQLite by default. For production, configure MySQL in `settings.py`.

### Static Files
Static files are served using WhiteNoise. Ensure `STATIC_ROOT` is properly configured.

## API Endpoints

Key URL patterns include:
- `/` - Homepage
- `/login/` - User login
- `/register/` - User registration
- `/hotel/<id>/` - Hotel details
- `/booking/` - Booking page
- `/cart/` - Shopping cart
- `/history/` - Booking history
- `/manage-hotel/` - Hotel management (owners)
- `/manage-account/` - User account management (admin)

## Localization

The application supports:
- Vietnamese (vi)
- English (en)

Language can be changed through the interface.

## Security Considerations

- Change the default `SECRET_KEY` before deployment
- Set `DEBUG = False` in production
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production
- Regular security updates for dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for the tourism industry of Tuyen Quang province
- Uses Bootstrap for responsive design
- Font Awesome for icons
- Owl Carousel for image sliders

## Support

For issues, questions, or contributions, please open an issue in the GitHub repository.