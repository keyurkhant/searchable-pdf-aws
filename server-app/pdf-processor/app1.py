import time

from flask import Flask, render_template, request, redirect, url_for, send_file
import boto3
import os
import uuid
import requests
import fitz
import io
import json
from processor import make_pdf_doc_searchable

from pathlib import Path
app = Flask(__name__)
aws_access_key_id = ""
aws_secret_access_key = ""
_id = None  # Initialize _id to None

@app.route('/document')
def index():
    return render_template('frontend_view.html', message="")

@app.route('/upload', methods=['POST'])
def upload():
    global _id
    print("Here")
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        files = {"file": file}


        # Check if the file is a PDF
        if file.filename.lower().endswith('.pdf'):
            file_path = os.path.join('.', file.filename)
            file.save(file_path)

            s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            bucket_name = "input-pdf-documents-b00935171-a"
            global _id
            _id = uuid.uuid4()
            print(_id)
            file_name_at_bucket = "input-" + str(_id) + ".pdf"
            # files = {'file': (file.name, file, 'application/pdf')}

            # result = requests.post(api_url, headers=headers, files=files)

            s3.upload_file(file_path, bucket_name, file_name_at_bucket)

            # Redirect to the download page with the generated _id
            time.sleep(
                5
            )
            return render_template('message.html', message="Searchable File successfully Processed")

        else:
            return 'Invalid file format. Please upload a PDF file.'

    return 'Invalid request'

@app.route('/download', methods=['GET'])
def download():
    try:

        file_url = f"https://output-pdf-documents-b00935171-a.s3.amazonaws.com/output-{_id}.pdf"
        return redirect(file_url)


    except Exception as e:
        print(e)
        return render_template('frontend_view.html', message="")

@app.route('/pdf-process', methods=['POST'])
def pdfProcessor():
    input_pdf = request.files['pdf']
    processed_json = request.files['json']

    pdf_path = '/tmp/input.pdf'
    json_path = '/tmp/response.json'

    input_pdf.save(pdf_path)
    processed_json.save(json_path)

    with open(json_path) as file:
        data = json.load(file)
    textract_blocks = data["Blocks"]

    doc = fitz.open(pdf_path)
    print("DOC===>", doc)

    selectable_pdf_doc = make_pdf_doc_searchable(
    pdf_doc=doc,
    textract_blocks=textract_blocks,
    add_word_bbox=True,
    show_selectable_char=False,
    pdf_image_dpi=200,
    verbose=True)

    print("HERE===>", selectable_pdf_doc)

    pdf_bytes = selectable_pdf_doc.tobytes()
    output_pdf_stream = io.BytesIO(pdf_bytes)
    output_pdf_stream.seek(0)
    global _id
    file_name_at_bucket = "output-" + str(_id) + ".pdf"
    # send_file(output_pdf_stream, mimetype='application/pdf', as_attachment=True, download_name=file_name_at_bucket)

    return send_file(output_pdf_stream, mimetype='application/pdf', as_attachment=True, download_name=file_name_at_bucket)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)
