import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Contact
from django.db.models import Q

@csrf_exempt
def identify(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        phone = data.get("phoneNumber")
        if not email and not phone:
            return JsonResponse({'error': 'email or phoneNumber is required'}, status=400)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Step 1: Find matching contacts
    contacts = Contact.objects.filter(
        Q(email=email) | Q(phoneNumber=phone)
    ).order_by("createdAt")

    # Step 2: Build contact graph
    if contacts.exists():
        # Get all related contacts
        related_contacts = set(contacts)
        checked = set(contacts)

        while checked:
            current = checked.pop()
            new_matches = Contact.objects.filter(
                Q(email=current.email) | Q(phoneNumber=current.phoneNumber)
            ).exclude(id__in=[c.id for c in related_contacts])
            related_contacts.update(new_matches)
            checked.update(new_matches)

        related_contacts = list(related_contacts)
        related_contacts.sort(key=lambda x: x.createdAt)
        primary_contact = next((c for c in related_contacts if c.linkPrecedence == "primary"), related_contacts[0])

        # Make sure there's only one primary
        for contact in related_contacts:
            if contact.id != primary_contact.id and contact.linkPrecedence == "primary":
                contact.linkPrecedence = "secondary"
                contact.linkedId = primary_contact.id
                contact.save()

        # Step 3: If current email/phone is new, add a secondary
        exists = any(c.email == email and c.phoneNumber == phone for c in related_contacts)
        if not exists:
            new_contact = Contact.objects.create(
                email=email,
                phoneNumber=phone,
                linkedId=primary_contact.id,
                linkPrecedence="secondary"
            )
            related_contacts.append(new_contact)

    else:
        # No match found — create new primary contact
        new_contact = Contact.objects.create(
            email=email,
            phoneNumber=phone,
            linkedId=None,
            linkPrecedence="primary"
        )
        primary_contact = new_contact
        related_contacts = [new_contact]

    # Step 4: Build response
    emails = []
    phones = []
    secondary_ids = []

    for c in related_contacts:
        if c.email and c.email not in emails:
            emails.append(c.email)
        if c.phoneNumber and c.phoneNumber not in phones:
            phones.append(c.phoneNumber)
        if c.linkPrecedence == "secondary":
            secondary_ids.append(c.id)

    return JsonResponse({
        "contact": {
            "primaryContatctId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    })
