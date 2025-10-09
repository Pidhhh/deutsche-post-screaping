"""
Kununu Web Scraper for Deutsche Post & DHL Reviews
Author: Cesario Hafidh
Date: October 8, 2025
"""

import time
import json
import csv
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import requests


class KununuScraper:
    def __init__(self, base_url, use_selenium=True):
        self.base_url = base_url
        self.reviews_data = []
        self.driver = None
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
    def setup_driver(self):
        """Initialize Selenium WebDriver with Chrome"""
        print("Setting up Chrome WebDriver...")
        try:
            # Configure Chrome options
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # Run without opening a browser window
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Setup WebDriver with explicit chromedriver.exe path
            chrome_install = ChromeDriverManager().install()
            folder = os.path.dirname(chrome_install)
            chromedriver_path = os.path.join(folder, "chromedriver.exe")
            
            print(f"ChromeDriver folder: {folder}")
            print(f"ChromeDriver path: {chromedriver_path}")
            
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("WebDriver setup complete!")
        except Exception as e:
            print(f"Error setting up ChromeDriver: {e}")
            print("\nTrying alternative approach...")
            raise
        
    def close_cookie_banner(self):
        """Close cookie consent banner if present"""
        try:
            # Wait for cookie banner and click accept
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Akzeptieren') or contains(text(), 'Accept')]"))
            )
            cookie_button.click()
            print("Cookie banner closed")
            time.sleep(2)
        except Exception as e:
            print("No cookie banner found or already closed")
    
    def click_show_stars_buttons(self):
        """Click all 'show stars' buttons to reveal hidden category ratings"""
        try:
            # Look for buttons that show hidden star ratings
            # Common patterns: "Sterne ausblenden", "Alle anzeigen", etc.
            show_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Sterne') or contains(text(), 'anzeigen') or contains(@class, 'reviews-hide-star')]"
            )
            
            if show_buttons:
                print(f"Found {len(show_buttons)} 'show stars' buttons, clicking them...")
                for idx, button in enumerate(show_buttons):
                    try:
                        # Scroll to button to make it visible
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        # Click the button
                        button.click()
                        time.sleep(0.3)
                        print(f"  Clicked button {idx + 1}/{len(show_buttons)}")
                    except Exception as e:
                        print(f"  Failed to click button {idx + 1}: {e}")
                        continue
                
                print("All 'show stars' buttons clicked")
                time.sleep(2)  # Wait for ratings to load
            else:
                print("No 'show stars' buttons found (ratings might be visible already)")
                
        except Exception as e:
            print(f"Error clicking show stars buttons: {e}")
    
    def scrape_review(self, review_element):
        """Extract data from a single review element"""
        review_data = {
            'title': '',
            'rating': '',
            'recommendation': '',
            'date': '',
            'position': '',
            'department': '',
            'location': '',
            'pros': '',
            'cons': '',
            'suggestions': '',
            'categories': {},
            'category_ratings': {}  # Store star ratings per category
        }
        
        try:
            # Extract title
            title_elem = review_element.find('h3')
            if title_elem:
                review_data['title'] = title_elem.get_text(strip=True)
            
            # Extract overall rating (e.g., "2,2", "3,5", "4")
            # Look for span with class containing 'score' (e.g., index__score__BktQY)
            rating_elem = review_element.find('span', class_=lambda x: x and 'score' in str(x).lower())
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Only accept if it looks like a number (e.g., "2,2" or "3")
                if rating_text and any(char.isdigit() for char in rating_text):
                    review_data['rating'] = rating_text
            
            # Extract recommendation
            recommendation_elem = review_element.find(string=lambda x: x and ('Empfohlen' in x or 'Nicht empfohlen' in x))
            if recommendation_elem:
                review_data['recommendation'] = recommendation_elem.strip()
            
            # Extract date
            date_elem = review_element.find(string=lambda x: x and any(month in str(x) for month in ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']))
            if date_elem:
                review_data['date'] = date_elem.strip()
            
            # Extract position/department/location
            position_elem = review_element.find(string=lambda x: x and 'Angestellte' in str(x) or 'Arbeiter' in str(x))
            if position_elem:
                review_data['position'] = position_elem.strip()
            
            # Extract pros (Gut am Arbeitgeber)
            pros_section = review_element.find(string=lambda x: x and 'Gut am Arbeitgeber finde ich' in str(x))
            if pros_section:
                pros_parent = pros_section.find_parent()
                if pros_parent:
                    next_elem = pros_parent.find_next_sibling()
                    if next_elem:
                        review_data['pros'] = next_elem.get_text(strip=True)
            
            # Extract cons (Schlecht am Arbeitgeber)
            cons_section = review_element.find(string=lambda x: x and 'Schlecht am Arbeitgeber finde ich' in str(x))
            if cons_section:
                cons_parent = cons_section.find_parent()
                if cons_parent:
                    next_elem = cons_parent.find_next_sibling()
                    if next_elem:
                        review_data['cons'] = next_elem.get_text(strip=True)
            
            # Extract improvement suggestions
            suggestions_section = review_element.find(string=lambda x: x and 'Verbesserungsvorschläge' in str(x))
            if suggestions_section:
                suggestions_parent = suggestions_section.find_parent()
                if suggestions_parent:
                    next_elem = suggestions_parent.find_next_sibling()
                    if next_elem:
                        review_data['suggestions'] = next_elem.get_text(strip=True)
            
            # Extract category ratings (Arbeitsatmosphäre, Work-Life-Balance, etc.)
            categories = [
                'Arbeitsatmosphäre', 'Image', 'Work-Life-Balance', 
                'Karriere/Weiterbildung', 'Gehalt/Sozialleistungen',
                'Umwelt-/Sozialbewusstsein', 'Kollegenzusammenhalt',
                'Umgang mit älteren Kollegen', 'Vorgesetztenverhalten',
                'Arbeitsbedingungen', 'Kommunikation', 'Gleichberechtigung',
                'Interessante Aufgaben'
            ]
            
            for category in categories:
                # Find all h4 tags and check if any contains the category name
                all_h4 = review_element.find_all('h4')
                for h4 in all_h4:
                    h4_text = h4.get_text(strip=True)
                    if category in h4_text:
                        # Found the category! Now get its parent container
                        cat_container = h4.find_parent()
                        if cat_container:
                            # Look for the text comment (usually in a <p> tag - could be sibling or child)
                            comment_p = cat_container.find('p')
                            if comment_p:
                                comment_text = comment_p.get_text(strip=True)
                                if comment_text and comment_text not in ['Flex', '== $0']:
                                    review_data['categories'][category] = comment_text
                            
                            # Now look for the rating span with data-score attribute
                            # Strategy 1: Look in the next sibling div (scoreBlock)
                            rating_span = None
                            next_sibling = h4.find_next_sibling('div')
                            if next_sibling:
                                rating_span = next_sibling.find('span', attrs={'data-score': True})
                            
                            # Strategy 2: If not found, look in parent's next sibling
                            if not rating_span and cat_container:
                                parent_next = cat_container.find_next_sibling('div')
                                if parent_next:
                                    rating_span = parent_next.find('span', attrs={'data-score': True})
                            
                            # Strategy 3: Look within the whole category container
                            if not rating_span:
                                # Search within a broader scope
                                rating_span = cat_container.find_next('span', attrs={'data-score': True})
                            
                            if rating_span:
                                data_score = rating_span.get('data-score')
                                if data_score:
                                    # ONLY accept INTEGER scores (1, 2, 3, 4, 5)
                                    # Reject decimal scores like "4.5" (those are overall ratings, not category ratings)
                                    try:
                                        # Check if it's a valid integer string (no decimal point)
                                        if '.' in data_score or ',' in data_score:
                                            print(f"  ⚠ {category}: data-score={data_score} diabaikan (desimal bukan rating kategori)")
                                        else:
                                            score_int = int(data_score)
                                            # Validate range (must be 1-5)
                                            if 1 <= score_int <= 5:
                                                review_data['category_ratings'][category] = str(score_int)
                                                print(f"  ✓ {category}: data-score={data_score} → {score_int} bintang")
                                            else:
                                                print(f"  ⚠ {category}: data-score={data_score} diabaikan (nilai tidak valid)")
                                    except ValueError:
                                        # If can't convert to int, skip it
                                        print(f"  ⚠ {category}: data-score={data_score} diabaikan (bukan integer)")
                            else:
                                print(f"  ✗ {category}: tidak ditemukan rating")
                        break  # Found this category, move to next one
            
        except Exception as e:
            print(f"Error extracting review data: {e}")
        
        return review_data
    
    def scrape_page_with_requests(self, page_num=1):
        """Scrape a single page using requests (no browser needed)"""
        if page_num == 1:
            url = self.base_url
        else:
            url = f"{self.base_url}/{page_num}"
        
        print(f"Scraping page {page_num}: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all review elements
            reviews = soup.find_all('article') or soup.find_all('div', class_=lambda x: x and 'review' in str(x).lower())
            
            if not reviews:
                # Alternative method - find by data attributes or other patterns
                reviews = soup.find_all(attrs={'data-testid': lambda x: x and 'review' in str(x).lower()})
            
            print(f"Found {len(reviews)} reviews on page {page_num}")
            
            for review in reviews:
                review_data = self.scrape_review(review)
                if review_data['title']:  # Only add if we got some data
                    self.reviews_data.append(review_data)
            
            return len(reviews) > 0  # Return True if reviews found
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            return False
    
    def scrape_page(self, page_num=1):
        """Scrape a single page of reviews"""
        if page_num == 1:
            url = self.base_url
        else:
            url = f"{self.base_url}/{page_num}"
        
        print(f"Scraping page {page_num}: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(2)  # short initial wait for the page to start loading

            # Human-verification detection: if a header like
            # <h1 ...>Let's confirm you are human</h1> appears, wait 5 seconds
            # to let the user solve it. Allow up to 2 attempts (2 "lives").
            attempts = 0
            max_attempts = 2
            while attempts < max_attempts:
                page_src = (self.driver.page_source or "").lower()
                # Look for a short identifying phrase rather than exact style
                if "confirm you are human" in page_src or "let's confirm you are human" in page_src or "lets confirm you are human" in page_src:
                    attempts += 1
                    print(f"Human verification detected. Waiting 10 seconds (attempt {attempts}/{max_attempts}) for you to solve it...")
                    time.sleep(10)
                    # After waiting, re-load the page source to check if cleared
                    page_src = (self.driver.page_source or "").lower()
                    if "confirm you are human" in page_src:
                        if attempts < max_attempts:
                            print("Verification still present. Refreshing the page and will wait again.")
                            try:
                                self.driver.refresh()
                            except Exception:
                                pass
                            time.sleep(2)
                            continue
                        else:
                            print("Verification still present after 2 attempts. Skipping this page.")
                            return False
                    else:
                        print("Verification cleared. Continuing scraping.")
                        break
                else:
                    break

            # Close cookie banner on first page
            if page_num == 1:
                self.close_cookie_banner()

            # Scroll multiple times to trigger lazy loading
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Click all "show stars" buttons to reveal hidden ratings
            self.click_show_stars_buttons()

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all review elements - try multiple selectors
            reviews = soup.find_all('article') 
            
            if not reviews:
                reviews = soup.find_all('div', class_=lambda x: x and 'review' in str(x).lower())
            
            if not reviews:
                # Alternative method - find by data attributes or other patterns
                reviews = soup.find_all(attrs={'data-testid': lambda x: x and 'review' in str(x).lower()})
            
            if not reviews:
                # Try finding divs that contain review-like content
                reviews = soup.find_all('div', class_=lambda x: x and ('index__' in str(x) or 'card' in str(x).lower()))
            
            print(f"Found {len(reviews)} review elements on page {page_num}")
            
            for review in reviews:
                review_data = self.scrape_review(review)
                if review_data['title']:  # Only add if we got some data
                    self.reviews_data.append(review_data)
            
            return len(reviews) > 0  # Return True if reviews found
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            return False
    
    def scrape_all_pages(self, max_pages=5):
        """Scrape multiple pages of reviews"""
        print(f"Starting to scrape up to {max_pages} pages...")
        
        if self.use_selenium:
            try:
                self.setup_driver()
            except Exception as e:
                print(f"\n⚠ Selenium failed to start. Switching to requests method...")
                print("This method doesn't require Chrome or ChromeDriver.")
                self.use_selenium = False
        
        try:
            for page_num in range(1, max_pages + 1):
                if self.use_selenium:
                    success = self.scrape_page(page_num)
                else:
                    success = self.scrape_page_with_requests(page_num)
                
                if not success:
                    print(f"No more reviews found at page {page_num}. Stopping.")
                    break
                
                # Be respectful - add delay between pages
                if page_num < max_pages:
                    print("Waiting 3 seconds before next page...")
                    time.sleep(3)
            
        finally:
            if self.driver:
                self.driver.quit()
                print("WebDriver closed")
        
        print(f"Total reviews scraped: {len(self.reviews_data)}")
    
    def save_to_json(self, filename='outputs/reviews.json'):
        """Save scraped data to JSON file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.reviews_data, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, filename='outputs/reviews.csv'):
        """Save scraped data to CSV file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.reviews_data:
            print("No data to save!")
            return
        
        # Flatten the nested categories dictionary
        flattened_data = []
        for review in self.reviews_data:
            flat_review = {
                'title': review['title'],
                'rating': review['rating'],
                'recommendation': review['recommendation'],
                'date': review['date'],
                'position': review['position'],
                'department': review['department'],
                'location': review['location'],
                'pros': review['pros'],
                'cons': review['cons'],
                'suggestions': review['suggestions']
            }
            # Add category text comments as separate columns
            for cat_name, cat_value in review['categories'].items():
                flat_review[f"{cat_name}_comment"] = cat_value
            
            # Add category ratings as separate columns with '_rating' suffix
            for cat_name, cat_rating in review.get('category_ratings', {}).items():
                flat_review[f"{cat_name}_rating"] = cat_rating
            
            flattened_data.append(flat_review)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(flattened_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"Data saved to {filename}")
    
    def save_to_excel(self, filename='outputs/reviews.xlsx'):
        """Save scraped data to Excel file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.reviews_data:
            print("No data to save!")
            return
        
        # Flatten the nested categories dictionary
        flattened_data = []
        for review in self.reviews_data:
            flat_review = {
                'title': review['title'],
                'rating': review['rating'],
                'recommendation': review['recommendation'],
                'date': review['date'],
                'position': review['position'],
                'department': review['department'],
                'location': review['location'],
                'pros': review['pros'],
                'cons': review['cons'],
                'suggestions': review['suggestions']
            }
            # Add category text comments as separate columns
            for cat_name, cat_value in review['categories'].items():
                flat_review[f"{cat_name}_comment"] = cat_value
            
            # Add category ratings as separate columns with '_rating' suffix
            for cat_name, cat_rating in review.get('category_ratings', {}).items():
                flat_review[f"{cat_name}_rating"] = cat_rating
            
            flattened_data.append(flat_review)
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(flattened_data)
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"Data saved to {filename}")


def main():
    """Main function to run the scraper"""
    print("=" * 60)
    print("Kununu Scraper - Deutsche Post & DHL Reviews")
    print("=" * 60)
    
    # Base URL
    base_url = "https://www.kununu.com/de/deutsche-post/kommentare"
    
    # Always use Selenium
    print("\nSelenium mode is enabled (Chrome browser required)")
    use_selenium = True

    # Create scraper instance
    scraper = KununuScraper(base_url, use_selenium=use_selenium)

    # Scrape reviews (adjust max_pages as needed)
    max_pages = int(input("\nHow many pages to scrape? (Enter number, e.g., 5): ") or "5")
    scraper.scrape_all_pages(max_pages=max_pages)

    # Prepare output folder name
    today_str = datetime.now().strftime("%d%m%Y")
    folder_name = f"outputs/{today_str} - {max_pages} pages"
    os.makedirs(folder_name, exist_ok=True)

    # Save data in multiple formats in the new folder
    if scraper.reviews_data:
        print("\nSaving data...")
        scraper.save_to_json(filename=os.path.join(folder_name, "reviews.json"))
        scraper.save_to_csv(filename=os.path.join(folder_name, "reviews.csv"))
        scraper.save_to_excel(filename=os.path.join(folder_name, "reviews.xlsx"))

        print("\n" + "=" * 60)
        print(f"✓ Scraping completed successfully!")
        print(f"✓ Total reviews collected: {len(scraper.reviews_data)}")
        print(f"✓ Check the '{folder_name}' folder for results")
        print("=" * 60)
    else:
        print("\n⚠ No data was scraped. Please check the website structure or try again.")


if __name__ == "__main__":
    main()
