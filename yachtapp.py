import streamlit as st
import json
from web3 import Web3
from PIL import Image
import qrcode
from eth_account import Account
import secrets
from walletconnect_client import WalletConnect
import requests
from passkit.models import Pass, Barcode, BarcodeFormat
from datetime import datetime

def create_qr_code(ticket_data):
    """Generate QR code for ticket data"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(ticket_data))
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def create_wallet_pass(ticket_data, qr_image):
    """Create Apple Wallet pass"""
    passfile = Pass(
        pass_type_identifier='pass.com.yourdomain.yachtticket',
        organization_name='Web3 Yacht Events',
        team_identifier='YOUR_TEAM_ID',
        background_color='rgb(27, 58, 91)',
        barcode=Barcode(
            message=json.dumps(ticket_data),
            format=BarcodeFormat.QR
        )
    )
    
    # Add pass fields
    passfile.add_primary_field('event_name', ticket_data['event_name'])
    passfile.add_secondary_field('date', ticket_data['date'])
    passfile.add_auxiliary_field('ticket_number', f"#{ticket_data['ticket_id']}")
    
    return passfile

def mint_nft(image_path, metadata, contract_address, private_key):
    """Mint NFT with ticket metadata"""
    w3 = Web3(Web3.HTTPProvider(st.session_state.rpc_url))
    account = Account.from_key(private_key)
    
    # Load NFT contract ABI
    with open('nft_abi.json', 'r') as f:
        contract_abi = json.load(f)
    
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    # Upload image and metadata to IPFS
    ipfs_image = upload_to_ipfs(image_path)
    metadata['image'] = ipfs_image
    ipfs_metadata = upload_to_ipfs(json.dumps(metadata))
    
    # Mint NFT
    nonce = w3.eth.get_transaction_count(account.address)
    mint_txn = contract.functions.mintNFT(
        account.address,
        ipfs_metadata
    ).build_transaction({
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed_txn = w3.eth.account.sign_transaction(mint_txn, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)

def main():
    st.title("Web3 Yacht Event Ticket Minting")
    
    # API Configuration Section
    with st.expander("API Configuration"):
        if 'rpc_url' not in st.session_state:
            st.session_state.rpc_url = ''
            
        rpc_url = st.text_input("RPC URL", value=st.session_state.rpc_url)
        if rpc_url != st.session_state.rpc_url:
            st.session_state.rpc_url = rpc_url
            
        contract_address = st.text_input("NFT Contract Address")
        private_key = st.text_input("Private Key", type="password")
        
    # Ticket Information Section
    st.subheader("Ticket Information")
    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date")
    ticket_price = st.number_input("Ticket Price (ETH)", min_value=0.0)
    max_tickets = st.number_input("Maximum Tickets", min_value=1, value=100)
    
    # Image Upload
    st.subheader("Event Image")
    uploaded_file = st.file_uploader("Upload Event Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Event Image", use_column_width=True)
        
        # Generate ticket metadata
        metadata = {
            "name": f"{event_name} Ticket",
            "description": f"NFT Ticket for {event_name} on {event_date}",
            "attributes": [
                {"trait_type": "Event Date", "value": str(event_date)},
                {"trait_type": "Ticket Price", "value": str(ticket_price)},
                {"trait_type": "Maximum Supply", "value": str(max_tickets)}
            ]
        }
        
        if st.button("Mint NFT Ticket"):
            try:
                # Create QR code
                ticket_data = {
                    "event_name": event_name,
                    "date": str(event_date),
                    "ticket_id": secrets.token_hex(4)
                }
                qr_image = create_qr_code(ticket_data)
                
                # Create wallet pass
                wallet_pass = create_wallet_pass(ticket_data, qr_image)
                
                # Mint NFT
                tx_receipt = mint_nft(uploaded_file, metadata, contract_address, private_key)
                
                st.success(f"NFT Ticket minted successfully! Transaction hash: {tx_receipt.transactionHash.hex()}")
                
                # Download buttons
                st.download_button(
                    label="Download Wallet Pass",
                    data=wallet_pass.serialize(),
                    file_name="yacht_ticket.pkpass",
                    mime="application/vnd.apple.pkpass"
                )
                
                qr_image_bytes = qr_image.tobytes()
                st.download_button(
                    label="Download QR Code",
                    data=qr_image_bytes,
                    file_name="ticket_qr.png",
                    mime="image/png"
                )
                
            except Exception as e:
                st.error(f"Error minting NFT: {str(e)}")

if __name__ == "__main__":
    main()
