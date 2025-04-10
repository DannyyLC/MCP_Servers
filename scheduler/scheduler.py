import os
import datetime as dt
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("scheduler")

# Constants
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate() -> Any:
    """
    Authenticates the user with Google Calendar API and returns the service object.
    
    Returns:
        service: Google Calendar API service object.
    """ 
    try:
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret_app_escritorio_oauth.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                
        return build("calendar", "v3", credentials=creds)
    except FileNotFoundError as e:
        print(f"❌ Archivo de credenciales no encontrado: {e}")
    except HttpError as e:
        print(f"❌ Error en la API de Google Calendar: {e}")
    except Exception as e:
        print(f"❌  Error inesperado en la autenticación: {e}")

@mcp.tool()
def create_event(summary: str, start_time: str, end_time: str, timezone: str, attendees: Optional[List[str]] = None) -> None:
    """
    Creates a Google Calendar event.
    
    Args:
        summary (str): Event title.
        start_time (str): Start time in ISO format.
        end_time (str): End time in ISO format.
        timezone (str): Time zone of the event.
        attendees (Optional[List[str]]): List of attendee email addresses.
    """
    try:
        service = authenticate()
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            }
        }
        
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
            
        event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")            
    except Exception as e:
        print(f"❌  Error inesperado en la creacion del evento: {e}")

@mcp.tool()
def update_event(event_id: str, summary: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
    """
    Updates an existing Google Calendar event.
    
    Args:
        event_id (str): ID of the event to update.
        summary (Optional[str]): New title.
        start_time (Optional[str]): New start time in ISO format.
        end_time (Optional[str]): New end time in ISO format.
    
    Returns:
        Dict[str, Any]: Updated event data.
    """
    try: 
        service = authenticate()
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        if summary:
            event['summary'] = summary
        if start_time:
            event['start']['dateTime'] = start_time
        if end_time:
            event['end']['dateTime'] = end_time
        updated_event = service.events().update(
            calendarId='primary', eventId=event_id, body=event).execute()
        return updated_event
    except HttpError as e:
        print(f"  ❌ Error en la API de Google Calendar: {e}")
    except Exception as e:
        print(f"  ❌  Error inesperado al actualizar el evento: {e}")

@mcp.tool()
def delete_event(event_id: str) -> bool:
    """
    Deletes an event from Google Calendar.
    
    Args:
        event_id (str): ID of the event to delete.
    
    Returns:
        bool: True if deletion was successful.
    """
    try:
        service = authenticate()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"❌  Error inesperado al eliminar el evento: {e}")
        return False

@mcp.tool()
def list_upcoming_events(max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Lists upcoming Google Calendar events.
    
    Args:
        max_results (int): Maximum number of events to retrieve.
    
    Returns:
        List[Dict[str, Any]]: List of upcoming events.
    """
    try:
        service = authenticate()
        now = dt.datetime.now().isoformat() + "Z"
        tomorrow = (dt.datetime.now() + dt.timedelta(days=5)).replace(hour=23, minute=59, second=0, microsecond=0).isoformat() + "Z"
        events_result = service.events().list(
            calendarId='primary', timeMin=now, timeMax=tomorrow,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print('No upcoming events found.')
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Convertir a objetos datetime (manejo de formato con y sin zona horaria)
                if 'T' in start:  # Formato con hora
                    start_dt = dt.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_start = start_dt.strftime("%d/%m/%Y %I:%M %p")
                else:  # Solo fecha
                    start_dt = dt.datetime.fromisoformat(start)
                    formatted_start = start_dt.strftime("%d/%m/%Y")
                    
                if 'T' in end:  # Formato con hora
                    end_dt = dt.datetime.fromisoformat(end.replace('Z', '+00:00'))
                    formatted_end = end_dt.strftime("%I:%M %p") if start_dt.date() == end_dt.date() else end_dt.strftime("%d/%m/%Y %I:%M %p")
                else:  # Solo fecha
                    end_dt = dt.datetime.fromisoformat(end)
                    formatted_end = end_dt.strftime("%d/%m/%Y")
                
                print(f"{formatted_start} - {formatted_end}: {event['summary']}")       
        return events
    
    except HttpError as error:
        print(f"❌ Error en la API de Google Calendar: {error}")
    except Exception as e:
        print(f"⚠️  Error inesperado al listar eventos: {e}")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
