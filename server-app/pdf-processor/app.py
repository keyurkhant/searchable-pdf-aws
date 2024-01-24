from flask import Flask, request, send_file
import json
import fitz
import io
from processor import make_pdf_doc_searchable


app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello from PDF Processor</h1>'

@app.route('/pdf-process', methods=['POST'])
def pdfProcessor():
    print('start')
    input_pdf = request.files['pdf']
    processed_json = request.files['json']

    print(input_pdf)
    print(processed_json)

    pdf_path = '/tmp/input.pdf'
    json_path = '/tmp/response.json'

    input_pdf.save(pdf_path)
    processed_json.save(json_path)

    with open(json_path) as file:
        data = json.load(file)
    textract_blocks = data["Blocks"]

    doc = fitz.open(pdf_path)

    selectable_pdf_doc = make_pdf_doc_searchable(
    pdf_doc=doc,
    textract_blocks=textract_blocks,
    add_word_bbox=True,
    show_selectable_char=False,
    pdf_image_dpi=200,
    verbose=True)

    pdf_bytes = selectable_pdf_doc.tobytes()

    output_pdf_stream = io.BytesIO(pdf_bytes)
    output_pdf_stream.seek(0)

    return send_file(output_pdf_stream, mimetype='application/pdf', as_attachment=True,  download_name='output.pdf')

if __name__ == "__main__":
 app.run(host='0.0.0.0', port=8000)