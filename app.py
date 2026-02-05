import streamlit as st
from fpdf import FPDF
import base64
import os
from datetime import datetime, timedelta
import tempfile
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="YH Invoice Generator",
    page_icon="📄",
    layout="wide"
)

# --- CONSTANTS ---
C_N = "Wuxi YuHuang Transmission Technology Co., Ltd"
C_A = "235-Xinzhou Road, Xinwu District, Wuxi City, Jiangsu Province, China"

SELLER_PROFILES = [
    {"name": "Imdadul Haque", "email": "imdadul@yhtransmissiontech.com", "phone": "+86-15895307823"},
    {"name": "Simon Zhang", "email": "simon@yhtransmissiontech.com", "phone": "+86-15895307753"},
    {"name": "YoYo", "email": "YoYo@yhtransmissiontech.com", "phone": "+86 153 0153 9221"}
]

MODEL_NUMBERS = [
    "YH8-520", "YH8-520S", "YH8-520P", "YH8-521", "YH8-522",
    "YH8-523D", "YH8-524E", "YH8-525", "YH8-526G", "YH8-526S",
    "YH8-527", "YH8-528", "Single Push Rod Controller",
    "2-CH Synchronous Controller", "4-CH Synchronous Controller",
    "Voltage converter", "Power Supply", "Other"
]

# Model to image mapping
MODEL_IMAGE_MAP = {
    "YH8-520": "520.png",
    "YH8-520S": "520S.png",
    "YH8-520P": "520P.png",
    "YH8-521": "521.png",
    "YH8-522": "522.png",
    "YH8-523D": "523D.png",
    "YH8-524E": "524E.png",
    "YH8-525": "525.png",
    "YH8-526G": "526G.png",
    "YH8-526S": "526S.png",
    "YH8-527": "527.png",
    "YH8-528": "528.png",
    "Voltage converter": "vconverter.png",
    "Power Supply": "psupply.png",
    "Single Push Rod Controller": "1ch.png",
    "2-CH Synchronous Controller": "2ch.png",
    "4-CH Synchronous Controller": "4ch.png"
}

SHIPPING_METHODS = ["DDP", "DAP", "FOB", "EXW", "CIF", "CFR", "FCA", "DPU", "FAS"]

# Initialize session state
if 'invoice_items' not in st.session_state:
    st.session_state['invoice_items'] = [
        {
            'model': 'YH8-527', 
            'qty': 4, 
            'price': 80.0, 
            'spec': 'Stroke: 6 inch, Load: 600 lbs',
            'image_data': None,
            'image_type': 'auto'
        }
    ]

# --- Helper Functions ---
def add_item():
    st.session_state['invoice_items'].append({
        'model': 'YH8-527', 
        'qty': 4, 
        'price': 80.0, 
        'spec': 'Stroke: 6 inch, Load: 600 lbs',
        'image_data': None,
        'image_type': 'auto'
    })

def remove_item(index):
    if len(st.session_state['invoice_items']) > 1:
        st.session_state['invoice_items'].pop(index)

def get_image_path(image_filename):
    """Get the full path for an image file"""
    # Check in current directory
    if os.path.exists(image_filename):
        return image_filename
    # Check in images folder
    if os.path.exists(f"images/{image_filename}"):
        return f"images/{image_filename}"
    # Check if file exists with different case
    for file in os.listdir():
        if file.lower() == image_filename.lower():
            return file
    # Check in images folder with different case
    if os.path.exists("images"):
        for file in os.listdir("images"):
            if file.lower() == image_filename.lower():
                return f"images/{file}"
    return None

def get_image_for_model(model_name):
    """Get the image file for a model"""
    if model_name in MODEL_IMAGE_MAP:
        image_file = MODEL_IMAGE_MAP[model_name]
        return get_image_path(image_file)
    return None

def create_pdf(invoice_data):
    """Create PDF document with all images"""
    pdf = FPDF()
    pdf.add_page()
    
    today = datetime.now()
    validity = today + timedelta(days=30)
    
    # --- HEADER IMAGES ---
    # Header image (top right)
    header_path = get_image_path("Header.png")
    if header_path and os.path.exists(header_path):
        try:
            header_width = 60  # Adjust as needed
            header_x = 210 - header_width  # Right side of A4 page (210mm width)
            pdf.image(header_path, x=header_x, y=0, w=header_width)
        except Exception as e:
            st.warning(f"Could not add header image: {e}")
    
    # Logo image (top left)
    logo_path = get_image_path("company_logo.png")
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=5, w=25)
            pdf.set_xy(45, 8)  # Move text position after logo
        except Exception as e:
            st.warning(f"Could not add logo: {e}")
            pdf.set_y(10)
    else:
        pdf.set_y(10)
    
    # --- COMPANY HEADER ---
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 112, 192)  # Blue color
    pdf.cell(0, 8, C_N, ln=1, align='C')
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(0, 0, 0)  # Black color
    pdf.cell(0, 4, C_A, ln=1, align='C')
    pdf.ln(4)
    
    # Document title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, invoice_data['doc_type'], ln=1, align='C')
    
    # Document info
    pdf.set_font("Arial", 'B', 8)
    doc_label = "Invoice Number:" if invoice_data['doc_type'] == "PROFORMA INVOICE" else "Quotation Number:"
    pdf.cell(115, 6, f" {doc_label} {invoice_data['invoice_no']}", border=1)
    cx, cy = pdf.get_x(), pdf.get_y()
    pdf.cell(75, 6, "", border=1)
    pdf.set_xy(cx, cy)
    pdf.cell(37.5, 6, f" Date : {today.strftime('%d-%b-%Y')}", border=0, align='L')
    pdf.set_xy(cx + 37.5, cy)
    pdf.cell(37.5, 6, f" Validity : {validity.strftime('%d-%b-%Y')}", border=0, align='R')
    pdf.ln(6)
    
    # --- SELLER & BUYER ---
    start_y = pdf.get_y()
    
    # Seller details
    seller_lines = [
        "Seller: Wuxi YuHuang Transmission Technology Co., Ltd.",
        f"Contact: {invoice_data['seller_contact']}",
        f"Mobile: {invoice_data['seller_phone']}",
        f"E-mail: {invoice_data['seller_email']}",
        "Address: No.235, Xinzhou Road, Xinwu District, Wuxi City, Jiangsu Province, China"
    ]
    
    pdf.set_font("Arial", '', 7.5)
    pdf.multi_cell(115, 4, "\n".join(seller_lines), border='LR')
    y1 = pdf.get_y()
    pdf.set_xy(125, start_y)
    
    # Buyer details
    buyer_lines = [
        "Ship To:",
        f"Company: {invoice_data['buyer_company']}",
        f"Contact: {invoice_data['buyer_contact']}",
        f"Tel: {invoice_data['buyer_tel']}",
        f"Address: {invoice_data['buyer_address']}"
    ]
    
    pdf.multi_cell(75, 4, "\n".join(buyer_lines), border='R')
    max_y = max(y1, pdf.get_y())
    pdf.set_xy(10, start_y)
    pdf.cell(115, max_y - start_y, "", border=1)
    pdf.set_xy(125, start_y)
    pdf.cell(75, max_y - start_y, "", border=1)
    
    pdf.set_y(max_y)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 7, f" DELIVERY TERM: {invoice_data['shipping_method']}", border=1, ln=1)
    
    # --- TABLE HEAD ---
    w = [10, 32, 28, 52, 15, 17, 17, 19]
    pdf.set_font("Arial", 'B', 7)
    
    h = ["No", "Model", "Photo", "Spec", "Qty", "Unit Price", f"Frt({invoice_data['shipping_method']})", "Total"]
    
    for i in range(8):
        pdf.cell(w[i], 7, h[i], 1, 0, 'C')
    pdf.ln(7)
    table_start_y = pdf.get_y()
    rh = 32
    
    # --- ITEM ROWS ---
    subtotal = 0
    for i, item in enumerate(invoice_data['items']):
        cy = pdf.get_y()
        qv = item['qty']
        pv = item['price']
        item_total = qv * pv
        subtotal += item_total
        
        pdf.set_font("Arial", '', 7.5)
        pdf.cell(w[0], rh, str(i+1), 1, 0, 'C')
        
        pdf.set_xy(20, cy+10)
        pdf.multi_cell(w[1], 4, item['model'], 0, 'C')
        pdf.set_xy(20, cy)
        pdf.cell(w[1], rh, "", 1)
        pdf.set_xy(52, cy)
        pdf.cell(w[2], rh, "", 1)
        
        # Add image to PDF
        try:
            image_added = False
            
            # Priority 1: Use uploaded image if available
            if item.get('image_data') and item.get('image_type') == 'uploaded':
                try:
                    # Save uploaded image to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                        tmp.write(item['image_data'].getvalue())
                        tmp_path = tmp.name
                    
                    # Add image to PDF
                    pdf.image(tmp_path, x=53, y=cy+2, w=26)
                    image_added = True
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                except Exception as e:
                    st.warning(f"Could not add uploaded image for item {i+1}: {e}")
            
            # Priority 2: Use auto image based on model
            if not image_added and item.get('image_type') == 'auto':
                image_path = get_image_for_model(item['model'])
                if image_path and os.path.exists(image_path):
                    try:
                        pdf.image(image_path, x=53, y=cy+2, w=26)
                        image_added = True
                    except Exception as e:
                        st.warning(f"Could not add auto image for item {i+1}: {e}")
            
            # If no image added, leave blank or add placeholder text
            if not image_added:
                pdf.set_xy(53, cy+rh/2-2)
                pdf.set_font("Arial", 'I', 6)
                pdf.cell(26, 4, "No Image", border=0, align='C')
                pdf.set_font("Arial", '', 7.5)
                
        except Exception as e:
            st.error(f"Error adding image: {e}")
        
        pdf.set_xy(80, cy+5)
        pdf.multi_cell(w[3], 4, item['spec'], 0, 'L')
        pdf.set_xy(80, cy)
        pdf.cell(w[3], rh, "", 1)
        pdf.set_xy(132, cy)
        pdf.cell(w[4], rh, str(int(qv)), 1, 0, 'C')
        pdf.cell(w[5], rh, f"${pv}", 1, 0, 'C')
        pdf.cell(w[6], rh, "", 0)
        pdf.cell(w[7], rh, f"${int(item_total)}", 1, 1, 'C')
    
    # Freight
    frt_val = invoice_data['freight_charge']
    pdf.set_xy(164, table_start_y)
    pdf.cell(w[6], rh * len(invoice_data['items']), f"${frt_val}", 1, 0, 'C')
    
    # --- SUMMARY ---
    pdf.set_y(table_start_y + (rh * len(invoice_data['items'])))
    grand_total = subtotal + frt_val
    
    w_meta = sum(w[:4])
    w_lbl = sum(w[4:7])
    w_val = w[7]
    
    fin_data = [
        (f"Package: {invoice_data['package']}", "SUBTOTAL", f"${int(subtotal)}"),
        (f"Lead Time: {invoice_data['lead_time']}", f"Freight Charge({invoice_data['shipping_method']})", f"${int(frt_val)}"),
        (f"Delivery Time: {invoice_data['delivery_time']}", f"GRAND TOTAL({invoice_data['shipping_method']})", f"${int(grand_total)} USD")
    ]
    
    for meta, label, value in fin_data:
        pdf.set_font("Arial", '', 7.5)
        pdf.cell(w_meta, 7, f" {meta}", 1, 0, 'L')
        is_gt = "GRAND" in label
        pdf.set_font("Arial", 'B' if is_gt else '', 7.5)
        pdf.cell(w_lbl, 7, label, 1, 0, 'R')
        pdf.cell(w_val, 7, value, 1, 1, 'C')
    
    # Terms
    terms = [
        (f"THE TOTAL AMOUNT IS {int(grand_total)} USD ONLY.", 'B', 10, 8, 'C'),
        ("PAYMENT TERM : Full Prepayment by T/T through bank, balance before shipment", '', 8, 6, 'L'),
        ("Warranty: 1 Year", '', 8, 6, 'L'),
        ("Service : Engineer supply install operation supporting by video", '', 8, 6, 'L')
    ]
    
    for term, style, size, height, align in terms:
        pdf.set_font("Arial", style, size)
        pdf.cell(190, height, f" {term}", 1, 1, align)
    
    # Bank details
    pdf.set_font("Arial", '', 7)
    x = pdf.get_x()
    y = pdf.get_y()
    pdf.cell(190, 28, "", 1, 1)
    pdf.set_xy(x, y)
    pdf.set_x(x + 2)
    
    bank_details = [
        "Beneficiary Name : Wuxi Yuhuang Transmission Technology Co., Ltd.",
        "Beneficiary account number : 3996000782763",
        "Country/Region : HongKong",
        "Swift Code : CITIHKHX or CITIHKHXXXX",
        "Beneficiary Address : 26/F., TOWER ONE, TIME SQUARE 1 MATHESON STREET CAUSEWAY BAY HK",
        "Beneficiary Bank : CITIBANK, N.A., HONG KONG BRANCH",
        "Beneficiary Bank Address : Champion Tower, Three Garden Road, Central, Hong Kong",
        "Bank Code : 006",
        "Branch Code : 391"
    ]
    
    for i, detail in enumerate(bank_details):
        pdf.cell(0, 3.0, detail, 0, 1, 'L')
    
    # --- FOOTER IMAGE ---
    # Move to bottom of page for footer
    current_y = pdf.get_y()
    
    # Add footer image if there's space
    footer_path = get_image_path("Footer.png")
    if footer_path and os.path.exists(footer_path):
        try:
            # Position footer at bottom of page
            footer_width = 80
            footer_height = 40
            footer_x = 0  # Left side
            footer_y = 321 - footer_height  # A4 page height is 297mm
            
            # Only add footer if we haven't already written too low
            if current_y < footer_y - 10:
                pdf.image(footer_path, x=footer_x, y=footer_y, w=footer_width)
        except Exception as e:
            st.warning(f"Could not add footer image: {e}")
    
    # --- SEAL IMAGE ---
    seal_path = get_image_path("company_seal.png")
    if seal_path and os.path.exists(seal_path):
        try:
            # Position seal at bottom right
            seal_width = 30
            seal_x = 150  # Right side
            
            # Calculate Y position - try to place after bank details
            seal_y = y + 17  # After bank details
            
            # Make sure it doesn't go too low
            max_y = 200  # Leave some margin at bottom
            if seal_y > max_y:
                seal_y = max_y
            
            pdf.image(seal_path, x=seal_x, y=seal_y, w=seal_width)
            
            # Add signature text
            pdf.set_font("Arial", '', 7)
            sig_y = seal_y + seal_width + 2
            pdf.set_xy(seal_x, sig_y)
            pdf.cell(seal_width, 3, "Authorized Signature", 0, 0, 'C')
            
            pdf.set_xy(seal_x, sig_y + 4)
            pdf.set_font("Arial", 'B', 7)
            pdf.cell(seal_width, 3, "Wuxi YuHuang", 0, 0, 'C')
            
            pdf.set_xy(seal_x, sig_y + 8)
            pdf.cell(seal_width, 3, "Transmission Tech Co., Ltd", 0, 0, 'C')
        except Exception as e:
            st.warning(f"Could not add seal image: {e}")
    
    return pdf

# --- MAIN APP ---
st.title("📄 YuHuang Invoice Generator")
st.markdown("Generate professional invoices with ALL images - Access from anywhere!")
st.markdown("---")

# Check for required images
st.sidebar.markdown("### 🖼️ Image Status")

required_images = {
    "Logo": "company_logo.png",
    "Header": "Header.png", 
    "Footer": "Footer.png",
    "Seal": "company_seal.png"
}

missing_images = []
for name, file in required_images.items():
    path = get_image_path(file)
    if path and os.path.exists(path):
        st.sidebar.success(f"✓ {name}: Found")
    else:
        st.sidebar.error(f"✗ {name}: Missing")
        missing_images.append(file)

if missing_images:
    st.sidebar.warning(f"Missing {len(missing_images)} image(s)")
    with st.sidebar.expander("View missing images"):
        for img in missing_images:
            st.write(f"- {img}")
else:
    st.sidebar.success("✓ All images found!")

# Document Information
col1, col2, col3 = st.columns(3)
with col1:
    doc_type = st.selectbox("Document Type", ["PROFORMA INVOICE", "QUOTATION"])
with col2:
    invoice_no = st.text_input("Invoice Number", "0120")
with col3:
    shipping_method = st.selectbox("Shipping Method", SHIPPING_METHODS, index=0)

# Seller Information
st.subheader("🧑‍💼 Seller Information")
seller_col1, seller_col2, seller_col3 = st.columns(3)
with seller_col1:
    seller_contact = st.selectbox(
        "Contact Person", 
        [p["name"] for p in SELLER_PROFILES],
        index=0
    )
with seller_col2:
    seller_email = st.text_input("Email", "imdadul@yhtransmissiontech.com")
with seller_col3:
    seller_phone = st.text_input("Phone", "+86-15895307823")

# Buyer Information
st.subheader("🏢 Buyer Information")
buyer_col1, buyer_col2 = st.columns(2)
with buyer_col1:
    buyer_company = st.text_input("Company", "springpro 1 llc")
    buyer_contact = st.text_input("Contact Person", "Tim Morgan")
with buyer_col2:
    buyer_tel = st.text_input("Tel", "+1-423 635-6930")
    buyer_address = st.text_area("Address", "94 enterprise drive Rossville, GA 30741, USA", height=80)

# Items Section
st.subheader("📦 Items")

# Buttons for adding/removing items
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("➕ Add Item"):
        add_item()
        st.rerun()

# Display items
for i, item in enumerate(st.session_state['invoice_items']):
    with st.expander(f"Item {i+1}", expanded=(i==0)):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            # Model selection
            new_model = st.selectbox(
                "Model", 
                MODEL_NUMBERS, 
                index=MODEL_NUMBERS.index(item['model']) if item['model'] in MODEL_NUMBERS else 0,
                key=f"model_{i}"
            )
            st.session_state['invoice_items'][i]['model'] = new_model
            
            # Check if auto image exists for this model
            if new_model in MODEL_IMAGE_MAP:
                image_file = get_image_for_model(new_model)
                if image_file:
                    st.session_state['invoice_items'][i]['image_type'] = 'auto'
                else:
                    st.session_state['invoice_items'][i]['image_type'] = None
            else:
                st.session_state['invoice_items'][i]['image_type'] = None
        
        with col2:
            new_qty = st.number_input(
                "Qty", 
                min_value=1, 
                value=item['qty'],
                key=f"qty_{i}"
            )
            st.session_state['invoice_items'][i]['qty'] = new_qty
        
        with col3:
            new_price = st.number_input(
                "Price ($)", 
                min_value=0.0, 
                value=item['price'],
                key=f"price_{i}"
            )
            st.session_state['invoice_items'][i]['price'] = new_price
        
        with col4:
            if len(st.session_state['invoice_items']) > 1:
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    remove_item(i)
                    st.rerun()
        
        # Specification
        new_spec = st.text_input(
            "Specification", 
            value=item['spec'],
            key=f"spec_{i}"
        )
        st.session_state['invoice_items'][i]['spec'] = new_spec
        
        # Image Upload Section
        st.markdown("**Image Options:**")
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            # Show auto image status
            if st.session_state['invoice_items'][i].get('image_type') == 'auto':
                image_file = get_image_for_model(new_model)
                if image_file:
                    try:
                        st.image(image_file, caption=f"Auto Image: {new_model}", width=150)
                    except:
                        st.warning(f"Auto image not found for {new_model}")
                else:
                    st.info(f"No auto image available for {new_model}")
            else:
                st.info("No auto image for this model")
        
        with col_img2:
            # Upload custom image
            uploaded_file = st.file_uploader(
                f"Upload custom image for Item {i+1}",
                type=['png', 'jpg', 'jpeg', 'gif'],
                key=f"upload_{i}"
            )
            if uploaded_file:
                # Display uploaded image
                st.image(uploaded_file, caption="Uploaded Image", width=150)
                # Store the uploaded file data
                st.session_state['invoice_items'][i]['image_data'] = uploaded_file
                st.session_state['invoice_items'][i]['image_type'] = 'uploaded'
                st.success("✓ Custom image uploaded")
            
            # Button to remove uploaded image
            if st.session_state['invoice_items'][i].get('image_type') == 'uploaded':
                if st.button("Remove Uploaded Image", key=f"remove_img_{i}"):
                    st.session_state['invoice_items'][i]['image_data'] = None
                    st.session_state['invoice_items'][i]['image_type'] = 'auto'
                    st.rerun()

# Shipping Details
st.subheader("🚚 Shipping & Delivery")
col1, col2, col3 = st.columns(3)
with col1:
    freight_charge = st.number_input("Freight Charge ($)", min_value=0.0, value=140.0)
with col2:
    lead_time = st.text_input("Lead Time", "7-8 days")
with col3:
    delivery_time = st.text_input("Delivery Time", "5-15 days")

package = st.selectbox("Package", ["Corrugated Box", "Wooden Box"])

# Generate PDF Button
if st.button("🚀 GENERATE PDF", type="primary", use_container_width=True):
    with st.spinner("Generating PDF with all images..."):
        # Prepare invoice data
        invoice_data = {
            'doc_type': doc_type,
            'invoice_no': invoice_no,
            'seller_contact': seller_contact,
            'seller_email': seller_email,
            'seller_phone': seller_phone,
            'buyer_company': buyer_company,
            'buyer_contact': buyer_contact,
            'buyer_tel': buyer_tel,
            'buyer_address': buyer_address,
            'items': st.session_state['invoice_items'],
            'shipping_method': shipping_method,
            'freight_charge': freight_charge,
            'lead_time': lead_time,
            'delivery_time': delivery_time,
            'package': package
        }
        
        try:
            # Create PDF
            pdf = create_pdf(invoice_data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                pdf.output(tmp.name)
                
                # Create download link
                with open(tmp.name, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # Show download button
                st.success("✅ PDF Generated Successfully!")
                
                doc_prefix = "PI" if doc_type == "PROFORMA INVOICE" else "QT"
                filename = f"{doc_prefix}_{invoice_no}_{buyer_contact.replace(' ', '_')}.pdf"
                
                # Show preview of included images
                with st.expander("📋 Included Images", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Show logo if exists
                    logo_path = get_image_path("company_logo.png")
                    if logo_path and os.path.exists(logo_path):
                        with col1:
                            st.image(logo_path, caption="Logo", width=100)
                    
                    # Show header if exists
                    header_path = get_image_path("Header.png")
                    if header_path and os.path.exists(header_path):
                        with col2:
                            st.image(header_path, caption="Header", width=100)
                    
                    # Show footer if exists
                    footer_path = get_image_path("Footer.png")
                    if footer_path and os.path.exists(footer_path):
                        with col3:
                            st.image(footer_path, caption="Footer", width=100)
                    
                    # Show seal if exists
                    seal_path = get_image_path("company_seal.png")
                    if seal_path and os.path.exists(seal_path):
                        with col4:
                            st.image(seal_path, caption="Seal", width=100)
                
                download_link = f'<a href="data:application/pdf;base64,{base64_pdf}" download="{filename}" style="background-color: #4CAF50; color: white; padding: 14px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; font-weight: bold; font-size: 16px;">📥 Download Complete PDF</a>'
                st.markdown(download_link, unsafe_allow_html=True)
                
                # Preview summary
                with st.expander("📊 PDF Details", expanded=False):
                    st.write(f"**Document:** {doc_type}")
                    st.write(f"**Number:** {invoice_no}")
                    st.write(f"**Total Items:** {len(st.session_state['invoice_items'])}")
                    st.write(f"**Shipping Method:** {shipping_method}")
                    st.write(f"**Freight Charge:** ${freight_charge}")
                    st.write(f"**Grand Total:** ${freight_charge + sum(item['qty'] * item['price'] for item in st.session_state['invoice_items']):.2f}")
                    
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.info("""
            **Troubleshooting Tips:**
            1. Make sure all image files are in the 'images' folder
            2. Check image file names match exactly
            3. Try generating without custom images first
            """)

# Sidebar with instructions
with st.sidebar:
    st.markdown("### 📋 Required Images")
    st.markdown("""
    For complete PDF, ensure these files are in `images/` folder:
    
    **Essential:**
    - `company_logo.png` (top left)
    - `Header.png` (top right)
    - `Footer.png` (bottom left)
    - `company_seal.png` (signature area)
    
    **Product Images (for auto mode):**
    - `1ch.png`, `2ch.png`, `4ch.png`
    - `520.png`, `521.png`, etc.
    - `psupply.png`, `vconverter.png`
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Tips")
    st.markdown("""
    1. Fill all required fields
    2. Add/remove items as needed
    3. Upload custom images if needed
    4. Check sidebar for missing images
    5. Click GENERATE PDF
    """)
    
    st.markdown("---")
    st.markdown("**Version:** 2.0 with All Images")
    st.markdown("**Status:** Online")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>YuHuang Invoice Generator v2.0 • Complete with Logo, Header, Footer & Seal</p>", unsafe_allow_html=True)