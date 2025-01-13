import streamlit as st
from PIL import Image
import qrcode
import json
from web3 import Web3
import io
import uuid
from pathlib import Path

def create_qr(data):
    """Generate QR code from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECTION_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def connect_to_web3(rpc_url):
    """Establish Web3 connection"""
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3 if w3.is_connected() else None
    except Exception:
        return None

def generate_ticket_json(event_data):
    """Generate ticket metadata"""
    return {
        "ticket_id": str(uuid.uuid4())[:8],
        "event_name": event_data["name"],
        "event_date": event_data["date"],
        "price": event_data["price"],
        "version": "1.0"
    }

def main():
    st.title("🛥️ Web3 Yacht Event Ticket Minter")
    
    # Sidebar for Web3 Configuration
    with st.sidebar:
        st.header("Network Configuration")
        network = st.selectbox(
            "Select Network",
            ["Ethereum Testnet", "Polygon Testnet", "Local Testnet"]
        )
        
        rpc_url = st.text_input(
            "RPC URL",
            type="password",
            help="Enter your Web3 RPC URL"
        )
        
        contract_addr = st.text_input(
            "Contract Address",
            help="Enter the NFT contract address"
        )

    # Main Content
    st.header("Event Details")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        event_name = st.text_input("Event Name", placeholder="Luxury Yacht Party")
        event_date = st.date_input("Event Date")
        
    with col2:
        ticket_price = st.number_input("Ticket Price (ETH)", min_value=0.0, value=0.1)
        max_supply = st.number_input("Maximum Tickets", min_value=1, value=100)

    # Image Upload Section
    st.header("Event Image")
    uploaded_file = st.file_uploader(
        "Upload Event Image", 
        type=["png", "jpg", "jpeg"],
        help="Upload the image to be used for the NFT ticket"
    )

    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview of NFT Ticket Image", use_column_width=True)
        
        # Prepare ticket data
        ticket_data = {
            "name": event_name,
            "date": str(event_date),
            "price": str(ticket_price)
        }
        
        # Generate ticket metadata
        ticket_metadata = generate_ticket_json(ticket_data)
        
        # Create preview section
        st.header("Ticket Preview")
        st.json(ticket_metadata)
        
        # Generate QR code
        qr_img = create_qr(json.dumps(ticket_metadata))
        qr_bytes = io.BytesIO()
        qr_img.save(qr_bytes, format='PNG')
        qr_bytes = qr_bytes.getvalue()
        
        st.image(qr_img, caption="Ticket QR Code", width=300)
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Download QR Code
            st.download_button(
                label="Download QR Code",
                data=qr_bytes,
                file_name=f"ticket_qr_{ticket_metadata['ticket_id']}.png",
                mime="image/png"
            )
            
        with col2:
            # Download Metadata
            st.download_button(
                label="Download Metadata",
                data=json.dumps(ticket_metadata, indent=2),
                file_name=f"ticket_metadata_{ticket_metadata['ticket_id']}.json",
                mime="application/json"
            )
        
        # Minting Section
        st.header("Mint NFT Ticket")
        if st.button("Mint Ticket NFT"):
            if not rpc_url or not contract_addr:
                st.error("Please configure network settings in the sidebar first!")
                return
                
            # Connect to Web3
            w3 = connect_to_web3(rpc_url)
            if not w3:
                st.error("Failed to connect to the network. Please check your RPC URL.")
                return
                
            st.info("Web3 connection established! Ready for minting...")
            # Note: Actual minting functionality would go here
            # This is a placeholder for demo purposes
            st.success(f"NFT Ticket #{ticket_metadata['ticket_id']} is ready for minting!")
            st.info("Please connect your wallet to complete the minting process.")

if __name__ == "__main__":
    main()
