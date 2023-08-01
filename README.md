# Intercom Conversations Exporter

This Python script fetches conversations from the Intercom API, processes the information, and exports it into a CSV file. The output includes Conversation ID, Customer Name, Email, Company, Created At, Closed AT, Rating, and the full conversation thread. Many other fields are available, you can reference the documentation at [https://developers.intercom.com/](https://developers.intercom.com/)

## Prerequisites

To run this script, you will need:

- Python 3.7 or higher
- The `requests`, `json`, `csv`, `html2text` and `concurrent.futures` libraries. If not already installed, you can install them using pip:

```bash
pip install requests html2text
```

- An Intercom Access Token. You can generate this from your Intercom dashboard (Settings > Developers > Access Tokens)

## Configuration

Set your Intercom Access Token as an environment variable. This can be done in the terminal before you run your script:

```bash
export ACCESS_TOKEN=<your_access_token>
```

Replace `<your_access_token>` with your actual Intercom Access Token.

## Running the script

1. Open the terminal.
2. Navigate to the directory where your script is located:

   ```bash
   cd /path/to/your/directory
   ```

3. Run the script:

   ```bash
   python intercom_conversation_exporter.py
   ```

This will create a CSV file named `intercom_conversations.csv` in the same directory.

## Notes

- Be aware of rate limits when making requests to the Intercom API. The current rate limit is 500 requests per minute.
- This script uses a default of 100 threads for fetching conversation details concurrently. If you encounter issues with this, you can adjust the number of threads by changing the parameter in the call to `export_conversations_to_csv(threads=100)` at the bottom of the script.

## Support

If you encounter any issues, please open an issue on GitHub.
