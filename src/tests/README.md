# Project Testing Directory

This directory contains configuration scripts and test cases to verify the `BookingAssistant_bot` architecture.

## How to Run System Tests
1. Ensure your `.env` file is fully configured.
2. Run python unit tests using:
   ```bash
   python -m unittest discover -s src/tests -p "*.py"