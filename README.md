Bitespeed Pro - Contact Identification API


____Overview___
This is a Django-based backend service exposing an /identify endpoint to manage contacts by email and phone number. The service merges contacts when duplicates are detected.

____Features____
Accepts JSON POST requests at /identify
Identifies and merges primary and secondary contacts
Returns consolidated contact data
Lightweight Django app (no DRF)
Ready for deployment (tested on Render.com)

____Prerequisites____
Python 3.11+
pip
virtualenv (recommended)

____Deployment____
Hosted live at:
https://bitespeed-backend-1-2t9t.onrender.com

Test the live API:
curl -X POST https://bitespeed-backend-1-2t9t.onrender.com/identify \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "phoneNumber": "1234567890"}'



___Notes___
Use JSON payload, not form-data.
Make sure to add your deployed domain to ALLOWED_HOSTS in settings.py.
Frequent commits with meaningful messages in the GitHub repo.