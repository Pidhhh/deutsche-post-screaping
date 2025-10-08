# Kununu Web Scraper - Deutsche Post & DHL Reviews

A Python web scraper to extract employee reviews from Kununu.com for Deutsche Post & DHL.

## 📋 Project Information

- **Target Website:** https://www.kununu.com/de/deutsche-post/kommentare
- **Company:** Deutsche Post & DHL
- **Total Reviews Available:** 12,569+ employee reviews
- **Date Created:** October 8, 2025

## 🎯 Features

- Scrapes employee reviews from multiple pages
- Extracts comprehensive review data including:
  - Review title and overall rating
  - Recommendation status
  - Employee position and department
  - Pros, cons, and improvement suggestions
  - Detailed category ratings (13 categories)
- Exports data in multiple formats:
  - JSON
  - CSV
  - Excel (XLSX)
- Respectful scraping with delays between requests
- Progress tracking and error handling

## 📊 Data Collected

### Basic Information

- Review title
- Overall rating (1-5 stars)
- Recommendation (Recommended/Not Recommended)
- Review date
- Employee position/role
- Department and location

### Review Content

- **Pros:** What employees like about the employer
- **Cons:** What employees dislike about the employer
- **Suggestions:** Improvement suggestions

### Category Ratings (13 Categories)

1. Arbeitsatmosphäre (Work atmosphere)
2. Image (Company image)
3. Work-Life-Balance
4. Karriere/Weiterbildung (Career/Training)
5. Gehalt/Sozialleistungen (Salary/Benefits)
6. Umwelt-/Sozialbewusstsein (Environmental/Social awareness)
7. Kollegenzusammenhalt (Team spirit)
8. Umgang mit älteren Kollegen (Treatment of older colleagues)
9. Vorgesetztenverhalten (Supervisor behavior)
10. Arbeitsbedingungen (Working conditions)
11. Kommunikation (Communication)
12. Gleichberechtigung (Equal opportunity)
13. Interessante Aufgaben (Interesting tasks)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser (for Selenium)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `selenium` - Browser automation
- `pandas` - Data manipulation
- `lxml` - XML/HTML parser
- `webdriver-manager` - Automatic ChromeDriver management
- `openpyxl` - Excel file support

## 💻 Usage

### Basic Usage

Run the scraper:

```bash
python scraper.py
```

You'll be prompted to enter the number of pages to scrape.

### Customizing the Scraper

Edit `scraper.py` to modify:

```python
# Change the number of pages to scrape
max_pages = 5  # Default is 5 pages

# Change delay between requests (in seconds)
time.sleep(3)  # Default is 3 seconds
```

## 📁 Output

All scraped data is saved in the `output/` folder:

- `output/reviews.json` - JSON format
- `output/reviews.csv` - CSV format (Excel-compatible)
- `output/reviews.xlsx` - Excel format

## 📝 Example Output Structure

### JSON Format

```json
[
  {
    "title": "Sehr positiver Bewerbungsprozess",
    "rating": "5.0",
    "recommendation": "Empfohlen",
    "date": "Oktober 2025",
    "position": "Angestellte/r oder Arbeiter/in",
    "department": "Logistik / Materialwirtschaft",
    "location": "Freiburg im Breisgau",
    "pros": "Ich finde die Professionalität und Freundlichkeit...",
    "cons": "Ich habe keinen negativen Eindruck...",
    "suggestions": "Ich hatte keine Verbesserungsvorschläge...",
    "categories": {
      "Arbeitsatmosphäre": "Alles war super, vielen Dank...",
      "Work-Life-Balance": "Die Work-Life-Balance scheint...",
      ...
    }
  }
]
```

### CSV/Excel Format

Each review is a row with columns for all data fields.

## ⚠️ Important Notes

### Legal & Ethical Considerations

- Always check the website's `robots.txt` and Terms of Service
- This scraper is for educational purposes
- Be respectful: don't overload the server with too many requests
- The scraper includes delays between requests to be polite

### Rate Limiting

- Default: 3 seconds delay between pages
- Increase if you encounter blocking or errors
- Consider scraping during off-peak hours

### Anti-Scraping Measures

- Kununu may use anti-bot protection
- The scraper uses Selenium with headless Chrome
- User-agent is set to mimic a real browser
- If blocked, try:
  - Increasing delays
  - Using proxies
  - Running without headless mode

## 🔧 Troubleshooting

### ChromeDriver Issues

```bash
# If automatic ChromeDriver installation fails:
# 1. Download ChromeDriver manually from:
#    https://chromedriver.chromium.org/
# 2. Place it in your PATH or project folder
```

### No Data Scraped

- Website structure may have changed
- Check if cookie banner is blocking content
- Try running without headless mode to debug:
  ```python
  # Comment out this line in scraper.py:
  # chrome_options.add_argument('--headless')
  ```

### Encoding Issues (Windows)

The scraper uses `utf-8-sig` encoding for CSV to ensure proper display of German characters (ä, ö, ü, ß) in Excel.

## 📈 Performance

- **Speed:** ~1 page per 5-6 seconds (including delays)
- **Reviews per page:** ~15-20 reviews
- **5 pages:** ~75-100 reviews in ~30 seconds

## 🔮 Future Improvements

- [ ] Add pagination auto-detection
- [ ] Scrape employer responses
- [ ] Add data visualization
- [ ] Export to database (SQLite/MySQL)
- [ ] Add filtering by date range
- [ ] Multi-threading for faster scraping

## 📚 Dependencies

See `requirements.txt` for the complete list of dependencies and versions.

## 👨‍💻 Author

Student Project - Created as part of a web scraping assignment

## 📄 License

This project is for educational purposes only.

## ⚡ Quick Start

```bash
# 1. Clone or download the project
# 2. Navigate to the project folder
cd Screaping-Jerman

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the scraper
python scraper.py

# 5. Check the output folder
cd output
```

---

**Happy Scraping! 🕷️**
