"""
Communications Manager - Contacts, voice dial, message dictation
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CommunicationsManager:
    """Manage communications features"""

    def __init__(self, data_dir='./communications'):
        """Initialize communications manager"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.contacts_file = self.data_dir / 'contacts.json'

        # Load contacts
        self.contacts = self._load_contacts()

        logger.info("Communications Manager initialized")

    def _load_contacts(self):
        """Load contacts from file"""
        try:
            if self.contacts_file.exists():
                with open(self.contacts_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading contacts: {e}")

        # Default empty contacts
        return {}

    def _save_contacts(self):
        """Save contacts to file"""
        try:
            with open(self.contacts_file, 'w') as f:
                json.dump(self.contacts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving contacts: {e}")

    def add_contact(self, name, phone_number, email=None):
        """Add a contact"""
        contact_key = name.lower()

        self.contacts[contact_key] = {
            'name': name,
            'phone': phone_number,
            'email': email
        }

        self._save_contacts()

        logger.info(f"Contact added: {name}")
        return f"Added contact: {name}, phone: {phone_number}"

    def get_contact(self, name):
        """Get contact information by name"""
        contact_key = name.lower()

        # Direct match
        if contact_key in self.contacts:
            contact = self.contacts[contact_key]
            result = f"{contact['name']}"

            if contact.get('phone'):
                result += f", phone: {contact['phone']}"
            if contact.get('email'):
                result += f", email: {contact['email']}"

            logger.info(f"Contact retrieved: {name}")
            return result

        # Partial match
        for key, contact in self.contacts.items():
            if contact_key in key or key in contact_key:
                result = f"Found: {contact['name']}"

                if contact.get('phone'):
                    result += f", phone: {contact['phone']}"
                if contact.get('email'):
                    result += f", email: {contact['email']}"

                return result

        return f"Contact not found: {name}"

    def list_contacts(self):
        """List all contacts"""
        if not self.contacts:
            return "No contacts saved. Add contacts with 'add contact' command."

        contact_list = f"You have {len(self.contacts)} contacts: "

        for contact in list(self.contacts.values())[:10]:  # Limit to first 10
            contact_list += f"{contact['name']}"
            if contact.get('phone'):
                contact_list += f" ({contact['phone']})"
            contact_list += ", "

        return contact_list.strip(', ')

    def delete_contact(self, name):
        """Delete a contact"""
        contact_key = name.lower()

        if contact_key in self.contacts:
            del self.contacts[contact_key]
            self._save_contacts()
            logger.info(f"Contact deleted: {name}")
            return f"Deleted contact: {name}"

        return f"Contact not found: {name}"

    def call_contact(self, name, bluetooth_manager=None):
        """Initiate a call to a contact"""
        contact_key = name.lower()

        # Find contact
        contact = None
        if contact_key in self.contacts:
            contact = self.contacts[contact_key]
        else:
            # Try partial match
            for key, c in self.contacts.items():
                if contact_key in key or key in contact_key:
                    contact = c
                    break

        if not contact:
            return f"Contact not found: {name}. Add contact first or say full phone number."

        phone = contact.get('phone')
        if not phone:
            return f"{contact['name']} has no phone number saved"

        # Note: Actual dialing would require Bluetooth HFP AT commands
        # This is a simplified version
        logger.info(f"Voice dial requested: {contact['name']} ({phone})")

        if bluetooth_manager:
            # In a real implementation, this would use Bluetooth HFP AT commands
            # to initiate a call. For now, we'll just log it.
            result = f"Calling {contact['name']} at {phone}. "
            result += "Note: Bluetooth voice dial requires HFP support on your phone."
            return result
        else:
            return f"Would call {contact['name']} at {phone}, but Bluetooth not available"

    def dictate_message(self, recipient, message_text):
        """Dictate a text message (stores locally, doesn't actually send)"""
        # Note: Sending SMS from Pi requires additional hardware or API services
        # This implementation stores the message draft locally

        contact_key = recipient.lower()

        # Find recipient
        recipient_name = recipient
        recipient_phone = None

        if contact_key in self.contacts:
            contact = self.contacts[contact_key]
            recipient_name = contact['name']
            recipient_phone = contact.get('phone')

        # Store message draft
        draft = {
            'to': recipient_name,
            'phone': recipient_phone,
            'message': message_text
        }

        drafts_file = self.data_dir / 'message_drafts.json'

        try:
            # Load existing drafts
            drafts = []
            if drafts_file.exists():
                with open(drafts_file, 'r') as f:
                    drafts = json.load(f)

            # Add new draft
            drafts.append(draft)

            # Save
            with open(drafts_file, 'w') as f:
                json.dump(drafts, f, indent=2)

            logger.info(f"Message draft saved: to {recipient_name}")

            result = f"Message to {recipient_name} saved: '{message_text}'. "
            result += "To actually send, sync with your phone's messaging app."

            return result

        except Exception as e:
            logger.error(f"Error saving message draft: {e}")
            return "Couldn't save message draft"

    def get_message_drafts(self):
        """Get saved message drafts"""
        drafts_file = self.data_dir / 'message_drafts.json'

        try:
            if not drafts_file.exists():
                return "No message drafts saved"

            with open(drafts_file, 'r') as f:
                drafts = json.load(f)

            if not drafts:
                return "No message drafts saved"

            result = f"You have {len(drafts)} message drafts: "

            for i, draft in enumerate(drafts[-5:], 1):  # Last 5
                result += f"{i}. To {draft['to']}: {draft['message'][:30]}... "

            return result.strip()

        except Exception as e:
            logger.error(f"Error reading drafts: {e}")
            return "Couldn't read message drafts"

    def clear_message_drafts(self):
        """Clear all message drafts"""
        drafts_file = self.data_dir / 'message_drafts.json'

        try:
            if drafts_file.exists():
                drafts_file.unlink()

            logger.info("Message drafts cleared")
            return "All message drafts cleared"

        except Exception as e:
            logger.error(f"Error clearing drafts: {e}")
            return "Couldn't clear drafts"

    def compose_email(self, recipient, subject, body):
        """Compose an email draft (stores locally)"""
        # Similar to messages, actual email sending requires SMTP setup
        # This stores email drafts locally

        email_drafts_file = self.data_dir / 'email_drafts.json'

        # Find recipient email if it's a contact name
        recipient_email = recipient
        if '@' not in recipient:
            # Look up in contacts
            contact_key = recipient.lower()
            if contact_key in self.contacts:
                contact = self.contacts[contact_key]
                recipient_email = contact.get('email', recipient)

        draft = {
            'to': recipient_email,
            'subject': subject,
            'body': body
        }

        try:
            # Load existing drafts
            drafts = []
            if email_drafts_file.exists():
                with open(email_drafts_file, 'r') as f:
                    drafts = json.load(f)

            # Add new draft
            drafts.append(draft)

            # Save
            with open(email_drafts_file, 'w') as f:
                json.dump(drafts, f, indent=2)

            logger.info(f"Email draft saved: to {recipient_email}")

            result = f"Email draft to {recipient_email} saved. "
            result += f"Subject: {subject}. "
            result += "To send, sync with your email client or set up SMTP."

            return result

        except Exception as e:
            logger.error(f"Error saving email draft: {e}")
            return "Couldn't save email draft"

    def get_email_drafts(self):
        """Get saved email drafts"""
        email_drafts_file = self.data_dir / 'email_drafts.json'

        try:
            if not email_drafts_file.exists():
                return "No email drafts saved"

            with open(email_drafts_file, 'r') as f:
                drafts = json.load(f)

            if not drafts:
                return "No email drafts saved"

            result = f"You have {len(drafts)} email drafts: "

            for i, draft in enumerate(drafts[-5:], 1):  # Last 5
                result += f"{i}. To {draft['to']}, Subject: {draft['subject']}. "

            return result.strip()

        except Exception as e:
            logger.error(f"Error reading email drafts: {e}")
            return "Couldn't read email drafts"
