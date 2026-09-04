from flask import Flask, render_template, request, jsonify, send_file
from fpdf import FPDF
import qrcode
import os

app = Flask(__name__)

# Ensure ek folder ho jahan PDF save hongi
if not os.path.exists('certificates'):
    os.makedirs('certificates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def check_weight():
    data = request.json
    shop_name = data.get('shop_name', 'Unknown Shop')
    standard = float(data['standard'])
    reading = float(data['reading'])

    error = abs(standard - reading)
    allowed_error = 2.0 

    if error <= allowed_error:
        status = "PASS"
        color = "green"
        # Generate QR Code
        qr_data = f"Verified: {shop_name} | Error: {error}g | Status: PASS"
        img = qrcode.make(qr_data)
        img.save("certificates/qr.png")

        # Generate Official PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="GOVERNMENT OF INDIA - LEGAL METROLOGY", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Verification Certificate (OIML R-76)", ln=True, align='C')
        pdf.line(10, 30, 200, 30)
        
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Shop/Entity Name: {shop_name}", ln=True)
        pdf.cell(200, 10, txt=f"Standard Weight Applied: {standard} g", ln=True)
        pdf.cell(200, 10, txt=f"Machine Reading: {reading} g", ln=True)
        pdf.cell(200, 10, txt=f"Detected Error: {error} g", ln=True)
        pdf.cell(200, 10, txt="Result: APPROVED & STAMPED", ln=True)
        
        # QR code image ko PDF mein dalna
        pdf.image("certificates/qr.png", x=150, y=50, w=30)
        
        pdf_path = f"certificates/{shop_name}_Certificate.pdf"
        pdf.output(pdf_path)
        
        pdf_url = f"/download/{shop_name}_Certificate.pdf"
    else:
        status = "FAIL - Seized under Sec 25"
        color = "red"
        pdf_url = None

    return jsonify({"status": status, "error": error, "color": color, "pdf_url": pdf_url})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(f"certificates/{filename}", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8080)