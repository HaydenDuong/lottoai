# backend/lottery_scraper.py
"""
Web scraper for Minh Ngoc lottery results
Scrapes all provinces from daily draw (3 separate tables)
"""
import logging
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()     # Output to console
    ]
)

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def scrape_lottery_results() -> List[Dict]:
    """
    Scrape lottery results from Minh Ngoc
    Returns list of dictionaries (one per province)
    """
    url = "https://www.minhngoc.net.vn/free/index.php"
    
    try:
        logger.info(f"[{datetime.now()}] Fetching lottery results from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the date from <td class="ngay">
        date_cell = soup.find('td', class_='ngay')
        draw_date = datetime.now().date()
        
        if date_cell:
            date_text = date_cell.get_text(strip=True)
            try:
                draw_date = datetime.strptime(date_text, "%d/%m/%Y").date()
                logger.info(f"Draw date: {draw_date}")
                logger.info(f"Successfully scraped {len(results)} provinces")
            except:
                logger.warning(f"Could not parse date '{date_text}', using today")
        
        # Find the main container table
        main_table = soup.find('table', class_='bkqmiennam')
        
        if not main_table:
            logger.error("Error: Could not find main lottery table (bkqmiennam)")
            return []
        
        # Find all 'rightcl' tables within the main table (these are the province tables)
        province_tables = main_table.find_all('table', class_='rightcl')
        
        logger.info(f"Found {len(province_tables)} province tables inside bkqmiennam")
        
        if not province_tables:
            logger.error("Error: Could not find province tables (rightcl)")
            return []
        
        results = []
        
        # Process each table (each represents one province)
        for idx, table in enumerate(province_tables):
            logger.info(f"Processing table {idx + 1}...")
            province_data = extract_province_data(table, draw_date)
            
            if province_data:
                results.append(province_data)
            else:
                logger.error(f"Failed to extract data from table {idx + 1}")
        
        logger.info(f"Successfully scraped {len(results)} provinces")
        return results
        
    except requests.RequestException as e:
        logger.error(f"Network error: {e}")
        return []
    
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_province_data(table, draw_date) -> Optional[Dict]:
    """
    Extract lottery data from a single province table
    """
    try:
        tbody = table.find('tbody')
        if not tbody:
            return None
        
        # Extract province name from <td class="tinh">
        province_cell = tbody.find('td', class_='tinh')
        if not province_cell:
            return None
        
        province_name = province_cell.get_text(strip=True)
        
        # Initialize prize data
        prize_data = {
            'province': province_name,
            'draw_date': draw_date,
            'prize_8': None,
            'prize_7': None,
            'prize_6': [],
            'prize_5': None,
            'prize_4': [],
            'prize_3': [],
            'prize_2': None,
            'prize_1': None,
            'jp': None
        }
        
        # Extract prizes using class names
        # Each prize is in a <td class="giai8">, <td class="giai7">, etc.
        # Numbers are in <div class="giaiSo" data="...">
        
        # Prize 8 (single number)
        prize_data['prize_8'] = extract_single_number(tbody, 'giai8')
        
        # Prize 7 (single number)
        prize_data['prize_7'] = extract_single_number(tbody, 'giai7')
        
        # Prize 6 (multiple numbers)
        prize_data['prize_6'] = extract_multiple_numbers(tbody, 'giai6')
        
        # Prize 5 (single number)
        prize_data['prize_5'] = extract_single_number(tbody, 'giai5')
        
        # Prize 4 (multiple numbers)
        prize_data['prize_4'] = extract_multiple_numbers(tbody, 'giai4')
        
        # Prize 3 (multiple numbers)
        prize_data['prize_3'] = extract_multiple_numbers(tbody, 'giai3')
        
        # Prize 2 (single number)
        prize_data['prize_2'] = extract_single_number(tbody, 'giai2')
        
        # Prize 1 (single number)
        prize_data['prize_1'] = extract_single_number(tbody, 'giai1')
        
        # Jackpot (single number)
        prize_data['jp'] = extract_single_number(tbody, 'giaidb')
        
        # Calculate jp_consolation (last 5 digits of jackpot)
        if prize_data['jp'] and len(prize_data['jp']) >= 5:
            prize_data['jp_consolation'] = prize_data['jp'][-5:]
        else:
            prize_data['jp_consolation'] = None
        
        return prize_data
        
    except Exception as e:
        logger.error(f"Error extracting province data: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_single_number(tbody, class_name: str) -> Optional[str]:
    """
    Extract a single number from <td class="...">
    Numbers are directly in the cell, not in <div> tags
    """
    try:
        cell = tbody.find('td', class_=class_name)
        if not cell:
            return None
        
        # Get all text from the cell, clean it
        text = cell.get_text(strip=True)
        
        # Remove any non-digit characters except spaces
        # (in case there are multiple numbers, we'll take the first)
        numbers = [num.strip() for num in text.split() if num.strip().isdigit()]
        
        if numbers:
            return numbers[0]  # Return first number
        
        return None
    except Exception as e:
        logger.error(f"Error extracting {class_name}: {e}")
        return None


def extract_multiple_numbers(tbody, class_name: str) -> List[str]:
    """
    Extract multiple numbers from <td class="...">
    Numbers might be concatenated without spaces, so we split by expected length
    """
    try:
        cell = tbody.find('td', class_=class_name)
        if not cell:
            return []
        
        # Get all text from the cell and remove all whitespace
        text = ''.join(cell.get_text(strip=True).split())
        
        # Remove any non-digit characters
        text = ''.join(c for c in text if c.isdigit())
        
        if not text:
            return []
        
        # Determine the digit length based on prize type
        # Prize 6 = 4 digits each
        # Prize 4 = 5 digits each
        # Prize 3 = 5 digits each
        if class_name == 'giai6':
            digit_length = 4
        elif class_name in ['giai4', 'giai3']:
            digit_length = 5
        else:
            # Unknown prize type, try to split by spaces if available
            return [text]
        
        # Split the continuous string into chunks of the correct length
        numbers = []
        for i in range(0, len(text), digit_length):
            chunk = text[i:i+digit_length]
            if len(chunk) == digit_length:  # Only add complete numbers
                numbers.append(chunk)
        
        return numbers
        
    except Exception as e:
        logger.error(f"Error extracting {class_name}: {e}")
        return []


def save_to_database(lottery_data: Dict) -> bool:
    """
    Insert lottery data into PostgreSQL
    Returns True if successful, False otherwise
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if this draw already exists (prevent duplicates)
        cursor.execute("""
            SELECT id FROM winning_numbers 
            WHERE draw_date = %s AND region = %s
        """, (lottery_data['draw_date'], lottery_data['province']))
        
        existing = cursor.fetchone()
        
        if existing:
            logger.info(f"Draw for {lottery_data['province']} on {lottery_data['draw_date']} already exists. Skipping.")
            return False
        
        # Insert new draw
        cursor.execute("""
            INSERT INTO winning_numbers 
            (prize_8, prize_7, prize_6, prize_5, prize_4, prize_3, prize_2, prize_1, jp_consolation, jp, draw_date, region)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            lottery_data['prize_8'],
            lottery_data['prize_7'],
            lottery_data['prize_6'],  # Array
            lottery_data['prize_5'],
            lottery_data['prize_4'],  # Array
            lottery_data['prize_3'],  # Array
            lottery_data['prize_2'],
            lottery_data['prize_1'],
            lottery_data['jp_consolation'],
            lottery_data['jp'],
            lottery_data['draw_date'],
            lottery_data['province']
        ))
        
        conn.commit()
        logger.info(f"Saved {lottery_data['province']} draw for {lottery_data['draw_date']}")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def scrape_and_save():
    """
    Main function: scrape results and save to database
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting lottery scraper - {datetime.now()}")
    logger.info(f"{'='*60}\n")
    
    # Scrape results
    results = scrape_lottery_results()
    
    if not results:
        logger.error("No results to save")
        return
    
    # Debug: print what we scraped
    for result in results:
        logger.info(f"\n{result['province']} - {result['draw_date']}")
        logger.info(f"   Prize 8: {result['prize_8']}")
        logger.info(f"   Prize 7: {result['prize_7']}")
        logger.info(f"   Prize 6: {result['prize_6']}")
        logger.info(f"   Prize 5: {result['prize_5']}")
        logger.info(f"   Prize 4: {result['prize_4']}")
        logger.info(f"   Prize 3: {result['prize_3']}")
        logger.info(f"   Prize 2: {result['prize_2']}")
        logger.info(f"   Prize 1: {result['prize_1']}")
        logger.info(f"   Jackpot: {result['jp']}")
        logger.info(f"   JP Consolation: {result['jp_consolation']}")
    
    # Save each province's results
    success_count = 0
    for province_data in results:
        if save_to_database(province_data):
            success_count += 1
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Scraping complete: {success_count}/{len(results)} provinces saved")
    logger.info(f"{'='*60}\n")


# For manual testing
if __name__ == "__main__":
    scrape_and_save()


