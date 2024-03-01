# Alfresco Watermark Tool

This tool can be used to watermark PDF documents in an Alfresco share. It downloads PDF files from the given target node, watermarks them with the user-supplied watermark (must be a PDF file) and upload the files back to Alfresco.

## Installation

Install all required dependencies:
`pip3 install -r  requirements.txt`

Create a `.env` file and fill it. See `.env.example` what it could look like.

## Running the tool

Run the tool with your IDE of choosing or in the terminal with `python3 main.py`
