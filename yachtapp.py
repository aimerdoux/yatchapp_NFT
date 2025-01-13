import streamlit as st
import json
from web3 import Web3
from PIL import Image
import qrcode
import io
import uuid
from datetime import datetime
import requests
from eth_account import Account
import os

class WalletPassGenerator:
    def __init__(self):
        self.pass_template = {
            "formatVersion": 1,
            "passTypeIdentifier": "pass.com.web3yachts.ticket",
            "serialNumber": "",
            "teamIdentifier": "",  # Your Apple Developer Team ID
            "organizationName": "Web3 Yacht Events",
            "description": "Yacht Event Ticket",
            "logoText": "Web3 Yacht Events",
            "foregroundColor": "rgb(255, 255, 255)",
            "backgroundColor": "rgb(27, 58, 91)",
            "eventTicket": {
                "primaryFields": [],
                "secondaryFields": [],
                "auxiliaryFields": []
            }
        }

    def create_pass(self, ticket_data):
        pass_json = self.pass_template.copy()
        pass_json["serialNumber"] = str(uuid.uuid4())
        
        # Add ticket details
        pass_json["eventTicket"]["primaryFields"].append({
            "key": "event",
            "label": "EVENT",
            "value": ticket_data["event_name"]
        })
        
        pass_json["eventTicket"]["secondaryFields"].extend([
            {
                "key": "date",
                "label": "DATE",
                "value": ticket_data["date"]
            },
            {
                "key": "ticketId",
                "label": "TICKET",
                "value": f"#{ticket_data['ticket_id']}"
            }
        ])
        
        return pass_json

def setup_web3(rpc_url):
    """Initialize Web3 connection"""
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            raise Exception("Failed to connect to Ethereum network")
        return w3
    except Exception as e:
        st.error(f"Web3 connection error: {str(e)}")
        return None

def create_qr_code(ticket_data):
    """Generate QR code for ticket data"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(ticket_data))
    qr.make(fit=True)
    
    # Create image in memory
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def upload_to_ipfs(file_bytes):
    """Upload file to IPFS using Pinata or similar service"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.ipfs_api_key}"
        }
        
        files = {
            'file': file_bytes
        }
        
        response = requests.post(
            "https://api.pinata.cloud/pinning/pinFileToIPFS",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            ipfs_hash = response.json()["IpfsHash"]
            return f"ipfs://{ipfs_hash}"
        else:
            raise Exception(f"IPFS upload failed: {response.text}")
            
    except Exception as e:
        st.error(f"IPFS upload error: {str(e)}")
        return None

def mint_nft(image_bytes, metadata, contract_address, private_key, w3):
    """Mint NFT with ticket metadata"""
    try:
        # Load NFT contract ABI
        contract_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "string", "name": "uri", "type": "string"}
                ],
                "name": "mintNFT",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # Upload image to IPFS
        image_uri = upload_to_ipfs(image_bytes)
        if not image_uri:
            raise Exception("Failed to upload image to IPFS")
        
        # Update metadata with image URI
        metadata["image"] = image_uri
        metadata_uri = upload_to_ipfs(json.dumps(metadata).encode())
        if not metadata_uri:
            raise Exception("Failed to upload metadata to IPFS")
        
        # Get contract and account
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        account = Account.from_key(private_key)
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        
        transaction = contract.functions.mintNFT(
            account.address,
            metadata_uri
        ).build_transaction({
            'nonce': nonce,
            'gas': 500000,
            'gasPrice': gas_price
        })
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return w3.eth.wait_for_transaction_receipt(tx_hash)
        
    except Exception as e:
        st.error(f"NFT minting error: {str(e)}")
        return None

def main():
    st.title("Web3 Yacht Event Ticket Minting")
    
    # Configuration Section
    with st.expander("API Configuration"):
        # Initialize session state
        if 'rpc_url' not in st.session_state:
            st.session_state.rpc_url = ''
        if 'ipfs_api_key' not in st.session_state:
            st.session_state.ipfs_api_key = ''
            
        # API Configuration inputs
        rpc_url = st.text_input("Ethereum RPC URL", value=st.session_state.rpc_url)
        ipfs_api_key = st.text_input("IPFS API Key", value=st.session_state.ipfs_api_key, type="password")
        contract_address = st.text_input("NFT Contract Address")
        private_key = st.text_input("Private Key", type="password")
        
        # Update session state
        if rpc_url != st.session_state.rpc_url:
            st.session_state.rpc_url = rpc_url
        if ipfs_api_key != st.session_state.ipfs_api_key:
            st.session_state.ipfs_api_key = ipfs_api_key
    
    # Initialize Web3
    w3 = setup_web3(st.session_state.rpc_url)
    
    # Ticket Information
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
            if not w3:
                st.error("Please configure Web3 connection first")
                return
                
            try:
                # Create ticket data
                ticket_data = {
                    "event_name": event_name,
                    "date": str(event_date),
                    "ticket_id": str(uuid.uuid4())[:8]
                }
                
                # Generate QR code
                qr_image_bytes = create_qr_code(ticket_data)
                
                # Create wallet pass
                wallet_pass = WalletPassGenerator().create_pass(ticket_data)
                
                # Mint NFT
                tx_receipt = mint_nft(
                    uploaded_file.getvalue(),
                    metadata,
                    contract_address,
                    private_key,
                    w3
                )
                
                if tx_receipt:
                    st.success(f"NFT Ticket minted successfully! Transaction hash: {tx_receipt['transactionHash'].hex()}")
                    
                    # Download buttons
                    st.download_button(
                        label="Download Wallet Pass JSON",
                        data=json.dumps(wallet_pass, indent=2),
                        file_name="ticket.pass.json",
                        mime="application/json"
                    )
                    
                    st.download_button(
                        label="Download QR Code",
                        data=qr_image_bytes,
                        file_name="ticket_qr.png",
                        mime="image/png"
                    )
                    
            except Exception as e:
                st.error(f"Error processing ticket: {str(e)}")

if __name__ == "__main__":
    main()
