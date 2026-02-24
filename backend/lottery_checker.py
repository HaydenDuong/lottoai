# backend/lottery_checker.py
"""
Lottery Prize Checking Module
Fetches winning numbers from PostgreSQL and checks user numbers against them.
"""

from typing import Dict, List, Any, Optional
from fastapi import HTTPException
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# ========== Database Helper ==========
def get_db_connection():
    """
    Establish connection to PostgreSQL database
    Returns: psycopg2.connection
    Raises: HTTPException if connection fails
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT")),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")

# Function for extracting stored winning numbers in Docker PosrgreSQL & format them into dictionary input for running prize_check function
def fetch_winning_numbers(draw_date: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch winning numbers from database and return in algorithm-compatible format
    
    Args:
        draw_date: Optional specific date (YYYY-MM-DD), defaults to latest
        region: Optional region filter (e.g., 'hcm')
    
    Returns:
        Dictionary matching algor_test.py structure:
        {
            "8": "51",
            "7": "517",
            "6": ["9515", "2694", "3761"],
            ...
        }
    
    Raises:
        HTTPException: If no winning numbers found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with optional filters
        query = """
            SELECT
                prize_8, prize_7, prize_6, prize_5, prize_4,
                prize_3, prize_2, prize_1, jp_consolation, jp,
                draw_date, region
            FROM winning_numbers
        """
        
        clauses = []
        params = []
        
        if draw_date:
            clauses.append("draw_date = %s")
            params.append(draw_date)
        
        if region:
            clauses.append("region = %s")
            params.append(region)
        
        # If both are provided, 'clauses' becomes ["draw_date = %s", "region = %s"]
        # query += " WHERE " + " AND ".join(clauses) will yield:
        # SELECT ... FROM winning_numbers WHERE draw_date = %s AND region = %s
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        
        query += " ORDER BY draw_date DESC LIMIT 1"
        
        # This will passing in the values being stored in params into %s of draw_date & region
        cursor.execute(query, tuple(params))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=404,
                detail="No winning numbers found for the specific criteria"
            )
        
        # Map to dictionary matching algor_test.py structure
        winning_numbers = {
            "8": row[0],
            "7": row[1],
            "6": row[2] if row[2] else [],
            "5": row[3],         
            "4": row[4] if row[4] else [],  
            "3": row[5] if row[5] else [],  
            "2": row[6],           
            "1": row[7],           
            "jp-consolation": row[8],  
            "jp": row[9]          
        }
        
        metadata = {
            "draw_date": row[10].isoformat() if row[10] else None,      #.isoformat() converts draw_date value to a string for JSON response
            "region": row[11]
        }
        
        print(f"Fetched winning numbers for draw: {metadata['draw_date']} ({metadata['region']})")
        
        return winning_numbers, metadata
    
    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ========== Algorithm Function ==========
def reverse_number_order(number: str) -> str:
    """Reverse the order of a number string"""
    return ''.join(reversed(number))


def extracting_prize_section(winning_numbers: Dict, position_list: List[str]) -> List[Dict]:
    """
    Extract and reverse winning numbers for specific prize positions
    
    Args:
        winning_numbers: Dict of prize tiers
        position_list: List of prize tier keys to extract
    
    Returns:
        List of dicts with reversed winning numbers
    """
    extracted_prize_list = []
    
    for position in position_list:
        reversed_winning_number_list = []
        
        value = winning_numbers[position]
        
        # Handle single string
        if isinstance(value, str):
            reversed_winning_number = ''.join(reversed(value))
            reversed_winning_number_list.append(reversed_winning_number)
        
        # Handle list
        elif isinstance(value, list):
            for winning_number in value:
                reversed_winning_number = ''.join(reversed(winning_number))
                reversed_winning_number_list.append(reversed_winning_number)
        
        extracted_prize_list.append({position: reversed_winning_number_list})
    
    return extracted_prize_list


def finding_prize_section(extracted_reversed_list: List[Dict], reversed_userNum: str, total_num: int) -> List[str]:
    """
    Find which prize sections match the user's number
    
    Args:
        extracted_reversed_list: Reversed winning numbers by prize tier
        reversed_userNum: User's number reversed
        total_num: Number of digits to check
    
    Returns:
        List of matching prize tier keys
    """
    target = reversed_userNum[:total_num]
    
    keyfound = [
        key
        for d in extracted_reversed_list
        for key, value in d.items()
        if target in value  # Exact match in list
    ]
    
    return keyfound


def prize_check(winning_numbers: Dict, user_num: str, winned_prize: List[str]):
    """
    Check user number against all prize tiers
    
    Args:
        winning_numbers: Dict of winning numbers
        user_num: User's lottery number
        winned_prize: List to append matched prize tiers (modified in place)
    """
    reversed_userNum = reverse_number_order(user_num)
    position_list = list(winning_numbers.keys())
    extracted_reversed_list = extracting_prize_section(winning_numbers, position_list)
    
    # Check from 2 digits up to full length
    for i in range(2, len(user_num) + 1):
        key_found = finding_prize_section(extracted_reversed_list, reversed_userNum, i)
        
        if key_found:
            winned_prize.extend(key_found)
    
    # Remove jp-consolation if user also won jackpot
    if ('jp-consolation' in winned_prize) and ('jp' in winned_prize):
        winned_prize.remove('jp-consolation')


# ==================== Main Public Function ====================

def check_user_prizes(user_number: str, draw_date: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to check if user's number wins any prizes
    
    Args:
        user_number: User's lottery number as string
        draw_date: Optional specific draw date
        region: Optional region filter
    
    Returns:
        {
            "user_number": "127333",
            "matched_prizes": ["4"],
            "is_winner": true,
            "draw_info": {
                "draw_date": "2025-01-15",
                "region": "hcm"
            }
        }
    """
    # Fetch winning numbers from database
    winning_numbers, metadata = fetch_winning_numbers(draw_date, region)
    
    # Run prize checking algorithm
    winned_prize = []
    prize_check(winning_numbers, user_number, winned_prize)
    
    # Build response
    result = {
        "user_number": user_number,
        "matched_prizes": winned_prize,
        "is_winner": len(winned_prize) > 0,
        "draw_info": metadata
    }
    
    print(f"Prize check result: {user_number} → {winned_prize}")
    
    return result