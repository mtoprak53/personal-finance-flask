# Personal Finance Tracker

A modern, intuitive web application for managing your personal finances built with Flask, PostgreSQL, and Bootstrap 5.

![Finance Dashboard](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3%2B-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 📊 **Dashboard Overview**
- Real-time financial dashboard with key metrics
- Monthly income/expense tracking
- Net worth calculation
- Visual statistics and trends

### 💼 **Account Management**
- Multiple currency support (USD, EUR, TRY)
- Account balance tracking
- Currency-specific calculations
- Quick account creation/deletion

### 💸 **Transaction Tracking**
- Income vs. expense categorization
- Custom transaction categories
- Date-based filtering
- Transaction descriptions and notes

### 🎨 **Modern UI/UX**
- Responsive design (mobile & desktop)
- Dark/light mode support
- Interactive charts and graphs
- Real-time updates
- Bootstrap 5 with custom CSS

### 🔒 **Security Features**
- Secure session management
- CSP (Content Security Policy) ready
- HTTPS enforcement in production
- SQL injection protection
- Rate limiting support

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mtoprak53/personal-finance-flask.git
cd personal-finance-flask
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp environments/.env.example environments/.env.development
# Edit environments/.env.development with your settings
```

5. **Configure database**
```bash
createdb finance_tracker
# Update DATABASE_URL in your .env file
```

6. **Run the application**
```bash
FLASK_ENV=development flask run
```

Visit `http://localhost:5000` to see your dashboard!

## 🏗️ Project Structure

```
personal-finance-flask/
├── app.py              # Main application factory
├── config/             # Configuration classes
├── routes/             # Application routes
├── models.py           # Database models
├── static/             # CSS, JS, images
├── templates/          # HTML templates
├── environments/       # Environment variables
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 📦 Configuration

### Environment Files
- `environments/.env.development` - Development settings
- `environments/.env.production` - Production settings
- `environments/.env.testing` - Testing settings

### Key Configuration Options
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/finance_tracker

# Security
SECRET_KEY=your-secure-secret-key-here
TIMEZONE=America/New_York

# Features
ENABLE_DARK_MODE=true
ENABLE_REGISTRATION=false
```

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t finance-tracker .

# Run the container
docker run -p 5000:5000 finance-tracker
```

## 🚂 Railway Deployment

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/mtoprak53/personal-finance-flask)

1. Click the "Deploy on Railway" button above
2. Add PostgreSQL database
3. Set environment variables
4. Deploy!

## 🔧 Development

### Running Tests
```bash
FLASK_ENV=testing pytest
```

### Code Style
```bash
# Format code
black app.py routes/ config/

# Check imports
isort .
```

### Database Migrations
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## 📈 API Endpoints

### REST API
```
GET    /api/transactions     # List transactions
GET    /api/stats            # Financial statistics
GET    /api/categories       # Spending categories
GET    /api/chart_data       # Chart data
```

### Health Check
```
GET    /health              # Application health status
```

## 🎯 Roadmap

- [ ] **User Authentication** - Multi-user support
- [ ] **Budget Planning** - Monthly budget setting
- [ ] **Recurring Transactions** - Automated entries
- [ ] **Data Export** - CSV/PDF reports
- [ ] **Mobile App** - React Native companion
- [ ] **Bank Sync** - Plaid integration
- [ ] **Investment Tracking** - Stock/portfolio
- [ ] **AI Insights** - Spending pattern analysis

<!-- ## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request -->

<!-- ## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. -->

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap 5](https://getbootstrap.com/) - CSS framework
- [Font Awesome](https://fontawesome.com/) - Icons
- [Chart.js](https://www.chartjs.org/) - Charts & graphs
- [Railway](https://railway.app/) - Deployment platform

<!-- ## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mtoprak53/personal-finance-flask/issues)
- **Email**: [Your Email]
- **Twitter**: [@YourHandle] -->

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mtoprak53/personal-finance-flask&type=Date)](https://star-history.com/#mtoprak53/personal-finance-flask&Date)

---

**Built with ❤️ by [MT](https://github.com/mtoprak53)**

If you find this project useful, please give it a ⭐ on GitHub!

---

<!-- ## 🔍 Quick Links

- [Live Demo](https://your-demo-link.railway.app)
- [Documentation](docs/)
- [Changelog](CHANGELOG.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing Guidelines](CONTRIBUTING.md) -->

---

*Last Updated: January 2026*