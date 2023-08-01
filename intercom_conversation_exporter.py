import requests
import json
import csv
import html2text
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Load your access token from environment variables
access_token = os.getenv("ACCESS_TOKEN")

API_URL = "https://api.intercom.io/conversations"

def send_request(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {url}")
        print("Response:", response.text)
        return None

def fetch_conversations(starting_after=None):
    url = f"{API_URL}?per_page=150"
    if starting_after:
        url += f"&starting_after={starting_after}"
    headers = {"Accept": "application/json", 'Authorization': f'Bearer {access_token}'}
    data = send_request(url, headers)
    if data is not None:
        next_page_info = data.get('pages', {}).get('next')
        next_starting_after = next_page_info['starting_after'] if next_page_info else None
        return data, next_starting_after
    else:
        return None, None

def fetch_conversation_details(conv_id):
    url = f"{API_URL}/{conv_id}"
    headers = {"Accept": "application/json", 'Authorization': f'Bearer {access_token}'}
    return send_request(url, headers)

def parse_conversation(conversation):
    customer_name = conversation['source']['author']['name']
    customer_email = conversation['source']['author']['email']
    company = conversation['source']['author'].get('companies', {}).get('name', 'N/A') if 'companies' in conversation['source']['author'] else 'N/A'
    conversation_id = conversation['id']
    created_at = datetime.fromtimestamp(conversation['created_at']).isoformat()
    closed_at = datetime.fromtimestamp(conversation['statistics']['last_close_at']).isoformat() if conversation['statistics']['last_close_at'] else 'N/A'
    conversation_rating = conversation.get('conversation_rating', {}).get('rating') if conversation.get('conversation_rating') else 'N/A'

    # Initialize a list to store conversation thread
    conversation_thread = []

    # HTML to text converter
    converter = html2text.HTML2Text()
    converter.ignore_links = True

    conversation_parts = conversation['conversation_parts']['conversation_parts']
    for part in conversation_parts:
        if 'body' in part and part['body'] is not None:
            # Remove HTML formatting
            message = converter.handle(part['body']).strip()
            if part['author']['type'] == 'user':
                conversation_thread.append(f"Customer: {message}")
            elif part['author']['type'] == 'admin':
                conversation_thread.append(f"Admin: {message}")

    conversation_details = {
        'conversation_id': conversation_id,
        'customer_name': customer_name,
        'customer_email': customer_email,
        'company': company,
        'created_at': created_at,
        'closed_at': closed_at,
        'conversation_rating': conversation_rating,
        'conversation_thread': conversation_thread
    }

    return conversation_details

def export_conversations_to_csv(threads=10):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        with open('intercom_conversations.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Conversation ID", "Customer Name", "Email", "Company", "Created At", "Closed At", "Rating", "Conversation Thread"])

            starting_after = None
            total_conversations = 0  # Initialize a counter for the total number of conversations
            while True:
                print(f"Fetching conversations starting after {starting_after}" if starting_after else "Fetching first page of conversations")
                data, last_id = fetch_conversations(starting_after)
                if not data:
                    break

                conversations = data.get('conversations')
                if not conversations:
                    break

                future_details = {executor.submit(fetch_conversation_details, conv['id']): conv for conv in conversations}

                for future in future_details:
                    details = future.result()

                    if details:
                        parsed_details = parse_conversation(details)
                        conversation_id = parsed_details['conversation_id']
                        customer_name = parsed_details['customer_name']
                        customer_email = parsed_details['customer_email']
                        company = parsed_details['company']
                        created_at = parsed_details['created_at']
                        closed_at = parsed_details['closed_at']
                        conversation_rating = parsed_details['conversation_rating']
                        conversation_thread = '\n'.join(parsed_details['conversation_thread'])

                        writer.writerow([conversation_id, customer_name, customer_email, company, created_at, closed_at, conversation_rating, conversation_thread])
                        total_conversations += 1  # Increment the counter each time a conversation is processed successfully

                starting_after = last_id  # Set starting_after to the last conversation ID on the current page

                if not starting_after or len(conversations) < 150:
                    break  # No more conversations to fetch

            print(f"Completed fetching conversations")
            print(f"Total conversations processed: {total_conversations}")  # Print the total number of conversations processed


if __name__ == "__main__":
    export_conversations_to_csv(threads=10)
