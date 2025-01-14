class Pass2UClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.pass2u.net/v2"
        
    def create_pass_template(self, event_data):
        """Create a pass template for the yacht event"""
        template_data = {
            "pass": {
                "passType": "eventTicket",
                "organizationName": "Web3 Yacht Events",
                "description": event_data["name"],
                "logoText": "Web3 Yacht Events",
                "backgroundColor": "rgb(40, 44, 52)",  # Dark background
                "foregroundColor": "rgb(255, 255, 255)",  # White text
                "labelColor": "rgb(255, 223, 0)",  # Gold accent color
                "relevantDate": event_data["date"],
                "barcode": {
                    "format": "PKBarcodeFormatQR",
                    "message": event_data["ticket_id"],
                    "messageEncoding": "iso-8859-1",
                    "altText": f"W3B {event_data['ticket_id']}"
                },
                "eventTicket": {
                    "headerFields": [
                        {
                            "key": "time",
                            "label": "",
                            "value": event_data["time"],
                            "textAlignment": "PKTextAlignmentRight"
                        }
                    ],
                    "primaryFields": [
                        {
                            "key": "yacht",
                            "label": "YACHT NAME",
                            "value": event_data["name"]
                        }
                    ],
                    "secondaryFields": [
                        {
                            "key": "showtime",
                            "label": "SHOWTIME",
                            "value": event_data["formatted_date"]
                        },
                        {
                            "key": "inclusive",
                            "label": "INCLUSIVE",
                            "value": "ALL"
                        }
                    ],
                    "auxiliaryFields": [
                        {
                            "key": "vip",
                            "label": "VIP",
                            "value": event_data["vip_status"]
                        },
                        {
                            "key": "guests",
                            "label": "GUEST",
                            "value": str(event_data["guest_count"])
                        }
                    ]
                },
                "images": {
                    "thumbnail": event_data["thumbnail_path"],
                    "background": event_data["background_path"]
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/passes",
            json=template_data,
            headers=headers
        )
        
        return response.json()

# Example usage:
event_data = {
    "name": "HAPPY ENDING",
    "date": "2025-03-21T08:30:00",
    "time": "7:40PM",
    "formatted_date": "3/21/25, 8:30AM",
    "ticket_id": "W3B332",
    "vip_status": "YES",
    "guest_count": 2,
    "thumbnail_path": "path/to/thumbnail.png",  # You'll need to upload this
    "background_path": "path/to/background.png"  # You'll need to upload this
}
