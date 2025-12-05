import os
import json
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import GoogleCredentials

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Scopes we need: create/read events
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Path to client_secret.json (project root)
CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'client_secret.json')

@login_required
def google_authorize(request):
    # Start the OAuth flow
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri('/calendar/oauth2callback/')
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent' # ensures refresh token returned
    )
    # store state in session for callback verification
    request.session['oauth_state'] = state
    return redirect(authorization_url)

@login_required
def oauth2callback(request):
    state = request.session.get('oauth_state')
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri('/calendar/oauth2callback/')
)
    # fetch the token using the auth response URL
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

'token_uri': creds.token_uri,
'client_id': creds.client_id,
'client_secret': creds.client_secret,
'scopes': creds.scopes,
        # expiry is not JSON serializable directly, convert to isoformat
'expiry'creds = flow.credentials
# store credentials JSON in our model
creds_data = {
    'token': creds.token,
    'refresh_token': creds.refresh_token,
    : creds.expiry.isoformat() if creds.expiry else None
}

GoogleCredentials.objects.update_or_create(
    user=request.user,
    defaults={'credentials': creds_data}
)

return redirect('calendarapp:oauth_success')

@login_required
def oauth_success(request):
    return render(request, 'calendarapp/oauth_success.html')

def _load_credentials_for_user(user):
    try:
        gc = GoogleCredentials.objects.get(user=user)
    except GoogleCredentials.DoesNotExist:
        return None
    data = gc.credentials
    # convert expiry back to datetime if present
    creds = Credentials(
        token=data.get('token'),
        refresh_token=data.get('refresh_token'),
        token_uri=data.get('token_uri'),
        client_id=data.get('client_id'),
        client_secret=data.get('client_secret'),
        scopes=data.get('scopes')
    )
    # google oauthlib can auto-refresh if refresh_token is present and revoked token is used.
    return creds

@login_required
def create_event_view(request):
    """
    Simple view with a form to create an event and push it to Google Calendar.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        start = request.POST.get('start') # example format: 2025-12-05T14:00:00
        end = request.POST.get('end') # example format: 2025-12-05T15:00:00

        creds = _load_credentials_for_user(request.user)
        if not creds:
            return redirect('calendarapp:authorize')

    service = build('calendar', 'v3', credentials=creds)
    event_body = {
        'summary': title,
        'description': desc,
        'start': {'dateTime': start, 'timeZone': 'Africa/Johannesburg'},
        'end': {'dateTime': end, 'timeZone': 'Africa/Johannesburg'},
}

created_event = service.events().insert(calendarId='primary', body=event_body).execute()
return render(request, 'calendarapp/create_event.html', {
    'success': True,
    'event_link': created_event.get('htmlLink')
})

# GET
return render(request, 'calendarapp/create_event.html')